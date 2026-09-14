import json
import logging
from pathlib import Path
from typing import List, Optional
import pandas as pd
import requests

from src.config import CATALOG_DIR, Config
from src.fetchers.base import EducationDataset

logger = logging.getLogger(__name__)


class JapanEduDataFetcher:
    """
    Fetches Japanese domestic education statistics from MEXT, NIER, and e-Stat API.
    Loads curated datasets on National Assessment (Math), GIGA ICT informatization,
    and School Basic Survey (Informatics/STEM enrollment).
    """

    def __init__(self, catalog_dir: Optional[Path] = None):
        self.catalog_dir = catalog_dir or CATALOG_DIR

    def _load_json_dataset(self, filename: str) -> Optional[EducationDataset]:
        path = self.catalog_dir / filename
        if not path.exists():
            logger.warning(f"Catalog file not found: {path}")
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            df = pd.DataFrame(raw["data"])
            return EducationDataset(
                id=raw["id"],
                title=raw["title"],
                category=raw["category"],
                region=raw["region"],
                source_name=raw["source_name"],
                source_url=raw["source_url"],
                description=raw["description"],
                df=df,
                metrics=raw["metrics"],
                time_col=raw.get("time_col"),
                group_col=raw.get("group_col"),
                recommended_chart=raw.get("recommended_chart", "trend_line"),
                unit=raw.get("unit", "%"),
            )
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return None

    def get_national_assessment_math(self) -> EducationDataset:
        """Loads National Assessment of Academic Ability (Math) dataset."""
        ds = self._load_json_dataset("japan_national_assessment_math.json")
        if ds:
            return ds
        # Minimal emergency fallback
        df = pd.DataFrame([
            {"年度": 2021, "校種・教科": "小学校_算数", "平均正答率": 70.3, "端末活用率": 58.7},
            {"年度": 2022, "校種・教科": "小学校_算数", "平均正答率": 63.3, "端末活用率": 78.3},
            {"年度": 2023, "校種・教科": "小学校_算数", "平均正答率": 62.7, "端末活用率": 83.1},
            {"年度": 2024, "校種・教科": "小学校_算数", "平均正答率": 63.6, "端末活用率": 85.6},
            {"年度": 2021, "校種・教科": "中学校_数学", "平均正答率": 57.5, "端末活用率": 52.1},
            {"年度": 2022, "校種・教科": "中学校_数学", "平均正答率": 51.4, "端末活用率": 71.9},
            {"年度": 2023, "校種・教科": "中学校_数学", "平均正答率": 51.4, "端末活用率": 78.4},
            {"年度": 2024, "校種・教科": "中学校_数学", "平均正答率": 53.1, "端末活用率": 81.2},
        ])
        return EducationDataset(
            id="japan_national_assessment_math",
            title="【全国学力調査】算数・数学平均正答率推移",
            category="math",
            region="japan",
            source_name="文部科学省",
            source_url="https://www.nier.go.jp/",
            description="全国学力・学習状況調査の平均正答率推移。",
            df=df,
            metrics=["平均正答率", "端末活用率"],
            time_col="年度",
            group_col="校種・教科",
            recommended_chart="trend_line",
            unit="%",
        )

    def get_ict_informatization(self) -> EducationDataset:
        """Loads MEXT School ICT Informatization Survey dataset."""
        ds = self._load_json_dataset("japan_mext_ict_informatization.json")
        if ds:
            return ds
        df = pd.DataFrame([
            {"年度": 2020, "指標区分": "端末の日常的利用率(週3日以上)", "全国平均": 32.8},
            {"年度": 2021, "指標区分": "端末の日常的利用率(週3日以上)", "全国平均": 62.5},
            {"年度": 2022, "指標区分": "端末の日常的利用率(週3日以上)", "全国平均": 75.3},
            {"年度": 2023, "指標区分": "端末の日常的利用率(週3日以上)", "全国平均": 81.9},
            {"年度": 2024, "指標区分": "端末の日常的利用率(週3日以上)", "全国平均": 85.2},
        ])
        return EducationDataset(
            id="japan_mext_ict_informatization",
            title="【学校教育情報化実態調査】1人1台端末利活用率の推移",
            category="info",
            region="japan",
            source_name="文部科学省",
            source_url="https://www.mext.go.jp/",
            description="1人1台端末利活用頻度の推移。",
            df=df,
            metrics=["全国平均"],
            time_col="年度",
            group_col="指標区分",
            recommended_chart="trend_line",
            unit="%",
        )

    def get_stem_cs_enrollment(self) -> EducationDataset:
        """Loads School Basic Survey (Informatics/STEM Enrollment) dataset."""
        ds = self._load_json_dataset("japan_stem_cs_enrollment.json")
        if ds:
            return ds
        df = pd.DataFrame([
            {"年度": 2020, "分野": "情報科学・工学", "入学者総数": 34600, "女性比率": 17.3},
            {"年度": 2022, "分野": "情報科学・工学", "入学者総数": 38100, "女性比率": 19.0},
            {"年度": 2024, "分野": "情報科学・工学", "入学者総数": 42800, "女性比率": 21.2},
        ])
        return EducationDataset(
            id="japan_stem_cs_enrollment",
            title="【学校基本調査】情報系学科入学者数と女子比率の推移",
            category="info",
            region="japan",
            source_name="文部科学省",
            source_url="https://www.mext.go.jp/",
            description="大学情報系学科入学者数推移。",
            df=df,
            metrics=["入学者総数", "女性比率"],
            time_col="年度",
            group_col="分野",
            recommended_chart="trend_line",
            unit="人 / %",
        )

    def query_estat_api(self, stats_data_id: str) -> Optional[dict]:
        """Optional query to e-Stat API if appId is set."""
        if not Config.ESTAT_APP_ID:
            logger.info("ESTAT_APP_ID is not set. Skipping live e-Stat API query.")
            return None
        url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
        params = {"appId": Config.ESTAT_APP_ID, "statsDataId": stats_data_id}
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.warning(f"e-Stat API query failed: {e}")
        return None
