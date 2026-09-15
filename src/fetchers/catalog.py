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
            # 7. Japan TIMSS Math
            self.japan_fetcher.get_timss_math(),
            # 8. Japan High School Informatics I
            self.japan_fetcher.get_high_school_informatics(),
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
        Alternates between math and info when topic is 'all'.
        """
        posted_history_ids = posted_history_ids or []
        all_ds = self.get_all_datasets()

        # Filter by category
        if topic in ("math", "算数", "数学"):
            candidates = [d for d in all_ds if d.category == "math"]
        elif topic in ("info", "情報", "プログラミング"):
            candidates = [d for d in all_ds if d.category == "info"]
        else:
            candidates = list(all_ds)

        if not candidates:
            logger.warning(f"No candidates for topic '{topic}'. Falling back to all datasets.")
            candidates = list(all_ds)

        if force:
            logger.info(f"Force mode active. Selecting first candidate: {candidates[0].id}")
            return candidates[0]

        # Helper: returns the MOST RECENT index of ds.id in posted_history_ids (-1 if never posted)
        def get_last_posted_index(ds: EducationDataset) -> int:
            for idx in range(len(posted_history_ids) - 1, -1, -1):
                if posted_history_ids[idx] == ds.id:
                    return idx
            return -1

        # Check for candidates not yet posted at all
        unposted = [d for d in candidates if get_last_posted_index(d) == -1]
        if unposted:
            # If topic == "all", try to alternate category based on last posted item
            if topic == "all" and posted_history_ids:
                last_posted_id = posted_history_ids[-1]
                last_ds = self.get_by_id(last_posted_id)
                target_cat = "info" if last_ds and last_ds.category == "math" else "math"
                matching_unposted = [d for d in unposted if d.category == target_cat]
                if matching_unposted:
                    logger.info(
                        f"Selecting unposted dataset in alternating category '{target_cat}': {matching_unposted[0].id}"
                    )
                    return matching_unposted[0]
            logger.info(f"Found {len(unposted)} unposted datasets. Selecting: {unposted[0].id}")
            return unposted[0]

        # If all candidate datasets have been posted at least once, rotate through least recently posted
        logger.info("All datasets have been posted at least once. Rotating through least recently posted.")

        # If topic is "all", alternate between math and info
        if topic == "all" and posted_history_ids:
            last_posted_id = posted_history_ids[-1]
            last_ds = self.get_by_id(last_posted_id)
            target_cat = "info" if last_ds and last_ds.category == "math" else "math"
            preferred = [d for d in candidates if d.category == target_cat]
            if preferred:
                preferred.sort(key=get_last_posted_index)
                logger.info(
                    f"Selected least recently posted dataset in category '{target_cat}': {preferred[0].id} "
                    f"(last posted index: {get_last_posted_index(preferred[0])})"
                )
                return preferred[0]

        # General rotation: pick candidate whose most recent post was the oldest (smallest index)
        candidates.sort(key=get_last_posted_index)
        logger.info(
            f"Selected least recently posted dataset: {candidates[0].id} "
            f"(last posted index: {get_last_posted_index(candidates[0])})"
        )
        return candidates[0]

