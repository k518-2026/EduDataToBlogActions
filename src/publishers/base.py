"""
Base publisher interface for sending reports to blogs.
"""
from abc import ABC, abstractmethod
import logging

from src.reporter import GeneratedReport

logger = logging.getLogger(__name__)


class BasePublisher(ABC):
    """Abstract base class for blog publishers."""

    @abstractmethod
    def publish(self, report: GeneratedReport) -> bool:
        """Publishes the given report to the target platform."""
        pass
