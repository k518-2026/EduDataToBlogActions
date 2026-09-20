"""
Open data fetcher base classes and models.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import pandas as pd


@dataclass
class EducationDataset:
    """Represents a standardized educational dataset for statistical analysis."""

    id: str
    title: str
    category: str  # 'math' (算数・数学) or 'info' (情報・プログラミング)
    region: str  # 'japan' or 'global'
    source_name: str
    source_url: str
    description: str
    df: pd.DataFrame
    metrics: List[str]
    time_col: Optional[str] = None
    group_col: Optional[str] = None
    recommended_chart: str = "trend_line"  # 'trend_line', 'ranking_bar', 'correlation_scatter'
    unit: str = "%"
    observation_unit: str = ""
    sample_population_note: str = ""
    sample_population_size: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def summary_info(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "region": self.region,
            "rows": len(self.df),
            "columns": list(self.df.columns),
            "metrics": self.metrics,
            "unit": self.unit,
        }
