"""
Academic Paper PDF Generation Engine using ReportLab Platypus.
Produces professional, undergraduate thesis-level (学部の卒論水準) documents
with running headers/footers, embedded statistical tables, high-resolution charts,
and standard academic formatting.
"""
from datetime import datetime
import logging
from pathlib import Path
from typing import List, Optional

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.academic_paper import AcademicPaper
from src.analyzer import AnalysisResult
from src.fetchers.base import EducationDataset
from src.pdf.font_loader import register_japanese_fonts

logger = logging.getLogger(__name__)


class AcademicNumberedCanvas(canvas.Canvas):
    """Two-pass canvas that computes and renders running headers and 'Page X of Y' footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.reg_font, self.bold_font = register_japanese_fonts()

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count: int):
        self.saveState()
        self.setFont(self.reg_font, 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header (Top)
        header_text = "EduData 調査研究シリーズ / 査読ワーキングペーパー (Working Paper)"
        self.drawString(50, 842 - 32, header_text)
        today_str = datetime.now().strftime("%Y年%m月%d日 発行")
        self.drawRightString(595 - 50, 842 - 32, f"Open Access | {today_str}")

        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.6)
        self.line(50, 842 - 38, 595 - 50, 842 - 38)

        # Running Footer (Bottom)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.6)
        self.line(50, 42, 595 - 50, 42)

        footer_left = "EduDataToBlogActions Project / Open Education Statistics Pipeline"
        self.drawString(50, 28, footer_left)
        page_str = f"ページ {self._pageNumber} / {page_count}"
        self.drawRightString(595 - 50, 28, page_str)

        self.restoreState()


class EduPaperPdfGenerator:
    """Compiles an AcademicPaper into a print-ready, thesis-grade PDF document."""

    def __init__(self):
        self.reg_font, self.bold_font = register_japanese_fonts()
        self.styles = self._setup_styles()

    def _setup_styles(self) -> dict:
        sheet = getSampleStyleSheet()
        styles = {}

        styles["PaperTitle"] = ParagraphStyle(
            "PaperTitle",
            parent=sheet["Normal"],
            fontName=self.bold_font,
            fontSize=16,
            leading=21,
            alignment=1,  # Center
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=6,
        )

        styles["PaperSubtitle"] = ParagraphStyle(
            "PaperSubtitle",
            parent=sheet["Normal"],
            fontName=self.reg_font,
            fontSize=11,
            leading=15,
            alignment=1,  # Center
            textColor=colors.HexColor("#334155"),
            spaceAfter=12,
        )

        styles["AuthorMeta"] = ParagraphStyle(
            "AuthorMeta",
            parent=sheet["Normal"],
            fontName=self.reg_font,
            fontSize=9,
            leading=13,
            alignment=1,  # Center
            textColor=colors.HexColor("#475569"),
            spaceAfter=14,
        )

        styles["AbstractHeader"] = ParagraphStyle(
            "AbstractHeader",
            parent=sheet["Normal"],
            fontName=self.bold_font,
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=4,
        )

        styles["AbstractBody"] = ParagraphStyle(
            "AbstractBody",
            parent=sheet["Normal"],
            fontName=self.reg_font,
            fontSize=8.5,
            leading=13,
            textColor=colors.HexColor("#334155"),
            spaceAfter=6,
        )

        styles["Keywords"] = ParagraphStyle(
            "Keywords",
            parent=sheet["Normal"],
            fontName=self.reg_font,
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#1e293b"),
        )

        styles["Heading1"] = ParagraphStyle(
            "Heading1",
            parent=sheet["Normal"],
            fontName=self.bold_font,
            fontSize=11.5,
            leading=16,
            textColor=colors.HexColor("#1d3557"),
            spaceBefore=12,
            spaceAfter=5,
            keepWithNext=True,
        )

        styles["Body"] = ParagraphStyle(
            "Body",
            parent=sheet["Normal"],
            fontName=self.reg_font,
            fontSize=9,
            leading=14.5,
            textColor=colors.HexColor("#1e293b"),
            firstLineIndent=12,
            spaceAfter=5,
        )

        styles["Caption"] = ParagraphStyle(
            "Caption",
            parent=sheet["Normal"],
            fontName=self.bold_font,
            fontSize=8.5,
            leading=12,
            alignment=1,  # Center
            textColor=colors.HexColor("#334155"),
            spaceBefore=4,
            spaceAfter=8,
        )

        styles["TableHeader"] = ParagraphStyle(
            "TableHeader",
            parent=sheet["Normal"],
            fontName=self.bold_font,
            fontSize=7.5,
            leading=10,
            alignment=1,  # Center
            textColor=colors.HexColor("#ffffff"),
        )

        styles["TableCell"] = ParagraphStyle(
            "TableCell",
            parent=sheet["Normal"],
            fontName=self.reg_font,
            fontSize=7.5,
            leading=10,
            alignment=1,  # Center
            textColor=colors.HexColor("#0f172a"),
        )

        styles["TableCellLeft"] = ParagraphStyle(
            "TableCellLeft",
            parent=sheet["Normal"],
            fontName=self.reg_font,
            fontSize=7.5,
            leading=10,
            alignment=0,  # Left
            textColor=colors.HexColor("#0f172a"),
        )

        styles["Reference"] = ParagraphStyle(
            "Reference",
            parent=sheet["Normal"],
            fontName=self.reg_font,
            fontSize=8,
            leading=12,
            textColor=colors.HexColor("#334155"),
            leftIndent=14,
            firstLineIndent=-14,
            spaceAfter=4,
        )

        return styles

    def _build_descriptive_stats_table(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> Table:
        """Constructs an academic-standard data table for descriptive statistics."""
        headers = [
            Paragraph("指標名", self.styles["TableHeader"]),
            Paragraph("N", self.styles["TableHeader"]),
            Paragraph(f"平均値 ({dataset.unit})", self.styles["TableHeader"]),
            Paragraph(f"中央値 ({dataset.unit})", self.styles["TableHeader"]),
            Paragraph("標準偏差", self.styles["TableHeader"]),
            Paragraph(f"最小値 ({dataset.unit})", self.styles["TableHeader"]),
            Paragraph(f"最大値 ({dataset.unit})", self.styles["TableHeader"]),
            Paragraph(f"IQR ({dataset.unit})", self.styles["TableHeader"]),
        ]

        data = [headers]
        for m, s in analysis.descriptive_stats.items():
            row = [
                Paragraph(str(m), self.styles["TableCellLeft"]),
                Paragraph(str(s.count), self.styles["TableCell"]),
                Paragraph(f"{s.mean:.2f}", self.styles["TableCell"]),
                Paragraph(f"{s.median:.2f}", self.styles["TableCell"]),
                Paragraph(f"{s.std:.2f}", self.styles["TableCell"]),
                Paragraph(f"{s.min_val:.2f}", self.styles["TableCell"]),
                Paragraph(f"{s.max_val:.2f}", self.styles["TableCell"]),
                Paragraph(f"{s.iqr:.2f}", self.styles["TableCell"]),
            ]
            data.append(row)

        col_widths = [115, 25, 50, 50, 48, 50, 50, 50]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                    ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#1e293b")),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
                ]
            )
        )
        return table

    def generate_pdf(
        self,
        paper: AcademicPaper,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        chart_path: Path,
        output_pdf_path: Path,
    ) -> Path:
        """Generates the full academic graduation thesis PDF document."""
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_pdf_path),
            pagesize=A4,
            leftMargin=50,
            rightMargin=50,
            topMargin=48,
            bottomMargin=48,
        )

        story = []

        # 1. Title Block
        story.append(Spacer(1, 4))
        story.append(Paragraph(paper.title, self.styles["PaperTitle"]))
        if paper.subtitle:
            story.append(Paragraph(paper.subtitle, self.styles["PaperSubtitle"]))

        author_text = (
            f"<b>EduData 調査研究グループ（教育データサイエンス解析班）</b><br/>"
            f"調査対象: {dataset.source_name} | 単位: {dataset.unit} | 分野: {'算数・数学教育' if dataset.category == 'math' else '情報教育・プログラミング教育'} ({dataset.region})"
        )
        story.append(Paragraph(author_text, self.styles["AuthorMeta"]))

        # 2. Abstract & Keywords Callout Box
        keywords_joined = ", ".join(paper.keywords)
        abstract_box_content = [
            [Paragraph("<b>【論文要旨 (Abstract)】</b>", self.styles["AbstractHeader"])],
            [Paragraph(paper.abstract, self.styles["AbstractBody"])],
            [Paragraph(f"<b>【キーワード】</b> {keywords_joined}", self.styles["Keywords"])],
        ]
        abstract_table = Table(abstract_box_content, colWidths=[495])
        abstract_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                    ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#94a3b8")),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.append(abstract_table)
        story.append(Spacer(1, 10))

        # 3. Section 1: はじめに（研究の背景）
        story.append(Paragraph("1. はじめに（研究の背景）", self.styles["Heading1"]))
        for p in paper.background.split("\n\n"):
            if p.strip():
                story.append(Paragraph(p.strip(), self.styles["Body"]))

        # 4. Section 2: 研究の目的とリサーチクエスチョン
        story.append(Paragraph("2. 研究の目的とリサーチクエスチョン", self.styles["Heading1"]))
        for p in paper.objectives.split("\n\n"):
            if p.strip():
                story.append(Paragraph(p.strip(), self.styles["Body"]))

        # 5. Section 3: 調査対象および分析方法
        story.append(Paragraph("3. 調査対象および分析方法", self.styles["Heading1"]))
        for p in paper.methodology.split("\n\n"):
            if p.strip():
                story.append(Paragraph(p.strip(), self.styles["Body"]))

        # 6. Section 4: 分析結果
        story.append(Paragraph("4. 分析結果", self.styles["Heading1"]))
        for p in paper.results_text.split("\n\n"):
            if p.strip():
                story.append(Paragraph(p.strip(), self.styles["Body"]))

        # Embedded Table 1
        story.append(Spacer(1, 4))
        story.append(Paragraph("表1: 主要指標における基本記述統計量一覧", self.styles["Caption"]))
        stats_table = self._build_descriptive_stats_table(dataset, analysis)
        story.append(stats_table)
        story.append(Spacer(1, 10))

        # Embedded Figure 1
        if chart_path and chart_path.exists():
            try:
                with PILImage.open(chart_path) as im:
                    orig_w, orig_h = im.size
                target_w = 460
                target_h = target_w * (orig_h / orig_w)
                # Keep height within reasonable bounds
                if target_h > 230:
                    target_h = 230
                    target_w = target_h * (orig_w / orig_h)

                chart_elements = [
                    Image(str(chart_path), width=target_w, height=target_h),
                    Paragraph(f"図1: {dataset.title} の経年変化および比較分析可視化", self.styles["Caption"]),
                ]
                story.append(KeepTogether(chart_elements))
                story.append(Spacer(1, 6))
            except Exception as e:
                logger.warning(f"Failed to embed chart into PDF: {e}")

        # 7. Section 5: 考察および教育実践への示唆
        story.append(Paragraph("5. 考察および教育実践への示唆", self.styles["Heading1"]))
        for p in paper.discussion.split("\n\n"):
            if p.strip():
                story.append(Paragraph(p.strip(), self.styles["Body"]))

        # 8. Section 6: 引用・参考文献
        story.append(Paragraph("6. 引用・参考文献", self.styles["Heading1"]))
        for i, ref in enumerate(paper.references, 1):
            if ref.strip():
                ref_text = f"[{i}] {ref.strip()}" if not ref.strip().startswith("[") else ref.strip()
                story.append(Paragraph(ref_text, self.styles["Reference"]))

        # Build document with NumberedCanvas
        doc.build(story, canvasmaker=AcademicNumberedCanvas)
        logger.info(f"Successfully generated academic thesis PDF: {output_pdf_path}")
        return output_pdf_path
