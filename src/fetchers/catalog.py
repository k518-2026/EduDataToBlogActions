import logging
from typing import Dict, List, Optional

from src.fetchers.base import EducationDataset
from src.fetchers.japan_edu_data import JapanEduDataFetcher
from src.fetchers.oecd_unesco_data import OECDUnescoFetcher
from src.fetchers.world_bank_data import WorldBankFetcher

logger = logging.getLogger(__name__)


class DatasetCatalog:
    """Registry and selector for all available education datasets."""

    def __init__(self):
        self.japan_fetcher = JapanEduDataFetcher()
        self.oecd_unesco_fetcher = OECDUnescoFetcher()
        self.world_bank_fetcher = WorldBankFetcher()

    def get_all_datasets(self) -> List[EducationDataset]:
        """Loads and returns all available datasets."""
        datasets = [
            # 1. Japan Math
            self.japan_fetcher.get_national_assessment_math(),
            # 2. Japan Info/ICT
            self.japan_fetcher.get_ict_informatization(),
            # 3. Global Math
            self.oecd_unesco_fetcher.get_pisa_math(),
            # 4. Global Info/Programming
            self.oecd_unesco_fetcher.get_unesco_ict_skills(),
            # 5. Japan STEM/CS Higher Ed
            self.japan_fetcher.get_stem_cs_enrollment(),
            # 6. Global Math vs Expenditure
            self.world_bank_fetcher.get_dataset(),
        ]
        return [ds for ds in datasets if ds is not None]

    def get_by_id(self, dataset_id: str) -> Optional[EducationDataset]:
        """Finds a dataset by its unique ID."""
        for ds in self.get_all_datasets():
            if ds.id == dataset_id:
                return ds
        return None

    def select_dataset(
        self,
        topic: str = "all",
        posted_history_ids: Optional[List[str]] = None,
        force: bool = False,
    ) -> EducationDataset:
        """
        Selects the most suitable dataset for today's post.
        Filters by topic ('math', 'info', or 'all') and rotates through unposted datasets.
        """
        posted_history_ids = posted_history_ids or []
        all_ds = self.get_all_datasets()

        # Filter by category
        if topic in ("math", "算数", "数学"):
            candidates = [d for d in all_ds if d.category == "math"]
        elif topic in ("info", "情報", "プログラミング"):
            candidates = [d for d in all_ds if d.category == "info"]
        else:
            candidates = all_ds

        if not candidates:
            logger.warning(f"No candidates for topic '{topic}'. Falling back to all datasets.")
            candidates = all_ds

        if force:
            logger.info(f"Force mode active. Selecting first candidate: {candidates[0].id}")
            return candidates[0]

        # Prioritize candidates not yet posted
        unposted = [d for d in candidates if d.id not in posted_history_ids]
        if unposted:
            logger.info(f"Found {len(unposted)} unposted datasets. Selecting: {unposted[0].id}")
            return unposted[0]

        # If all have been posted, cycle through: pick the one posted least recently
        logger.info("All datasets have been posted at least once. Cycling through historical order.")
        # Find position of each candidate in posted_history_ids (earlier index = older post)
        def get_last_posted_index(ds: EducationDataset) -> int:
            try:
                return posted_history_ids.index(ds.id)
            except ValueError:
                return -1

        candidates.sort(key=get_last_posted_index)
        return candidates[0]
