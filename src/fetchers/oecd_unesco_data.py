import json
import logging
from pathlib import Path
from typing import Optional
import pandas as pd

from src.config import CATALOG_DIR
from src.fetchers.base import EducationDataset

logger = logging.getLogger(__name__)


class OECDUnescoFetcher:
    """
    Fetches international educational statistics from OECD PISA and UNESCO UIS.
    Covers mathematics literacy, gender parity in STEM, and programming/ICT skills.
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
                recommended_chart=raw.get("recommended_chart", "ranking_bar"),
                unit=raw.get("unit", "%"),
            )
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return None

    def get_pisa_math(self) -> EducationDataset:
        """Loads OECD PISA Mathematics Literacy dataset."""
        ds = self._load_json_dataset("oecd_pisa_math_ict.json")
        if ds:
            return ds
        df = pd.DataFrame([
            {"調査年": 2022, "国・地域": "シンガポール", "数学得点": 575, "男女得点差": 10},
            {"調査年": 2022, "国・地域": "日本", "数学得点": 536, "男女得点差": 10},
            {"調査年": 2022, "国・地域": "韓国", "数学得点": 527, "男女得点差": 10},
            {"調査年": 2022, "国・地域": "エストニア", "数学得点": 510, "男女得点差": 4},
            {"調査年": 2022, "国・地域": "OECD平均", "数学得点": 472, "男女得点差": 9},
        ])
        return EducationDataset(
            id="oecd_pisa_math_ict",
            title="【OECD PISA】主要国の数学的リテラシー得点国際比較",
            category="math",
            region="global",
            source_name="OECD PISA Database",
            source_url="https://www.oecd.org/pisa/",
            description="PISAにおける主要国の数学的リテラシー得点比較データ。",
            df=df,
            metrics=["数学得点", "男女得点差"],
            time_col="調査年",
            group_col="国・地域",
            recommended_chart="ranking_bar",
            unit="Score (点)",
        )

    def get_unesco_ict_skills(self) -> EducationDataset:
        """Loads UNESCO/ITU Programming and ICT skills dataset."""
        ds = self._load_json_dataset("unesco_world_ict_skills.json")
        if ds:
            return ds
        df = pd.DataFrame([
            {"年": 2023, "国名": "フィンランド", "プログラミングスキル保有率": 28.4, "表計算高度利用率": 62.1},
            {"年": 2023, "国名": "エストニア", "プログラミングスキル保有率": 25.8, "表計算高度利用率": 58.4},
            {"年": 2023, "国名": "シンガポール", "プログラミングスキル保有率": 24.5, "表計算高度利用率": 57.1},
            {"年": 2023, "国名": "日本", "プログラミングスキル保有率": 14.6, "表計算高度利用率": 43.5},
            {"年": 2023, "国名": "OECD平均", "プログラミングスキル保有率": 17.5, "表計算高度利用率": 48.6},
        ])
        return EducationDataset(
            id="unesco_world_ict_skills",
            title="【UNESCO/ITU】若年層のプログラミング・デジタルスキル保有率国際比較",
            category="info",
            region="global",
            source_name="UNESCO UIS / ITU",
            source_url="http://data.uis.unesco.org/",
            description="若年層におけるプログラミングスキルの国際比較。",
            df=df,
            metrics=["プログラミングスキル保有率", "表計算高度利用率"],
            time_col="年",
            group_col="国名",
            recommended_chart="ranking_bar",
            unit="%",
        )

    def get_talis_teacher_survey(self) -> Optional[EducationDataset]:
        """Loads OECD TALIS Teacher Survey dataset."""
        return self._load_json_dataset("oecd_talis_teacher_survey.json")
