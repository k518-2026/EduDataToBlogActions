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


def test_workload_catalog_is_reproducible_from_the_transcribed_table():
    from tools.build_workload_catalog import build

    assert build() == _saved("japan_teacher_workload_survey")


def test_workload_known_published_values():
    rows = {r["業務内容"]: r for r in _saved("japan_teacher_workload_survey")}
    # MEXT, Teacher Working Conditions Survey FY2022 (final), p.2 table (minutes per day, teachers)
    assert rows["授業（主担当）"]["平日・小学校・平成28年度"] == 4 * 60 + 6
    assert rows["授業（主担当）"]["平日・小学校・令和4年度"] == 4 * 60 + 13
    assert rows["部活動・クラブ活動"]["土日・中学校・平成28年度"] == 2 * 60 + 9
    assert rows["部活動・クラブ活動"]["土日・中学校・令和4年度"] == 60 + 29
    assert len(rows) == 25


def test_ict_catalog_is_reproducible_from_the_transcribed_charts():
    from tools.build_ict_catalog import build

    assert build() == _saved("japan_mext_ict_informatization")


def test_ict_known_published_values():
    rows = {r["調査年（3月1日現在）"]: r for r in _saved("japan_mext_ict_informatization")}
    # MEXT, Survey on the informatization of education in schools, FY2023 results (final), pp.4-8
    assert rows[2024]["学習者用コンピュータ台数"] == 11847856
    assert rows[2024]["児童生徒数"] == 11033041
    assert rows[2021]["児童生徒1人あたり学習者用コンピュータ台数"] == 0.7
    assert rows[2020]["インターネット接続率（1Gbps以上）"] == 15.0
    assert rows[2019]["インターネット接続率（1Gbps以上）"] is None  # not surveyed yet
    assert rows[2023]["学習者用デジタル教科書整備率"] == 87.9


def test_info_teachers_catalog_is_reproducible_and_matches_table_totals():
    from tools.build_info_teachers_catalog import build

    rows = build()
    assert rows == _saved("japan_high_school_informatics")
    assert len(rows) == 49
    # MEXT (Nov 2022) p.2-3: national totals (May 1, 2022)
    assert sum(r["臨時免許状"] for r in rows) == 236
    assert sum(r["免許外教科担任"] for r in rows) == 560
    assert sum(r["臨時免許状・免許外教科担任の計"] for r in rows) == 796
    by = {r["自治体"]: r for r in rows}
    assert (by["長野県"]["臨時免許状"], by["長野県"]["免許外教科担任"]) == (0, 76)
    assert (by["栃木県"]["臨時免許状"], by["栃木県"]["免許外教科担任"]) == (45, 23)


def test_tokkyu_catalog_is_reproducible_and_known_values():
    from tools.build_tokkyu_catalog import build

    rows = build()
    assert rows == _saved("japan_special_needs_education")
    by = {r["年度"]: r for r in rows}
    # MEXT, FY2022 survey on resource-room instruction, p.4
    assert by[1993]["全体の通級指導児童生徒数（総数）"] == 12259
    assert by[2022]["全体の通級指導児童生徒数（総数）"] == 198343
    assert by[2022]["全体の通級指導児童生徒数（総数）"] - by[2021]["全体の通級指導児童生徒数（総数）"] == 14464
    assert by[2018]["高等学校の通級指導児童生徒数"] == 508
    assert by[2017]["高等学校の通級指導児童生徒数"] is None


def test_talis_catalog_is_reproducible_and_matches_the_country_note():
    from tools.build_talis_catalog import build

    rows, average = build()
    assert rows == _saved("oecd_talis_teacher_survey")
    by = {r["国・地域"]: r for r in rows}
    # OECD, Results from TALIS 2024 country note for Japan: 17% used AI (OECD average 36%); Singapore 75%
    assert round(by["日本"]["AIを仕事で使った教員の割合"]) == 17
    assert round(by["シンガポール"]["AIを仕事で使った教員の割合"]) == 75
    assert round(average["AIを仕事で使った教員の割合"]) == 36
    assert "ベルギー" not in by and "ベルギー（フランドル語圏）" in by


def test_unesco_catalog_is_reproducible_from_the_saved_api_response():
    from tools.build_unesco_catalog import build

    rows = build()
    assert rows == _saved("unesco_world_ict_skills")
    assert len(rows) == 47
    by = {r["国・地域"]: r for r in rows}
    # UNESCO Institute for Statistics, SDG 4.4.1 (ICTSKILL*), 2021
    assert by["日本"]["プログラミングをした人の割合"] == 5.6
    assert by["日本"]["表計算ソフトで基本的な算術式を使った人の割合"] == 50.9
    assert by["日本"]["プレゼンテーション資料を作成した人の割合"] == 33.5
    assert by["日本"]["プログラミングをした女性の割合"] is None  # not published for Japan


def test_enrollment_catalog_is_reproducible_from_the_estat_tables():
    from tools.build_enrollment_catalog import build

    rows, _ = build()
    assert rows == _saved("japan_stem_cs_enrollment")
    by = {(r["年度"], r["学科"]): r for r in rows}
    # MEXT, School Basic Survey FY2025, table "関係学科別 大学入学状況" (women / all entrants)
    assert by[(2025, "工学・機械工学")]["入学者の女性比率（%）"] == 8.2
    assert by[(2025, "工学・電気通信工学")]["入学者の女性比率（%）"] == 12.2
    assert by[(2025, "理学・数学")]["入学者の女性比率（%）"] == 21.0
    assert len({r["学科"] for r in rows}) == 58


def test_national_assessment_catalog_is_reproducible_and_known_values():
    from tools.build_national_assessment_catalog import build

    rows = build()
    assert rows == _saved("japan_national_assessment_math")
    by = {r["年度"]: r for r in rows}
    # NIER / MEXT, results of the National Assessment (public schools, nationwide)
    assert by[2021]["小学校算数の平均正答率"] == 70.3
    assert by[2025]["小学校算数の平均正答率"] == 58.2
    assert by[2025]["中学校数学の平均正答率"] == 48.8
    assert 2020 not in by  # not conducted


def test_timss_attitudes_catalog_is_reproducible_and_known_values():
    from tools.build_timss_attitudes_catalog import build

    rows = build()
    assert rows == _saved("timss2023_student_attitudes")
    by = {r["国・地域"]: r for r in rows}
    # IEA, TIMSS 2023 International Results, Exhibits 6.2.2 / 6.2.3 / 1.1.1 / 1.2.1
    jp = by["日本"]
    assert jp["小4・とても好き(%)"] == 22.0
    assert jp["小4・好きでない(%)"] == 42.0
    assert jp["小4・平均得点"] == 591.0
    assert jp["中2・平均得点"] == 595.0
    assert jp["小4・とても価値ありと考える(%)"] if False else "小4・とても価値ありと考える(%)" not in jp  # value scale: grade 8 only
