"""
Academic Paper PDF Generation Engine adhering to the Japan Society for Educational
Technology (JSET: 日本教育工学会論文誌) official template guidelines (2023-09-07).
Features:
- JIS B5 page size (182mm x 257mm)
- 2-column layout (2段組: 204pt per column, 17.25pt gutter) with 1-column title/abstract block
- Strict JSET typography (MS Mincho 8.5pt body, MS Gothic 8.5pt bold headings, 16pt title)
- JSET-standard three-line table (三本線表) with caption ABOVE the table
- Chart figure with caption BELOW the figure
- Official running headers and footers (alternating odd/even page headers/footers)
- English summary block at the end (Summary, KEYWORDS in uppercase)
- First-page English metadata callout box
"""
from datetime import datetime
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from unicodedata import category

from src.utils import (
    clean_english_text,
    clean_text_spaces,
    format_bayes_factor,
    format_bayes_factor_short_interpretation,
    format_title_two_lines,
    get_jst_now,
    resolve_metric_unit,
)

from PIL import Image as PILImage
from reportlab.lib import colors
import reportlab.lib.textsplit as rlp_ts
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    FrameBreak,
    Image,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
import reportlab.platypus.paragraph as rlp_para
from reportlab.platypus.paragraph import (
    cjkU,
    isBytes,
    _FUZZ,
    makeCJKParaLine,
    ParaLines,
)

from src.academic_paper import AcademicPaper, sort_jset_references
from src.analyzer import AnalysisResult
from src.fetchers.base import EducationDataset
from src.pdf.font_loader import register_japanese_fonts

logger = logging.getLogger(__name__)

# ==========================================
# Strict Japanese Typography (JIS X 4051 行頭・行末禁則処理)
# ==========================================
_EXTRA_CANNOT_START = "，．％%）)]｝}」』〉》〕〜ー!?！？:：;；"
for ch in _EXTRA_CANNOT_START:
    if ch not in rlp_para.ALL_CANNOT_START:
        rlp_para.ALL_CANNOT_START += ch
    if ch not in rlp_ts.ALL_CANNOT_START:
        rlp_ts.ALL_CANNOT_START += ch

_ALL_CANNOT_END = "（([｛{〔「『【"


def _jset_cjkFragSplit(frags, maxWidths, calcBounds, encoding="utf8"):
    """Enhanced CJK text splitting with strict Japanese typography (JIS X 4051 行頭・行末禁則処理)."""
    U = []
    for f in frags:
        text = f.text
        if isBytes(text):
            text = text.decode(encoding)
        if text:
            U.extend([cjkU(t, f, encoding) for t in text])
        else:
            U.append(cjkU(text, f, encoding))
    lines = []
    i = widthUsed = lineStartPos = 0
    maxWidth = maxWidths[0]
    nU = len(U)
    while i < nU:
        u = U[i]
        i += 1
        w = u.width
        if hasattr(w, "normalizedValue"):
            w._normalizer = maxWidth
            w = w.normalizedValue(maxWidth)
        widthUsed += w
        lineBreak = hasattr(u.frag, "lineBreak")
        endLine = (widthUsed > maxWidth + _FUZZ and widthUsed > 0) or lineBreak
        if endLine:
            extraSpace = maxWidth - widthUsed
            if not lineBreak:
                if ord(u) < 0x3000:
                    limitCheck = (lineStartPos + i) >> 1
                    for j in range(i - 1, limitCheck, -1):
                        uj = U[j]
                        if uj and category(uj) == "Zs" or ord(uj) >= 0x3000:
                            k = j + 1
                            if k < i:
                                j = k + 1
                                extraSpace += sum(U[ii].width for ii in range(j, i))
                                w = U[k].width
                                u = U[k]
                                i = j
                                break

                # Rule 1: character u cannot start line, keep on current line unless progress blocked
                if u not in rlp_para.ALL_CANNOT_START and i > lineStartPos + 1:
                    i -= 1
                    extraSpace += w

                # Rule 2: next line (starting at U[i]) must never start with a character in ALL_CANNOT_START
                while i > lineStartPos + 1 and i < nU and U[i] in rlp_para.ALL_CANNOT_START:
                    i -= 1
                    extraSpace += U[i].width

                # Rule 3: current line (ending at U[i-1]) must never end with a character in _ALL_CANNOT_END
                while i > lineStartPos + 1 and U[i - 1] in _ALL_CANNOT_END:
                    i -= 1
                    extraSpace += U[i].width

            lines.append(makeCJKParaLine(U[lineStartPos:i], maxWidth, widthUsed, extraSpace, lineBreak, calcBounds))
            try:
                maxWidth = maxWidths[len(lines)]
            except IndexError:
                maxWidth = maxWidths[-1]

            lineStartPos = i
            widthUsed = 0

    if widthUsed > 0:
        lines.append(makeCJKParaLine(U[lineStartPos:], maxWidth, widthUsed, maxWidth - widthUsed, False, calcBounds))

    return ParaLines(kind=1, lines=lines)


# Patch ReportLab paragraph module for bulletproof CJK typography
rlp_para.cjkFragSplit = _jset_cjkFragSplit

# Official JSET Page Size: JIS B5 (182mm x 257mm)
JIS_B5 = (182 * mm, 257 * mm)
PAGE_WIDTH, PAGE_HEIGHT = JIS_B5

# Official Margins & Grid Setup
MARGIN_X = 16.0 * mm        # 45.35 pt (left & right margins)
MARGIN_TOP = 24.5 * mm      # 69.45 pt (top margin)
MARGIN_BOTTOM = 22.5 * mm   # 63.8 pt (bottom margin)
GUTTER = 6.08 * mm          # 17.25 pt (space between columns)

PRINTABLE_W = PAGE_WIDTH - 2 * MARGIN_X      # 425.20 pt
PRINTABLE_H = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM  # 595.25 pt
COL_W = (PRINTABLE_W - GUTTER) / 2          # 203.98 pt

# Page 1 Box Heights
TOP_FRAME_H = 220.0   # Full-width area for Title, Authors, Abstract, Keywords
BOX_H = 75.0          # English metadata box in bottom-left corner of Page 1


class JSETNumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas implementing official JSET headers, footers, and page 1 metadata box.
    """
    current_paper: Optional[AcademicPaper] = None
    current_dataset: Optional[EducationDataset] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.mincho_font, self.gothic_font = register_japanese_fonts()

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_jset_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_jset_decorations(self, total_pages: int):
        self.saveState()
        p = self._pageNumber
        paper = self.current_paper
        dataset = self.current_dataset

        if p == 1:
            # 1. Top-Left Category Box (論文種別枠)
            self.setLineWidth(0.6)
            self.setStrokeColor(colors.black)
            self.rect(MARGIN_X, PAGE_HEIGHT - MARGIN_TOP + 4, 84, 16)
            self.setFont(self.gothic_font, 8.5)
            self.drawCentredString(MARGIN_X + 42, PAGE_HEIGHT - MARGIN_TOP + 8.5, "生成AI論文")

            # 2. Top-Right: 学会名・雑誌名は掲載しない（体裁・レイアウトのみ利用）

            # 3. Bottom-Left English Metadata Box
            self.rect(MARGIN_X, MARGIN_BOTTOM, COL_W, BOX_H)
            self.setFont(self.mincho_font, 7.0)
            today_date = get_jst_now().strftime("%Y年%m月%d日執筆")
            self.drawString(MARGIN_X + 5, MARGIN_BOTTOM + BOX_H - 11, today_date)

            self.setFont(self.mincho_font, 6.5)
            authors_str = paper.authors_en if paper and paper.authors_en else "EduData Research Group*1, Educational Data Science Team*2"
            title_str = paper.title_en if paper and paper.title_en else (dataset.title if dataset else "Empirical Educational Data Analysis")
            if len(title_str) > 42:
                title_str = title_str[:40] + "…"

            self.drawString(MARGIN_X + 5, MARGIN_BOTTOM + BOX_H - 22, f"†{authors_str[:44]}")
            self.drawString(MARGIN_X + 5, MARGIN_BOTTOM + BOX_H - 32, f"  : {title_str}")
            self.drawString(MARGIN_X + 5, MARGIN_BOTTOM + BOX_H - 43, "*1 Open Education Data Project, Tokyo, Japan")
            self.drawString(MARGIN_X + 5, MARGIN_BOTTOM + BOX_H - 53, "*2 Educational Data Science Unit, Tokyo, Japan")

            # 4. Page 1 Footer (Page number on outer margin)
            self.setFont(self.mincho_font, 8.5)
            self.drawRightString(PAGE_WIDTH - MARGIN_X, MARGIN_BOTTOM - 16, "1")

        else:
            # Later Pages Footers (alternating even/odd: page numbers on outer margin)
            self.setFont(self.mincho_font, 8.5)
            if p % 2 == 0:
                # Even page footer: [PageNum] on outer left
                self.drawString(MARGIN_X, MARGIN_BOTTOM - 16, f"{p}")
            else:
                # Odd page footer: [PageNum] on outer right
                self.drawRightString(PAGE_WIDTH - MARGIN_X, MARGIN_BOTTOM - 16, f"{p}")

        self.restoreState()


# Backwards compatibility alias
AcademicNumberedCanvas = JSETNumberedCanvas


class EduPaperPdfGenerator:
    """Compiles an AcademicPaper into a print-ready JSET-compliant academic paper PDF."""

    def __init__(self):
        self.mincho_font, self.gothic_font = register_japanese_fonts()
        self.styles = self._setup_styles()

    def _setup_styles(self) -> dict:
        sheet = getSampleStyleSheet()
        styles = {}

        # Title Block Styles
        styles["PaperTitle"] = ParagraphStyle(
            "PaperTitle",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=15.0,
            leading=19.0,
            alignment=1,  # Centered
            spaceAfter=4,
            wordWrap="CJK",
        )

        styles["PaperSubtitle"] = ParagraphStyle(
            "PaperSubtitle",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=10.0,
            leading=13.0,
            alignment=1,  # Centered
            spaceAfter=6,
            wordWrap="CJK",
        )

        styles["AuthorMeta"] = ParagraphStyle(
            "AuthorMeta",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=9.5,
            leading=13.0,
            alignment=1,  # Centered
            spaceAfter=2,
            wordWrap="CJK",
        )

        styles["AffiliationMeta"] = ParagraphStyle(
            "AffiliationMeta",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=12.0,
            alignment=1,  # Centered
            spaceAfter=8,
            wordWrap="CJK",
        )

        styles["Abstract"] = ParagraphStyle(
            "Abstract",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=12.5,
            firstLineIndent=8.5,  # 1 full-width character indent
            spaceAfter=4,
            wordWrap="CJK",
        )

        styles["Keywords"] = ParagraphStyle(
            "Keywords",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=12.5,
            spaceAfter=6,
            wordWrap="CJK",
        )

        # Section Headings (MS Gothic 8.5pt bold)
        styles["Heading1"] = ParagraphStyle(
            "Heading1",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=8.5,
            leading=12.5,
            spaceBefore=7,
            spaceAfter=2,
            keepWithNext=False,
            wordWrap="CJK",
        )

        styles["Heading2"] = ParagraphStyle(
            "Heading2",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=8.5,
            leading=12.5,
            spaceBefore=5,
            spaceAfter=2,
            keepWithNext=False,
            wordWrap="CJK",
        )

        styles["Heading3"] = ParagraphStyle(
            "Heading3",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=8.5,
            leading=12.5,
            spaceBefore=4,
            spaceAfter=2,
            keepWithNext=False,
            wordWrap="CJK",
        )

        # Body Text (MS Mincho 8.5pt, 1-char indent, leading 12.5pt)
        styles["Body"] = ParagraphStyle(
            "Body",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=12.5,
            firstLineIndent=8.5,
            spaceAfter=2,
            wordWrap="CJK",
        )

        # Research Question Bullets (14pt hanging indent for clean alignment)
        styles["RQBullet"] = ParagraphStyle(
            "RQBullet",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=12.5,
            leftIndent=14.0,
            firstLineIndent=-14.0,
            spaceAfter=2.5,
            wordWrap="CJK",
        )

        # Generative AI Disclosure Note (Elegant callout box before references)
        styles["AIDisclosure"] = ParagraphStyle(
            "AIDisclosure",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=7.0,
            leading=9.5,
            textColor=colors.HexColor("#334155"),
            backColor=colors.HexColor("#f8fafc"),
            borderColor=colors.HexColor("#94a3b8"),
            borderWidth=0.5,
            borderPadding=4.5,
            spaceBefore=5,
            spaceAfter=6,
            wordWrap="CJK",
        )

        # Table & Figure Captions (MS Gothic 8.5pt)
        styles["TableCaption"] = ParagraphStyle(
            "TableCaption",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=8.5,
            leading=11.0,
            alignment=1,  # Centered
            spaceBefore=6,
            spaceAfter=3,
            keepWithNext=True,
            wordWrap="CJK",
        )

        styles["FigureCaption"] = ParagraphStyle(
            "FigureCaption",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=8.5,
            leading=11.0,
            alignment=1,  # Centered
            spaceBefore=3,
            spaceAfter=6,
            wordWrap="CJK",
        )

        # Table Cell Typography
        styles["TableHeader"] = ParagraphStyle(
            "TableHeader",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=6.5,
            leading=8.5,
            alignment=1,  # Centered
            wordWrap="CJK",
        )

        styles["TableCell"] = ParagraphStyle(
            "TableCell",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=6.5,
            leading=8.5,
            alignment=1,  # Centered
            wordWrap="CJK",
        )

        styles["TableCellLeft"] = ParagraphStyle(
            "TableCellLeft",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=6.5,
            leading=8.5,
            alignment=0,  # Left
            wordWrap="CJK",
        )

        styles["TableNote"] = ParagraphStyle(
            "TableNote",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=6.0,
            leading=8.0,
            alignment=0,
            spaceAfter=4,
            wordWrap="CJK",
        )

        # References (Hanging indent: 2 characters = 17pt, JSET standard 8.5pt font)
        styles["Reference"] = ParagraphStyle(
            "Reference",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=12.0,
            leftIndent=17.0,
            firstLineIndent=-17.0,
            spaceAfter=3,
            wordWrap="CJK",
        )

        # Summary Block Styles (End of paper)
        styles["SummaryHeading"] = ParagraphStyle(
            "SummaryHeading",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=9.5,
            leading=13.0,
            alignment=1,  # Centered
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True,
            wordWrap="CJK",
        )

        styles["SummaryBody"] = ParagraphStyle(
            "SummaryBody",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.0,
            leading=11.5,
            spaceAfter=4,
            wordWrap="CJK",
        )

        styles["SummaryKeywords"] = ParagraphStyle(
            "SummaryKeywords",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.0,
            leading=11.5,
            spaceAfter=4,
            wordWrap="CJK",
        )

        styles["SummaryDate"] = ParagraphStyle(
            "SummaryDate",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=7.5,
            leading=10.0,
            alignment=1,
            spaceAfter=4,
            wordWrap="CJK",
        )

        return styles

    def _para(self, text: str, style: ParagraphStyle) -> Paragraph:
        """Constructs a Paragraph after standardizing text spaces, numbers, and formulas."""
        return Paragraph(clean_text_spaces(text), style)

    def _para_en(self, text: str, style: ParagraphStyle) -> Paragraph:
        """Constructs a Paragraph for English text with standard ASCII typography."""
        return Paragraph(clean_english_text(text), style)

    def _build_descriptive_stats_table(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> Table:
        """Constructs a JSET-standard three-line table (三本線表) for descriptive statistics."""
        headers = [
            Paragraph("指標名", self.styles["TableHeader"]),
            Paragraph("<i>K</i>", self.styles["TableHeader"]),
            Paragraph("平均", self.styles["TableHeader"]),
            Paragraph("SD", self.styles["TableHeader"]),
            Paragraph("中央値", self.styles["TableHeader"]),
            Paragraph("最小", self.styles["TableHeader"]),
            Paragraph("最大", self.styles["TableHeader"]),
        ]

        data = [headers]
        for m, s in analysis.descriptive_stats.items():
            metric_display = str(m)[:8] + "…" if len(str(m)) > 9 else str(m)
            row = [
                Paragraph(metric_display, self.styles["TableCellLeft"]),
                Paragraph(str(s.count), self.styles["TableCell"]),
                Paragraph(f"{s.mean:.1f}", self.styles["TableCell"]),
                Paragraph(f"{s.std:.1f}", self.styles["TableCell"]),
                Paragraph(f"{s.median:.1f}", self.styles["TableCell"]),
                Paragraph(f"{s.min_val:.1f}", self.styles["TableCell"]),
                Paragraph(f"{s.max_val:.1f}", self.styles["TableCell"]),
            ]
            data.append(row)

        col_widths = [64, 16, 25, 24, 25, 25, 25]  # Sum = 204 pt
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (-1, 0), 1.0, colors.black),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
                    ("LINEBELOW", (0, -1), (-1, -1), 1.0, colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("LEFTPADDING", (0, 0), (-1, -1), 1.5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 1.5),
                ]
            )
        )
        return table

    def _build_secondary_table(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> Tuple[str, Table, str]:
        """Constructs a secondary academic three-line table (Table 2) for trend regressions or correlations."""
        if analysis.trends and len(analysis.trends) > 0:
            headers = [
                Paragraph("指標名", self.styles["TableHeader"]),
                Paragraph("開始値", self.styles["TableHeader"]),
                Paragraph("最終値", self.styles["TableHeader"]),
                Paragraph("変化率", self.styles["TableHeader"]),
                Paragraph("CAGR", self.styles["TableHeader"]),
                Paragraph("傾き", self.styles["TableHeader"]),
                Paragraph("<i>R</i><sup>2</sup>", self.styles["TableHeader"]),
                Paragraph("<i>BF</i><sub>10</sub>", self.styles["TableHeader"]),
            ]
            data = [headers]
            for tr in analysis.trends[:6]:
                metric_name = str(tr.group_name or tr.metric)
                disp_name = metric_name[:7] + "…" if len(metric_name) > 8 else metric_name
                cagr_text = f"{tr.cagr:.1f}%" if tr.cagr is not None else "-"
                bf_text = format_bayes_factor(getattr(tr, "bf10", None))

                row = [
                    Paragraph(disp_name, self.styles["TableCellLeft"]),
                    Paragraph(f"{tr.start_val:.1f}", self.styles["TableCell"]),
                    Paragraph(f"{tr.end_val:.1f}", self.styles["TableCell"]),
                    Paragraph(f"{tr.pct_change:+.1f}%", self.styles["TableCell"]),
                    Paragraph(cagr_text, self.styles["TableCell"]),
                    Paragraph(f"{tr.slope:.2f}", self.styles["TableCell"]),
                    Paragraph(f"{tr.r_squared:.2f}", self.styles["TableCell"]),
                    Paragraph(bf_text, self.styles["TableCell"]),
                ]
                data.append(row)

            col_widths = [44, 23, 23, 23, 23, 22, 23, 23]  # Sum = 204 pt
            caption = "表２　時系列トレンド分析および回帰・ベイズ分析結果一覧"
            note = "注）CAGRは年平均成長率，傾きは単回帰直線の勾配，R²は決定係数，BF₁₀はJZSベイズファクター（>3でH1支持，<0.33でH0支持）．"

        elif analysis.correlations and len(analysis.correlations) > 0:
            headers = [
                Paragraph("指標X", self.styles["TableHeader"]),
                Paragraph("指標Y", self.styles["TableHeader"]),
                Paragraph("相関<i>r</i>", self.styles["TableHeader"]),
                Paragraph("<i>p</i>値", self.styles["TableHeader"]),
                Paragraph("<i>BF</i><sub>10</sub>", self.styles["TableHeader"]),
                Paragraph("BF証拠判定", self.styles["TableHeader"]),
            ]
            data = [headers]
            for cr in analysis.correlations[:5]:
                x_name = str(cr.metric_x)[:6] + "…" if len(str(cr.metric_x)) > 7 else str(cr.metric_x)
                y_name = str(cr.metric_y)[:6] + "…" if len(str(cr.metric_y)) > 7 else str(cr.metric_y)
                p_text = "<.001" if cr.p_value < 0.001 else f"{cr.p_value:.3f}"
                bf_val = getattr(cr, "bf10", None)
                bf_text = format_bayes_factor(bf_val)
                bf_interp_short = format_bayes_factor_short_interpretation(bf_val)

                row = [
                    Paragraph(x_name, self.styles["TableCellLeft"]),
                    Paragraph(y_name, self.styles["TableCellLeft"]),
                    Paragraph(f"{cr.pearson_r:+.2f}", self.styles["TableCell"]),
                    Paragraph(p_text, self.styles["TableCell"]),
                    Paragraph(bf_text, self.styles["TableCell"]),
                    Paragraph(bf_interp_short, self.styles["TableCell"]),
                ]
                data.append(row)

            col_widths = [45, 45, 27, 27, 27, 33]  # Sum = 204 pt
            caption = "表２　主要指標間における相関・有意確率・ベイズファクター一覧"
            note = "注）rはピアソン積率相関係数，p値は両側検定有意確率，BF₁₀はJZSベイズファクター（BF判定はH1対立仮説支持強度: >100で極めて強い，>3で中程度，1-3は弱い証拠/逸話的）．"

        else:
            headers = [
                Paragraph("指標名", self.styles["TableHeader"]),
                Paragraph("Q1(25%)", self.styles["TableHeader"]),
                Paragraph("中央値", self.styles["TableHeader"]),
                Paragraph("Q3(75%)", self.styles["TableHeader"]),
                Paragraph("IQR", self.styles["TableHeader"]),
                Paragraph("歪度", self.styles["TableHeader"]),
            ]
            data = [headers]
            for m, s in list(analysis.descriptive_stats.items())[:6]:
                metric_name = str(m)[:8] + "…" if len(str(m)) > 9 else str(m)
                row = [
                    Paragraph(metric_name, self.styles["TableCellLeft"]),
                    Paragraph(f"{s.q25:.1f}", self.styles["TableCell"]),
                    Paragraph(f"{s.median:.1f}", self.styles["TableCell"]),
                    Paragraph(f"{s.q75:.1f}", self.styles["TableCell"]),
                    Paragraph(f"{s.iqr:.1f}", self.styles["TableCell"]),
                    Paragraph(f"{s.skewness:.2f}", self.styles["TableCell"]),
                ]
                data.append(row)

            col_widths = [54, 30, 30, 30, 30, 30]  # Sum = 204 pt
            caption = "表２　主要指標における四分位範囲および分布形状一覧"
            note = "注）Q1/Q3は第1/第3四分位数，IQRは四分位範囲，歪度は分布の非対称性．"

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (-1, 0), 1.0, colors.black),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
                    ("LINEBELOW", (0, -1), (-1, -1), 1.0, colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("LEFTPADDING", (0, 0), (-1, -1), 1.5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 1.5),
                ]
            )
        )
        return caption, table, note

    def generate_pdf(
        self,
        paper: AcademicPaper,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        chart_path: Optional[Path],
        output_pdf_path: Path,
        secondary_chart_path: Optional[Path] = None,
    ) -> Path:
        """Generates the full academic thesis PDF document conforming to academic rules."""
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

        # Pass metadata to canvas
        JSETNumberedCanvas.current_paper = paper
        JSETNumberedCanvas.current_dataset = dataset

        doc = BaseDocTemplate(
            str(output_pdf_path),
            pagesize=JIS_B5,
            leftMargin=MARGIN_X,
            rightMargin=MARGIN_X,
            topMargin=MARGIN_TOP,
            bottomMargin=MARGIN_BOTTOM,
        )

        # ==========================================
        # 1. Page 1 Top Block Elements (Title & Abstract)
        # ==========================================
        clean_title = clean_text_spaces(paper.title)
        title_text = clean_title if clean_title.endswith("†") else f"{clean_title}†"
        title_formatted = format_title_two_lines(title_text)
        author_jp = "EduData 調査研究グループ＊1・教育データサイエンス解析班＊2"
        affil_jp = "オープン教育統計推進プロジェクト＊1・初等中等STEM教育データ基盤ユニット＊2"
        kw_jp = "， ".join(paper.keywords)

        # Enforce that the title is strictly at most 2 lines by auto-scaling font size
        title_font_size = 15.0
        title_leading = 19.0
        title_style = ParagraphStyle(
            "DynamicPaperTitle",
            parent=self.styles["PaperTitle"],
            fontSize=title_font_size,
            leading=title_leading,
        )
        p_title = Paragraph(title_formatted, title_style)
        _, h_title = p_title.wrap(PRINTABLE_W, 1000)

        while round(h_title / title_leading) > 2 and title_font_size > 11.0:
            title_font_size -= 0.5
            title_leading = title_font_size * 1.25
            title_style = ParagraphStyle(
                "DynamicPaperTitle",
                parent=self.styles["PaperTitle"],
                fontSize=title_font_size,
                leading=title_leading,
            )
            p_title = Paragraph(title_formatted, title_style)
            _, h_title = p_title.wrap(PRINTABLE_W, 1000)

        top_elements = [
            Spacer(1, 4),
            p_title,
        ]
        if paper.subtitle:
            top_elements.append(self._para(paper.subtitle, self.styles["PaperSubtitle"]))
        top_elements.extend([
            self._para(author_jp, self.styles["AuthorMeta"]),
            self._para(affil_jp, self.styles["AffiliationMeta"]),
            self._para(paper.abstract, self.styles["Abstract"]),
            self._para(f"キーワード：{kw_jp}", self.styles["Keywords"]),
        ])

        # Dynamically measure exact height required for the top block
        needed_top_h = 0.0
        for el in top_elements:
            _, h_el = el.wrap(PRINTABLE_W, 1000)
            space = getattr(el, "style", None)
            after = getattr(space, "spaceAfter", 0) if space else 0
            before = getattr(space, "spaceBefore", 0) if space else 0
            needed_top_h += h_el + after + before

        # Add safe buffer so ReportLab never spills elements into Column 1
        top_frame_h = needed_top_h + 12.0
        p1_c1_h = PRINTABLE_H - top_frame_h - BOX_H - 10.0
        p1_c2_h = PRINTABLE_H - top_frame_h

        # Page 1 Frames: Top 1-column + Bottom 2-column
        frame_top = Frame(
            MARGIN_X,
            PAGE_HEIGHT - MARGIN_TOP - top_frame_h,
            PRINTABLE_W,
            top_frame_h,
            id="p1_top",
            topPadding=0,
            bottomPadding=0,
            leftPadding=0,
            rightPadding=0,
        )
        frame_p1_c1 = Frame(
            MARGIN_X,
            MARGIN_BOTTOM + BOX_H + 10.0,
            COL_W,
            p1_c1_h,
            id="p1_c1",
            topPadding=0,
            bottomPadding=0,
            leftPadding=0,
            rightPadding=0,
        )
        frame_p1_c2 = Frame(
            MARGIN_X + COL_W + GUTTER,
            MARGIN_BOTTOM,
            COL_W,
            p1_c2_h,
            id="p1_c2",
            topPadding=0,
            bottomPadding=0,
            leftPadding=0,
            rightPadding=0,
        )

        # Later Pages Frames: 2 full-height columns
        frame_c1 = Frame(
            MARGIN_X,
            MARGIN_BOTTOM,
            COL_W,
            PRINTABLE_H,
            id="c1",
            topPadding=0,
            bottomPadding=0,
            leftPadding=0,
            rightPadding=0,
        )
        frame_c2 = Frame(
            MARGIN_X + COL_W + GUTTER,
            MARGIN_BOTTOM,
            COL_W,
            PRINTABLE_H,
            id="c2",
            topPadding=0,
            bottomPadding=0,
            leftPadding=0,
            rightPadding=0,
        )

        template_first = PageTemplate(
            id="FirstPage", frames=[frame_top, frame_p1_c1, frame_p1_c2]
        )
        template_later = PageTemplate(
            id="LaterPages", frames=[frame_c1, frame_c2]
        )
        doc.addPageTemplates([template_first, template_later])

        story = list(top_elements)
        # Transition to 2-column body text
        story.append(FrameBreak())
        story.append(NextPageTemplate("LaterPages"))

        # ==========================================
        # 2. Section 1: はじめに
        # ==========================================
        story.append(self._para("1．はじめに", self.styles["Heading1"]))
        story.append(self._para("1.1. 研究の背景", self.styles["Heading2"]))
        for p in paper.background.split("\n\n"):
            if p.strip():
                story.append(self._para(p.strip(), self.styles["Body"]))

        story.append(self._para("1.2. リサーチクエスチョンと作業仮説", self.styles["Heading2"]))
        for block in paper.objectives.split("\n"):
            line = block.strip()
            if not line:
                continue
            if line.startswith(("・", "-", "*", "（", "(")) or "RQ" in line[:6]:
                story.append(self._para(line, self.styles["RQBullet"]))
            else:
                story.append(self._para(line, self.styles["Body"]))

        # ==========================================
        # 3. Section 2: 調査対象および分析方法
        # ==========================================
        story.append(self._para("2．調査対象および分析方法", self.styles["Heading1"]))
        for p in paper.methodology.split("\n\n"):
            if p.strip():
                story.append(self._para(p.strip(), self.styles["Body"]))

        # ==========================================
        # 4. Section 3: 結果
        # ==========================================
        story.append(self._para("3．結果", self.styles["Heading1"]))
        for p in paper.results_text.split("\n\n"):
            if p.strip():
                story.append(self._para(p.strip(), self.styles["Body"]))

        # Table 1: Caption ABOVE the table
        first_m = dataset.metrics[0] if dataset.metrics else ""
        unit_note = resolve_metric_unit(first_m, dataset.unit)
        pop_info = getattr(analysis, "sample_population_size", "") or getattr(dataset, "sample_population_size", "")
        pop_str = f"（母集団規模: {pop_info}）" if pop_info else ""
        table1_elements = [
            self._para("表１　主要指標における基本記述統計量一覧", self.styles["TableCaption"]),
            self._build_descriptive_stats_table(dataset, analysis),
            self._para(f"注）単位は {unit_note}．<i>K</i>はデータ系列数{pop_str}，SDは不偏標準偏差．", self.styles["TableNote"]),
        ]
        story.append(KeepTogether(table1_elements))
        story.append(Spacer(1, 4))

        # Table 2: Caption ABOVE the table (Secondary Table)
        sec_cap, sec_table, sec_note = self._build_secondary_table(dataset, analysis)
        table2_elements = [
            self._para(sec_cap, self.styles["TableCaption"]),
            sec_table,
            self._para(sec_note, self.styles["TableNote"]),
        ]
        story.append(KeepTogether(table2_elements))
        story.append(Spacer(1, 4))

        # Figure 1: Caption BELOW the figure (Primary Chart)
        if chart_path and chart_path.exists():
            try:
                with PILImage.open(chart_path) as im:
                    orig_w, orig_h = im.size
                target_w = 200.0
                target_h = target_w * (orig_h / orig_w)
                if target_h > 115.0:
                    target_h = 115.0
                    target_w = target_h * (orig_w / orig_h)

                # Clean dataset title for concise academic caption
                clean_fig_title = dataset.title
                if "】" in clean_fig_title:
                    clean_fig_title = clean_fig_title.split("】", 1)[1].strip()
                if len(clean_fig_title) > 28:
                    clean_fig_title = clean_fig_title[:26] + "…"

                figure1_elements = [
                    Image(str(chart_path), width=target_w, height=target_h),
                    self._para(f"図１　{clean_fig_title}の経年推移と傾向分析（95%CI併記）", self.styles["FigureCaption"]),
                ]
                story.append(KeepTogether(figure1_elements))
                story.append(Spacer(1, 4))
            except Exception as e:
                logger.warning(f"Failed to embed primary chart into PDF: {e}")

        # Figure 2: Caption BELOW the figure (Secondary Chart)
        if secondary_chart_path and secondary_chart_path.exists():
            try:
                with PILImage.open(secondary_chart_path) as im:
                    orig_w, orig_h = im.size
                target_w = 200.0
                target_h = target_w * (orig_h / orig_w)
                if target_h > 115.0:
                    target_h = 115.0
                    target_w = target_h * (orig_w / orig_h)

                clean_fig_title2 = dataset.title
                if "】" in clean_fig_title2:
                    clean_fig_title2 = clean_fig_title2.split("】", 1)[1].strip()
                if len(clean_fig_title2) > 28:
                    clean_fig_title2 = clean_fig_title2[:26] + "…"

                figure2_elements = [
                    Image(str(secondary_chart_path), width=target_w, height=target_h),
                    self._para(f"図２　{clean_fig_title2}の相関構造および比較分析（95%CI併記）", self.styles["FigureCaption"]),
                ]
                story.append(KeepTogether(figure2_elements))
                story.append(Spacer(1, 4))
            except Exception as e:
                logger.warning(f"Failed to embed secondary chart into PDF: {e}")

        # ==========================================
        # 5. Section 4: 考察
        # ==========================================
        story.append(self._para("4．考察", self.styles["Heading1"]))
        for p in paper.discussion.split("\n\n"):
            if p.strip():
                story.append(self._para(p.strip(), self.styles["Body"]))

        # ==========================================
        # 6. References (参 考 文 献)
        # ==========================================
        story.append(PageBreak())
        story.append(self._para("参　考　文　献", self.styles["Heading1"]))
        sorted_references = sort_jset_references(paper.references)
        for ref in sorted_references:
            if ref.strip():
                story.append(self._para(ref.strip(), self.styles["Reference"]))

        # ==========================================
        # 7. English Summary & KEYWORDS (End of paper)
        # ==========================================
        story.append(FrameBreak())
        if paper.summary_en:
            summary_elements = [
                self._para_en("Summary", self.styles["SummaryHeading"]),
                self._para_en(paper.summary_en, self.styles["SummaryBody"]),
            ]
            if paper.keywords_en:
                kw_en_str = ", ".join(paper.keywords_en)
                summary_elements.append(
                    self._para_en(f"KEYWORDS: {kw_en_str}", self.styles["SummaryKeywords"])
                )
            summary_elements.append(
                self._para_en(
                    f"({get_jst_now().strftime('%B %d, %Y')})",
                    self.styles["SummaryDate"],
                )
            )
            story.append(KeepTogether(summary_elements))

        # ==========================================
        # 8. Generative AI Disclosure Note (After English SUMMARY)
        # ==========================================
        ai_notice_text = (
            "<b>【付記：生成AIによる自動執筆に関する開示】</b><br/>"
            "本論文は学生への教育目的で作成しています．<br/>"
            "（論文執筆に悩んでいる学生への応援も兼ねています）<br/><br/>"
            "内容について，使用しているデータは公的オープンデータです．<br/>"
            "Pythonによる統計解析エンジンの算出結果に基づき，"
            "生成AI（Generative AI: Anthropic Claude / Google Gemini）を活用して自動生成されています．<br/><br/>"
            "記載された統計数値および数理モデルは元データに準拠していますが，"
            "教育学的考察および提言の妥当性については，"
            "指導現場の実情に応じた批判的吟味を必ずしてください．"
        )
        story.append(Spacer(1, 6))
        story.append(self._para(ai_notice_text, self.styles["AIDisclosure"]))

        # Build document with JSETNumberedCanvas
        doc.build(story, canvasmaker=JSETNumberedCanvas)

        logger.info(f"Successfully generated JSET academic paper PDF: {output_pdf_path}")
        return output_pdf_path
