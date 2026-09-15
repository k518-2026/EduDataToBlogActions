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


def test_catalog_rotation_cycles_through_all():
    catalog = DatasetCatalog()
    all_ds = catalog.get_all_datasets()
    assert len(all_ds) >= 8

    # Simulate history where all datasets have been posted
    sim_history = [ds.id for ds in all_ds]
    # Now select the next one; it should NOT be the last one in sim_history
    next_ds = catalog.select_dataset(topic="all", posted_history_ids=sim_history)
    assert next_ds.id != sim_history[-1]

    # Verify that in a full cycle of len(all_ds) selections, every dataset is chosen
    selected_ids = []
    for _ in range(len(all_ds)):
        picked = catalog.select_dataset(topic="all", posted_history_ids=sim_history)
        selected_ids.append(picked.id)
        sim_history.append(picked.id)

    # Every dataset must appear in the cycle
    all_ids = {ds.id for ds in all_ds}
    assert set(selected_ids) == all_ids


def test_topic_alternation():
    catalog = DatasetCatalog()
    all_ds = catalog.get_all_datasets()
    sim_history = [ds.id for ds in all_ds]

    # Select 6 consecutive datasets and check that categories alternate
    last_cat = None
    for _ in range(6):
        ds = catalog.select_dataset(topic="all", posted_history_ids=sim_history)
        if last_cat is not None:
            assert ds.category != last_cat, f"Category did not alternate: {ds.category} == {last_cat}"
        last_cat = ds.category
        sim_history.append(ds.id)


def test_jst_date_utility():
    from src.utils_date import get_jst_now
    jst_now = get_jst_now()
    assert jst_now is not None
    assert jst_now.year >= 2026
    # String format checks
    iso_date = jst_now.strftime("%Y-%m-%d")
    assert len(iso_date) == 10

