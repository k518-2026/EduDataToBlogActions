"""
Japanese Font Loader and Manager for ReportLab PDF Generation.
Cross-platform detection supporting Windows, Ubuntu (GitHub Actions), and fallback CID fonts.
"""
import logging
import os
from pathlib import Path
from typing import Optional

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

# Cached registered font name
_REGISTERED_FONT_NAME: Optional[str] = None
_REGISTERED_BOLD_FONT_NAME: Optional[str] = None


def register_japanese_fonts() -> tuple[str, str]:
    """
    Detects and registers available Japanese fonts in ReportLab.
    Returns (regular_font_name, bold_font_name).
    """
    global _REGISTERED_FONT_NAME, _REGISTERED_BOLD_FONT_NAME
    if _REGISTERED_FONT_NAME and _REGISTERED_BOLD_FONT_NAME:
        return _REGISTERED_FONT_NAME, _REGISTERED_BOLD_FONT_NAME

    # 1. Candidate paths for Windows and Linux
    candidates = [
        # Windows Fonts
        ("Meiryo", "C:/Windows/Fonts/meiryo.ttc", 0),
        ("MSGothic", "C:/Windows/Fonts/msgothic.ttc", 0),
        ("YuMincho", "C:/Windows/Fonts/yumin.ttf", None),
        # Ubuntu / Debian Fonts (apt-get install -y fonts-ipafont-gothic / fonts-noto-cjk)
        ("IPAGothic", "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf", None),
        ("IPAGothic", "/usr/share/fonts/truetype/ipafont-gothic/ipag.ttf", None),
        ("NotoSansCJK", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 0),
        ("NotoSansCJK", "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 0),
        ("JapaneseGothic", "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", None),
    ]

    registered_regular = None
    for font_id, path_str, subfont_idx in candidates:
        if os.path.exists(path_str):
            try:
                if subfont_idx is not None:
                    font = TTFont(font_id, path_str, subfontIndex=subfont_idx)
                else:
                    font = TTFont(font_id, path_str)
                pdfmetrics.registerFont(font)
                registered_regular = font_id
                logger.info(f"Successfully registered Japanese TrueType font: {font_id} ({path_str})")
                break
            except Exception as e:
                logger.warning(f"Failed to register font {path_str}: {e}")

    # 2. Check for Meiryo Bold or fallback
    registered_bold = None
    if registered_regular == "Meiryo" and os.path.exists("C:/Windows/Fonts/meiryob.ttc"):
        try:
            pdfmetrics.registerFont(TTFont("MeiryoBold", "C:/Windows/Fonts/meiryob.ttc", subfontIndex=0))
            registered_bold = "MeiryoBold"
        except Exception:
            registered_bold = registered_regular

    # 3. Fallback to Adobe CID Japanese fonts if no TrueType was found
    if not registered_regular:
        try:
            cid_regular = "HeiseiMin-W3"
            cid_bold = "HeiseiKakuGo-W5"
            pdfmetrics.registerFont(UnicodeCIDFont(cid_regular))
            pdfmetrics.registerFont(UnicodeCIDFont(cid_bold))
            registered_regular = cid_regular
            registered_bold = cid_bold
            logger.info("Registered Adobe CID Japanese fonts (HeiseiMin-W3 / HeiseiKakuGo-W5) as fallback.")
        except Exception as e:
            logger.error(f"Failed to register CID fonts: {e}")
            registered_regular = "Helvetica"
            registered_bold = "Helvetica-Bold"

    if not registered_bold:
        registered_bold = registered_regular

    _REGISTERED_FONT_NAME = registered_regular
    _REGISTERED_BOLD_FONT_NAME = registered_bold
    return _REGISTERED_FONT_NAME, _REGISTERED_BOLD_FONT_NAME
