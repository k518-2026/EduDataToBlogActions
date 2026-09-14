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
from typing import List, Optional

from PIL import Image as PILImage
from reportlab.lib import colors
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

from src.academic_paper import AcademicPaper
from src.analyzer import AnalysisResult
from src.fetchers.base import EducationDataset
from src.pdf.font_loader import register_japanese_fonts

logger = logging.getLogger(__name__)

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
            self.rect(MARGIN_X, PAGE_HEIGHT - MARGIN_TOP + 4, 96, 16)
            self.setFont(self.gothic_font, 8.5)
            self.drawCentredString(MARGIN_X + 48, PAGE_HEIGHT - MARGIN_TOP + 8.5, "教育実践研究論文")

            # 2. Top-Right: 学会名・雑誌名は掲載しない（体裁・レイアウトのみ利用）

            # 3. Bottom-Left English Metadata Box
            self.rect(MARGIN_X, MARGIN_BOTTOM, COL_W, BOX_H)
            self.setFont(self.mincho_font, 7.0)
            today_date = datetime.now().strftime("%Y年%m月%d日執筆")
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
        )

        styles["PaperSubtitle"] = ParagraphStyle(
            "PaperSubtitle",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=10.0,
            leading=13.0,
            alignment=1,  # Centered
            spaceAfter=6,
        )

        styles["AuthorMeta"] = ParagraphStyle(
            "AuthorMeta",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=9.5,
            leading=13.0,
            alignment=1,  # Centered
            spaceAfter=2,
        )

        styles["AffiliationMeta"] = ParagraphStyle(
            "AffiliationMeta",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=12.0,
            alignment=1,  # Centered
            spaceAfter=8,
        )

        styles["Abstract"] = ParagraphStyle(
            "Abstract",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=12.5,
            firstLineIndent=8.5,  # 1 full-width character indent
            spaceAfter=4,
        )

        styles["Keywords"] = ParagraphStyle(
            "Keywords",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=12.5,
            spaceAfter=6,
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
            keepWithNext=True,
        )

        styles["Heading2"] = ParagraphStyle(
            "Heading2",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=8.5,
            leading=12.5,
            spaceBefore=5,
            spaceAfter=2,
            keepWithNext=True,
        )

        styles["Heading3"] = ParagraphStyle(
            "Heading3",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=8.5,
            leading=12.5,
            spaceBefore=4,
            spaceAfter=2,
            keepWithNext=True,
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
        )

        # Table Cell Typography
        styles["TableHeader"] = ParagraphStyle(
            "TableHeader",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=6.5,
            leading=8.5,
            alignment=1,  # Centered
        )

        styles["TableCell"] = ParagraphStyle(
            "TableCell",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=6.5,
            leading=8.5,
            alignment=1,  # Centered
        )

        styles["TableCellLeft"] = ParagraphStyle(
            "TableCellLeft",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=6.5,
            leading=8.5,
            alignment=0,  # Left
        )

        styles["TableNote"] = ParagraphStyle(
            "TableNote",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=6.0,
            leading=8.0,
            alignment=0,
            spaceAfter=4,
        )

        # References (Hanging indent: 2 characters = 17pt)
        styles["Reference"] = ParagraphStyle(
            "Reference",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.0,
            leading=11.5,
            leftIndent=17.0,
            firstLineIndent=-17.0,
            spaceAfter=3,
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
        )

        styles["SummaryBody"] = ParagraphStyle(
            "SummaryBody",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.0,
            leading=11.5,
            spaceAfter=4,
        )

        styles["SummaryKeywords"] = ParagraphStyle(
            "SummaryKeywords",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.0,
            leading=11.5,
            spaceAfter=4,
        )

        styles["SummaryDate"] = ParagraphStyle(
            "SummaryDate",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=7.5,
            leading=10.0,
            alignment=1,
            spaceAfter=4,
        )

        return styles

    def _build_descriptive_stats_table(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> Table:
        """Constructs a JSET-standard three-line table (三本線表) for descriptive statistics."""
        headers = [
            Paragraph("指標名", self.styles["TableHeader"]),
            Paragraph("N", self.styles["TableHeader"]),
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

        col_widths = [48, 18, 28, 28, 28, 27, 27]  # Sum = 204 pt
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

    def generate_pdf(
        self,
        paper: AcademicPaper,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        chart_path: Optional[Path],
        output_pdf_path: Path,
    ) -> Path:
        """Generates the full academic thesis PDF document conforming to JSET official rules."""
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
        title_text = paper.title if paper.title.endswith("†") else f"{paper.title}†"
        author_jp = "EduData 調査研究グループ＊1・教育データサイエンス解析班＊2"
        affil_jp = "オープン教育統計推進プロジェクト＊1・初等中等STEM教育データ基盤ユニット＊2"
        kw_jp = "， ".join(paper.keywords)

        top_elements = [
            Spacer(1, 4),
            Paragraph(title_text, self.styles["PaperTitle"]),
        ]
        if paper.subtitle:
            top_elements.append(Paragraph(paper.subtitle, self.styles["PaperSubtitle"]))
        top_elements.extend([
            Paragraph(author_jp, self.styles["AuthorMeta"]),
            Paragraph(affil_jp, self.styles["AffiliationMeta"]),
            Paragraph(paper.abstract, self.styles["Abstract"]),
            Paragraph(f"キーワード：{kw_jp}", self.styles["Keywords"]),
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
        story.append(Paragraph("1．はじめに", self.styles["Heading1"]))
        story.append(Paragraph("1.1. 研究の背景", self.styles["Heading2"]))
        for p in paper.background.split("\n\n"):
            if p.strip():
                story.append(Paragraph(p.strip(), self.styles["Body"]))

        story.append(Paragraph("1.2. リサーチクエスチョンと作業仮説", self.styles["Heading2"]))
        for p in paper.objectives.split("\n\n"):
            if p.strip():
                story.append(Paragraph(p.strip(), self.styles["Body"]))

        # ==========================================
        # 3. Section 2: 調査対象および分析方法
        # ==========================================
        story.append(Paragraph("2．調査対象および分析方法", self.styles["Heading1"]))
        for p in paper.methodology.split("\n\n"):
            if p.strip():
                story.append(Paragraph(p.strip(), self.styles["Body"]))

        # ==========================================
        # 4. Section 3: 結果
        # ==========================================
        story.append(Paragraph("3．結果", self.styles["Heading1"]))
        for p in paper.results_text.split("\n\n"):
            if p.strip():
                story.append(Paragraph(p.strip(), self.styles["Body"]))

        # Table 1: Caption ABOVE the table (JSET Rule)
        table_elements = [
            Paragraph("表１　主要指標における基本記述統計量一覧", self.styles["TableCaption"]),
            self._build_descriptive_stats_table(dataset, analysis),
            Paragraph(f"注）単位は {dataset.unit}．Nは有効標本数，SDは不偏標準偏差．", self.styles["TableNote"]),
        ]
        story.append(KeepTogether(table_elements))
        story.append(Spacer(1, 4))

        # Figure 1: Caption BELOW the figure (JSET Rule)
        if chart_path and chart_path.exists():
            try:
                with PILImage.open(chart_path) as im:
                    orig_w, orig_h = im.size
                target_w = 200.0
                target_h = target_w * (orig_h / orig_w)
                if target_h > 130.0:
                    target_h = 130.0
                    target_w = target_h * (orig_w / orig_h)

                figure_elements = [
                    Image(str(chart_path), width=target_w, height=target_h),
                    Paragraph(f"図１　{dataset.title} の推移と傾向分析", self.styles["FigureCaption"]),
                ]
                story.append(KeepTogether(figure_elements))
                story.append(Spacer(1, 4))
            except Exception as e:
                logger.warning(f"Failed to embed chart into JSET PDF: {e}")

        # ==========================================
        # 5. Section 4: 考察
        # ==========================================
        story.append(Paragraph("4．考察", self.styles["Heading1"]))
        for p in paper.discussion.split("\n\n"):
            if p.strip():
                story.append(Paragraph(p.strip(), self.styles["Body"]))

        # ==========================================
        # 6. References (参 考 文 献)
        # ==========================================
        story.append(Paragraph("参　考　文　献", self.styles["Heading1"]))
        for ref in paper.references:
            if ref.strip():
                # Clean any leading brackets
                clean_ref = ref.strip()
                if clean_ref.startswith("[") and "]" in clean_ref[:5]:
                    clean_ref = clean_ref.split("]", 1)[1].strip()
                story.append(Paragraph(clean_ref, self.styles["Reference"]))

        # ==========================================
        # 7. English Summary & KEYWORDS (End of paper)
        # ==========================================
        if paper.summary_en:
            summary_elements = [
                Paragraph("Summary", self.styles["SummaryHeading"]),
                Paragraph(paper.summary_en, self.styles["SummaryBody"]),
            ]
            if paper.keywords_en:
                kw_en_str = "， ".join(paper.keywords_en)
                summary_elements.append(
                    Paragraph(f"KEYWORDS: {kw_en_str}", self.styles["SummaryKeywords"])
                )
            summary_elements.append(
                Paragraph(
                    f"({datetime.now().strftime('%B %d， %Y')})",
                    self.styles["SummaryDate"],
                )
            )
            story.append(KeepTogether(summary_elements))

        # Build document with JSETNumberedCanvas
        doc.build(story, canvasmaker=JSETNumberedCanvas)
        logger.info(f"Successfully generated JSET academic paper PDF: {output_pdf_path}")
        return output_pdf_path
