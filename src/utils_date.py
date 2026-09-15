"""
Date and Time utilities for EduDataToBlogActions.
Ensures consistent Japan Standard Time (JST, UTC+9) handling across platforms.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")


def get_jst_now() -> datetime:
    """
    Returns the current datetime in Japan Standard Time (JST, UTC+9).
    Falls back gracefully to system local datetime if zoneinfo database is missing.
    """
    try:
        return datetime.now(JST)
    except Exception:
        return datetime.now()
