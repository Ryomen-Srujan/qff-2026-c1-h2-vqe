from pathlib import Path
from xml.sax.saxutils import escape
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak
)

source = Path("report.md")
output = Path("report.pdf")

text = source.read_text(encoding="utf-8")
lines = text.splitlines()

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="ReportTitle", parent=styles["Title"],
    fontSize=19, leading=24, alignment=TA_CENTER,
    textColor=colors.HexColor("#17365D"), spaceAfter=12
))
styles.add(ParagraphStyle(
    name="Section", parent=styles["Heading2"],
    textColor=colors.HexColor("#17365D"),
    spaceBefore=12, spaceAfter=7
))
styles.add(ParagraphStyle(
    name="SmallBody", parent=styles["BodyText"],
    fontSize=9, leading=13, spaceAfter=6
))

def inline(text):
    text = escape(text.strip())
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.*?)`", r"<font name='Courier'>\1</font>", text)
    return text

story = []
i = 0

while i < len(lines):
    line = lines[i].strip()

    if not line or line == "---":
        story.append(Spacer(1, 5))
        i += 1
        continue

    if line.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            if not all(re.fullmatch(r"[-: ]+", c or " ") for c in cells):
                rows.append([Paragraph(inline(c), styles["SmallBody"]) for c in cells])
            i += 1

        if rows:
            table = Table(rows, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17365D")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.extend([table, Spacer(1, 8)])
        continue

    if line.startswith("# "):
        story.append(Paragraph(inline(line[2:]), styles["ReportTitle"]))
    elif line.startswith("## "):
        story.append(Paragraph(inline(line[3:]), styles["Section"]))
    elif line.startswith("### "):
        story.append(Paragraph(inline(line[4:]), styles["Heading3"]))
    elif line.startswith("- ") or line.startswith("* "):
        story.append(Paragraph("• " + inline(line[2:]), styles["SmallBody"]))
    else:
        story.append(Paragraph(inline(line), styles["SmallBody"]))

    i += 1

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(20 * mm, 12 * mm, "Qiskit Fall Fest 2026 | PS-C1")
    canvas.drawRightString(190 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate(
    str(output),
    pagesize=A4,
    rightMargin=18 * mm,
    leftMargin=18 * mm,
    topMargin=18 * mm,
    bottomMargin=22 * mm,
    title="Qiskit Fall Fest 2026 - PS-C1 Technical Report",
    author="Team Straw Hats"
)

doc.build(story, onFirstPage=footer, onLaterPages=footer)

print(f"PDF created successfully: {output.resolve()}")
print(f"PDF size: {output.stat().st_size:,} bytes")