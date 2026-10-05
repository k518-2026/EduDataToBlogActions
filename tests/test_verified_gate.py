"""Only data that was checked against its published source may be used."""
import json
from pathlib import Path

import pytest

from src.config import CATALOG_DIR
from src.fetchers.catalog import DataNotVerifiedError, DatasetCatalog, verification_status

pytestmark = pytest.mark.verified_gate


def _verified_ids():
    return {p.stem for p in Path(CATALOG_DIR).glob("*.json")
            if json.loads(p.read_text(encoding="utf-8")).get("verification", {}).get("status") == "verified"}


def test_only_verified_datasets_are_offered():
    ids = {d.id for d in DatasetCatalog().get_all_datasets()}
    assert ids == _verified_ids()
    assert ids  # every catalog file is verified now
    assert {"japan_school_absenteeism_bullying", "worldbank_education_indicators"} <= ids


def test_unverified_dataset_cannot_be_requested(monkeypatch):
    # All 12 catalog files are verified now; mark one as unverified to check that it cannot be requested.
    real = verification_status
    monkeypatch.setattr("src.fetchers.catalog.verification_status",
                        lambda i: "unverified" if i == "japan_national_assessment_math" else real(i))
    with pytest.raises(DataNotVerifiedError):
        DatasetCatalog().select_dataset_and_angle(dataset_id="japan_national_assessment_math")


def test_nothing_verified_means_an_error(monkeypatch):
    monkeypatch.setattr("src.fetchers.catalog.verification_status", lambda _id: "unverified")
    with pytest.raises(DataNotVerifiedError):
        DatasetCatalog().select_dataset(topic="all")


def test_missing_verification_field_is_unverified():
    assert verification_status("no_such_dataset") == "unverified"


def test_unverified_data_is_not_used_in_a_normal_run():
    # Every catalog entry that is not 'verified' stays out of rotation.
    ids = {d.id for d in DatasetCatalog().get_all_datasets()}
    for p in Path(CATALOG_DIR).glob("*.json"):
        status = json.loads(p.read_text(encoding="utf-8")).get("verification", {}).get("status")
        if status != "verified":
            assert p.stem not in ids
