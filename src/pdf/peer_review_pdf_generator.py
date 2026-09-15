"""
Academic Peer Review Report PDF Generation Engine.
Produces official, highly structured, and publication-grade A4 Peer Review Report PDFs (査読結果通知書・査読報告書)
conforming to academic journal editorial committee standards.
"""
from datetime import datetime
import logging
from pathlib import Path
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.peer_review import PeerReviewReport
from src.pdf.font_loader import register_japanese_fonts

logger = logging.getLogger(__name__)

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_X = 20.0 * mm        # 56.7 pt
MARGIN_Y = 20.0 * mm        # 56.7 pt
CONTENT_W = PAGE_WIDTH - 2 * MARGIN_X  # ~481.9 pt


class PeerReviewNumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render running headers and total page count."""

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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        self.saveState()
        p = self._pageNumber

        # Running Header (Pages >= 2)
        if p >= 2:
            self.setFont(self.mincho_font, 8.0)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(MARGIN_X, PAGE_HEIGHT - MARGIN_Y + 12, "学術論文誌 査読結果通知書・査読報告書 (Peer Review Report)")
            self.drawRightString(PAGE_WIDTH - MARGIN_X, PAGE_HEIGHT - MARGIN_Y + 12, f"審査書類 [Confidential]")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(MARGIN_X, PAGE_HEIGHT - MARGIN_Y + 8, PAGE_WIDTH - MARGIN_X, PAGE_HEIGHT - MARGIN_Y + 8)

        # Running Footer (All pages)
        self.setFont(self.mincho_font, 8.0)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(MARGIN_X, MARGIN_Y - 14, "※本通知書は学術審査に係る機密文書です．審査目的以外の無断転載・複製を禁じます．")
        self.drawRightString(PAGE_WIDTH - MARGIN_X, MARGIN_Y - 14, f"第 {p} 頁 / 全 {total_pages} 頁")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(MARGIN_X, MARGIN_Y - 6, PAGE_WIDTH - MARGIN_X, MARGIN_Y - 6)

        self.restoreState()


class PeerReviewPdfGenerator:
    """Generates official academic peer review report PDFs."""

    def __init__(self):
        self.mincho_font, self.gothic_font = register_japanese_fonts()
        self.styles = self._setup_styles()

    def _setup_styles(self):
        sheet = getSampleStyleSheet()
        styles = {}

        styles["HeaderOrg"] = ParagraphStyle(
            "HeaderOrg",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=9.0,
            leading=12.0,
            textColor=colors.HexColor("#475569"),
            spaceAfter=2,
        )

        styles["DocTitle"] = ParagraphStyle(
            "DocTitle",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=15.0,
            leading=19.0,
            textColor=colors.HexColor("#0f172a"),
            alignment=1,  # Center
            spaceAfter=12,
        )

        styles["MetaLabel"] = ParagraphStyle(
            "MetaLabel",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=8.5,
            leading=12.0,
            textColor=colors.HexColor("#1e293b"),
        )

        styles["MetaValue"] = ParagraphStyle(
            "MetaValue",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=12.0,
            textColor=colors.black,
        )

        styles["DecisionBadge"] = ParagraphStyle(
            "DecisionBadge",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=10.5,
            leading=14.0,
            textColor=colors.HexColor("#b91c1c"),  # Deep red for strict condition
            alignment=1,
        )

        styles["SectionHeading"] = ParagraphStyle(
            "SectionHeading",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=10.5,
            leading=14.0,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True,
        )

        styles["SubSectionHeading"] = ParagraphStyle(
            "SubSectionHeading",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=9.0,
            leading=12.5,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=6,
            spaceAfter=2,
            keepWithNext=True,
        )

        styles["Body"] = ParagraphStyle(
            "Body",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=13.0,
            firstLineIndent=8.5,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=4,
        )

        styles["CritiqueBox"] = ParagraphStyle(
            "CritiqueBox",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=13.0,
            textColor=colors.HexColor("#1e293b"),
            backColor=colors.HexColor("#f8fafc"),
            borderColor=colors.HexColor("#cbd5e1"),
            borderWidth=0.5,
            borderPadding=6,
            spaceBefore=4,
            spaceAfter=6,
        )

        styles["MajorRevisionItem"] = ParagraphStyle(
            "MajorRevisionItem",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=12.5,
            textColor=colors.HexColor("#0f172a"),
            backColor=colors.HexColor("#fff7ed"),  # subtle amber alert
            borderColor=colors.HexColor("#fdba74"),
            borderWidth=0.6,
            borderPadding=5.5,
            spaceBefore=3,
            spaceAfter=4,
        )

        styles["MinorRevisionItem"] = ParagraphStyle(
            "MinorRevisionItem",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=12.5,
            leftIndent=14.0,
            firstLineIndent=-14.0,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=3,
        )

        styles["QuestionItem"] = ParagraphStyle(
            "QuestionItem",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.5,
            leading=12.5,
            leftIndent=14.0,
            firstLineIndent=-14.0,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=3,
        )

        styles["TableHeader"] = ParagraphStyle(
            "TableHeader",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=8.0,
            leading=10.5,
            alignment=1,
            textColor=colors.HexColor("#0f172a"),
        )

        styles["TableCell"] = ParagraphStyle(
            "TableCell",
            parent=sheet["Normal"],
            fontName=self.mincho_font,
            fontSize=8.0,
            leading=11.0,
            textColor=colors.HexColor("#1e293b"),
        )

        styles["TableCellCenter"] = ParagraphStyle(
            "TableCellCenter",
            parent=sheet["Normal"],
            fontName=self.gothic_font,
            fontSize=8.5,
            leading=11.0,
            alignment=1,
            textColor=colors.HexColor("#0f172a"),
        )

        return styles

    def generate_pdf(
        self,
        review: PeerReviewReport,
        output_pdf_path: Path,
    ) -> Path:
        """Compiles the PeerReviewReport into a publication-grade A4 PDF."""
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            str(output_pdf_path),
            pagesize=A4,
            leftMargin=MARGIN_X,
            rightMargin=MARGIN_X,
            topMargin=MARGIN_Y,
            bottomMargin=MARGIN_Y,
        )

        story = []

        # 1. Header Organization Line
        header_table_data = [
            [
                Paragraph("学術論文誌 編集委員会 査読部会", self.styles["HeaderOrg"]),
                Paragraph(f"審査実施日: {review.review_date}", ParagraphStyle("HDate", parent=self.styles["HeaderOrg"], alignment=2)),
            ]
        ]
        t_head = Table(header_table_data, colWidths=[CONTENT_W * 0.6, CONTENT_W * 0.4])
        t_head.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        story.append(t_head)

        # 2. Document Title
        story.append(Paragraph("査読結果通知書・査読報告書 (Peer Review Report)", self.styles["DocTitle"]))
        story.append(HRFlowable(width="100%", thickness=1.0, color=colors.HexColor("#0f172a"), spaceAfter=8))

        # 3. Paper Meta & Decision Box
        clean_title = review.paper_title.rstrip("†").strip()
        meta_table_data = [
            [
                Paragraph("審査対象論文", self.styles["MetaLabel"]),
                Paragraph(f"<b>{clean_title}</b>", self.styles["MetaValue"]),
            ],
            [
                Paragraph("論文審査区分", self.styles["MetaLabel"]),
                Paragraph(f"{review.category}（学術査読論文 / 刷上り4頁以内）", self.styles["MetaValue"]),
            ],
            [
                Paragraph("査読判定結果", self.styles["MetaLabel"]),
                Paragraph(f"<b>【 {review.decision} 】</b>", self.styles["DecisionBadge"]),
            ],
        ]
        t_meta = Table(meta_table_data, colWidths=[85, CONTENT_W - 85])
        t_meta.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
            ("BACKGROUND", (1, 2), (1, 2), colors.HexColor("#fef2f2")),  # soft red background for decision
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#94a3b8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(t_meta)
        story.append(Spacer(1, 10))

        # 4. Evaluation Criteria Matrix Table (5大審査基準)
        story.append(Paragraph("1．審査評価マトリクス (Evaluation Matrix)", self.styles["SectionHeading"]))
        eval_headers = [
            Paragraph("審査評価項目", self.styles["TableHeader"]),
            Paragraph("評定", self.styles["TableHeader"]),
            Paragraph("評価所見および審査基準", self.styles["TableHeader"]),
        ]
        eval_rows = [eval_headers]

        criteria_list = [
            "独創性・新規性",
            "有用性・教育的貢献",
            "信頼性・統計的妥当性",
            "論理的一貫性・構成",
            "表現・体裁・引用規範",
        ]

        for crit in criteria_list:
            if crit in review.scores:
                grade, comment = review.scores[crit]
                # Color code grade
                grade_color = "#b91c1c" if "C" in grade else ("#0284c7" if "A" in grade else "#d97706")
                grade_p = Paragraph(f"<font color='{grade_color}'><b>{grade}</b></font>", self.styles["TableCellCenter"])
                eval_rows.append([
                    Paragraph(f"<b>{crit}</b>", self.styles["TableCell"]),
                    grade_p,
                    Paragraph(comment, self.styles["TableCell"]),
                ])

        t_eval = Table(eval_rows, colWidths=[105, 45, CONTENT_W - 150])
        t_eval.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("LINEABOVE", (0, 0), (-1, 0), 1.0, colors.HexColor("#0f172a")),
            ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.HexColor("#0f172a")),
            ("LINEBELOW", (0, -1), (-1, -1), 1.0, colors.HexColor("#0f172a")),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(t_eval)
        story.append(Spacer(1, 10))

        # 5. Overall Critique (総合講評)
        story.append(Paragraph("2．総合講評 (Overall Critique)", self.styles["SectionHeading"]))
        story.append(Paragraph(review.overall_critique, self.styles["CritiqueBox"]))
        story.append(Spacer(1, 6))

        # 6. Major Revisions (主要修正要求事項 - 必須項目)
        story.append(Paragraph("3．主要修正要求事項（Major Revisions：採録に向けた必須対応事項）", self.styles["SectionHeading"]))
        story.append(Paragraph(
            "以下の各項目は，学術論文としての信頼性および科学的妥当性を担保するために不可欠な修正要求です．"
            "再提出時には，修正箇所および各指摘への対応理由を明記した「修正対照表（Rebuttal Letter）」を必ず添付してください．",
            self.styles["Body"]
        ))
        for i, item in enumerate(review.major_revisions, 1):
            item_text = f"<b>[要求 {i}]</b> {item.strip()}"
            story.append(Paragraph(item_text, self.styles["MajorRevisionItem"]))
        story.append(Spacer(1, 6))

        # 7. Minor Revisions (軽微な修正事項)
        story.append(Paragraph("4．軽微な修正事項（Minor Revisions：表現・体裁等の改善点）", self.styles["SectionHeading"]))
        for i, item in enumerate(review.minor_revisions, 1):
            story.append(Paragraph(f"・ {item.strip()}", self.styles["MinorRevisionItem"]))
        story.append(Spacer(1, 6))

        # 8. Questions to Authors (著者への試問・確認事項)
        story.append(Paragraph("5．著者への試問・照会事項 (Questions to Authors)", self.styles["SectionHeading"]))
        for item in review.questions_to_authors:
            story.append(Paragraph(f"・ {item.strip()}", self.styles["QuestionItem"]))
        story.append(Spacer(1, 6))

        # 9. AI Disclosure Review (生成AI利用開示に対する評価)
        story.append(Paragraph("6．研究倫理および生成AI利用開示に関する審査所見", self.styles["SectionHeading"]))
        story.append(Paragraph(review.ai_disclosure_evaluation, self.styles["CritiqueBox"]))
        story.append(Spacer(1, 10))

        # 10. Reviewer Footnote Block
        footer_block = [
            HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=6),
            Paragraph(
                "<b>【査読担当委員 審査所見結び】</b><br/>"
                "本論文は公的オープンデータを適切にハンドリングし，教育工学的示唆を導出しようとする真摯な試みとして高く評価できます．"
                "上記に挙げた「マクロ集計データの制約と生態学的誤謬の回避」「因果関係の慎重な言述」「教育現場への処方箋の具体化」"
                "について誠実に対処いただくことで，学会誌ショートレターとして極めて学術価値の高い論文へと昇華するものと期待いたします．",
                self.styles["Body"]
            ),
        ]
        story.append(KeepTogether(footer_block))

        # Build document
        doc.build(story, canvasmaker=PeerReviewNumberedCanvas)
        logger.info(f"Successfully generated Peer Review PDF report: {output_pdf_path}")
        return output_pdf_path
