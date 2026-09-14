import pytest

from src.fetchers.catalog import DatasetCatalog
from src.fetchers.japan_edu_data import JapanEduDataFetcher
from src.fetchers.oecd_unesco_data import OECDUnescoFetcher
from src.fetchers.world_bank_data import WorldBankFetcher


def test_japan_fetcher():
    fetcher = JapanEduDataFetcher()
    math_ds = fetcher.get_national_assessment_math()
    assert math_ds.id == "japan_national_assessment_math"
    assert len(math_ds.df) > 0
    assert "平均正答率" in math_ds.metrics

    ict_ds = fetcher.get_ict_informatization()
    assert ict_ds.id == "japan_mext_ict_informatization"
    assert len(ict_ds.df) > 0

    stem_ds = fetcher.get_stem_cs_enrollment()
    assert stem_ds.id == "japan_stem_cs_enrollment"
    assert len(stem_ds.df) > 0


def test_oecd_unesco_fetcher():
    fetcher = OECDUnescoFetcher()
    pisa_ds = fetcher.get_pisa_math()
    assert pisa_ds.id == "oecd_pisa_math_ict"
    assert len(pisa_ds.df) > 0

    unesco_ds = fetcher.get_unesco_ict_skills()
    assert unesco_ds.id == "unesco_world_ict_skills"
    assert len(unesco_ds.df) > 0


def test_world_bank_fetcher():
    fetcher = WorldBankFetcher()
    wb_ds = fetcher.get_dataset()
    assert wb_ds.id == "worldbank_education_indicators"
    assert len(wb_ds.df) > 0


def test_catalog_selection():
    catalog = DatasetCatalog()
    all_ds = catalog.get_all_datasets()
    assert len(all_ds) >= 5

    # Filter math
    math_ds = catalog.select_dataset(topic="math", force=True)
    assert math_ds.category == "math"

    # Filter info
    info_ds = catalog.select_dataset(topic="info", force=True)
    assert info_ds.category == "info"

    # Rotation test
    first_ds = catalog.select_dataset(topic="all", posted_history_ids=[])
    second_ds = catalog.select_dataset(topic="all", posted_history_ids=[first_ds.id])
    assert first_ds.id != second_ds.id
