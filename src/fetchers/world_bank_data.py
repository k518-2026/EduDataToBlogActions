import json
import logging
from pathlib import Path
from typing import Optional
import pandas as pd
import requests

from src.config import CATALOG_DIR
from src.fetchers.base import EducationDataset

logger = logging.getLogger(__name__)


class WorldBankFetcher:
    """
    Fetches international educational statistics from the World Bank Open Data API.
    Provides robust fallback to local cached dataset if offline or rate-limited.
    """

    INDICATORS = {
        "learning_outcomes": "HD.HCI.HLOS",  # Harmonized Learning Outcomes (HLO) score
        "internet_users": "IT.NET.USER.ZS",  # Internet users % of population
        "education_expenditure": "SE.XPD.TOTL.GD.ZS",  # Public edu expenditure % GDP
    }

    def __init__(self, cache_file: Optional[Path] = None):
        self.cache_file = cache_file or (CATALOG_DIR / "worldbank_education_indicators.json")

    def fetch_live_indicator(self, indicator: str, date_range: str = "2018:2023") -> Optional[pd.DataFrame]:
        """Queries the official World Bank API for a given indicator."""
        url = f"http://api.worldbank.org/v2/country/all/indicator/{indicator}"
        params = {
            "format": "json",
            "date": date_range,
            "per_page": 500,
        }
        try:
            logger.info(f"Querying World Bank API: {url} (indicator: {indicator})")
            resp = requests.get(url, params=params, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) > 1 and isinstance(data[1], list):
                    records = []
                    for item in data[1]:
                        country = item.get("country", {}).get("value")
                        val = item.get("value")
                        date = item.get("date")
                        if val is not None and country:
                            records.append({"国名": country, "年": int(date), indicator: float(val)})
                    if records:
                        return pd.DataFrame(records)
        except Exception as e:
            logger.warning(f"Failed to fetch live World Bank data ({indicator}): {e}")
        return None

    def get_dataset(self) -> EducationDataset:
        """
        Loads the World Bank Education Indicators dataset.
        Uses cached/curated master dataset as default reliable source.
        """
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
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
                    recommended_chart=raw.get("recommended_chart", "correlation_scatter"),
                    unit=raw.get("unit", "%"),
                    observation_unit=raw.get("observation_unit", ""),
                    sample_population_note=raw.get("sample_population_note", ""),
                    sample_population_size=raw.get("sample_population_size", ""),
                )
            except Exception as e:
                logger.error(f"Error loading World Bank cached dataset: {e}")

        raise FileNotFoundError(f"World Bank のカタログが読み込めません: {self.cache_file}（代わりの数値は使いません）")
