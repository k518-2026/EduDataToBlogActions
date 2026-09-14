"""
Japanese Font Loader and Manager for ReportLab PDF Generation.
Cross-platform detection supporting Windows, Ubuntu (GitHub Actions), and fallback CID fonts.
Configured specifically for JSET academic papers requiring Mincho (body) and Gothic (headings/captions).
"""
import logging
import os
from typing import Optional, Tuple

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

# Cached registered font names: (mincho_font, gothic_font)
_REGISTERED_MINCHO: Optional[str] = None
_REGISTERED_GOTHIC: Optional[str] = None


def register_japanese_fonts() -> Tuple[str, str]:
    """
    Detects and registers available Japanese fonts in ReportLab.
    Returns (mincho_font_name, gothic_font_name).
    - mincho_font_name: Used for body text, abstract, and table cells (JSET: MS 明朝 8.5pt).
    - gothic_font_name: Used for titles, section headings, table/figure captions (JSET: MS ゴシック 8.5pt/16pt).
    """
    global _REGISTERED_MINCHO, _REGISTERED_GOTHIC
    if _REGISTERED_MINCHO and _REGISTERED_GOTHIC:
        return _REGISTERED_MINCHO, _REGISTERED_GOTHIC

    # 1. Candidate paths for Mincho (明朝体)
    mincho_candidates = [
        # Windows
        ("MSMincho", "C:/Windows/Fonts/msmincho.ttc", 0),
        ("YuMincho", "C:/Windows/Fonts/yumin.ttf", None),
        # Ubuntu / Debian
        ("IPAMincho", "/usr/share/fonts/opentype/ipafont-mincho/ipam.ttf", None),
        ("IPAMincho", "/usr/share/fonts/truetype/ipafont-mincho/ipam.ttf", None),
        ("NotoSerifCJK", "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", 0),
        ("NotoSerifCJK", "/usr/share/fonts/truetype/noto/NotoSerifCJK-Regular.ttc", 0),
    ]

    registered_mincho = None
    for font_id, path_str, subfont_idx in mincho_candidates:
        if os.path.exists(path_str):
            try:
                if subfont_idx is not None:
                    font = TTFont(font_id, path_str, subfontIndex=subfont_idx)
                else:
                    font = TTFont(font_id, path_str)
                pdfmetrics.registerFont(font)
                registered_mincho = font_id
                logger.info(f"Successfully registered Japanese Mincho font: {font_id} ({path_str})")
                break
            except Exception as e:
                logger.warning(f"Failed to register Mincho font {path_str}: {e}")

    # 2. Candidate paths for Gothic (ゴシック体)
    gothic_candidates = [
        # Windows
        ("MSGothic", "C:/Windows/Fonts/msgothic.ttc", 0),
        ("Meiryo", "C:/Windows/Fonts/meiryo.ttc", 0),
        ("YuGothic", "C:/Windows/Fonts/yugothr.ttc", 0),
        # Ubuntu / Debian
        ("IPAGothic", "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf", None),
        ("IPAGothic", "/usr/share/fonts/truetype/ipafont-gothic/ipag.ttf", None),
        ("NotoSansCJK", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 0),
        ("NotoSansCJK", "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 0),
        ("JapaneseGothic", "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", None),
    ]

    registered_gothic = None
    for font_id, path_str, subfont_idx in gothic_candidates:
        if os.path.exists(path_str):
            try:
                if subfont_idx is not None:
                    font = TTFont(font_id, path_str, subfontIndex=subfont_idx)
                else:
                    font = TTFont(font_id, path_str)
                pdfmetrics.registerFont(font)
                registered_gothic = font_id
                logger.info(f"Successfully registered Japanese Gothic font: {font_id} ({path_str})")
                break
            except Exception as e:
                logger.warning(f"Failed to register Gothic font {path_str}: {e}")

    # 3. Fallback to Adobe CID Japanese fonts if no TrueType was found
    if not registered_mincho:
        try:
            cid_mincho = "HeiseiMin-W3"
            pdfmetrics.registerFont(UnicodeCIDFont(cid_mincho))
            registered_mincho = cid_mincho
            logger.info("Registered Adobe CID Mincho font (HeiseiMin-W3) as fallback.")
        except Exception as e:
            logger.error(f"Failed to register CID Mincho font: {e}")
            registered_mincho = "Times-Roman"

    if not registered_gothic:
        try:
            cid_gothic = "HeiseiKakuGo-W5"
            pdfmetrics.registerFont(UnicodeCIDFont(cid_gothic))
            registered_gothic = cid_gothic
            logger.info("Registered Adobe CID Gothic font (HeiseiKakuGo-W5) as fallback.")
        except Exception as e:
            logger.error(f"Failed to register CID Gothic font: {e}")
            registered_gothic = "Helvetica-Bold"

    _REGISTERED_MINCHO = registered_mincho
    _REGISTERED_GOTHIC = registered_gothic
    return _REGISTERED_MINCHO, _REGISTERED_GOTHIC
