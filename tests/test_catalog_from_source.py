"""The PISA and TIMSS catalog files must be exactly what the published workbooks in data/source/ give."""
import json

from src.config import CATALOG_DIR
from tools.build_pisa_timss_catalog import build_pisa, build_timss


def _saved(name):
    return json.loads((CATALOG_DIR / f"{name}.json").read_text(encoding="utf-8"))["data"]


def test_pisa_catalog_is_reproducible_from_the_oecd_workbooks():
    _head, rows = build_pisa()
    assert rows == _saved("oecd_pisa_math_ict")
    assert len(rows) == 32


def test_timss_catalog_is_reproducible_from_the_iea_workbooks():
    _head, rows = build_timss()
    assert rows == _saved("japan_timss_math_science")
    assert len(rows) == 14


def test_known_published_values():
    pisa = {(r["調査年"], r["国・地域"]): r for r in _saved("oecd_pisa_math_ict")}
    # OECD, PISA 2025 Results (Volume I), Table I.B1.2a.38 / I.B1.2c.29-31
    assert pisa[(2022, "日本")]["数学得点"] == 535.6
    assert pisa[(2025, "日本")]["数学得点"] == 525.4
    timss = {(r["調査年"], r["学年・教科"]): r for r in _saved("japan_timss_math_science")}
    # IEA, TIMSS 2023 International Results, Exhibit 1.1.10 / 1.2.10
    assert timss[(2023, "小学校4年_算数")]["平均得点"] == 591
    assert timss[(1995, "小学校4年_算数")]["平均得点"] == 567
