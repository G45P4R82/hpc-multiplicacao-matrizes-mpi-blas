#!/usr/bin/env python3
"""Gera o PDF do relatorio Markdown usando ReportLab disponivel no Lovelace."""
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate
from reportlab.platypus import Spacer, Table, TableStyle


def inline(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def build_story(source, styles):
    story = []
    lines = source.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), styles["TitleCustom"]))
            index += 1
            continue
        if line.startswith("## "):
            story.extend((Spacer(1, 8), Paragraph(inline(line[3:]), styles["Heading2"])))
            index += 1
            continue
        if line.startswith("- "):
            while index < len(lines) and lines[index].startswith("- "):
                story.append(Paragraph("&#8226; " + inline(lines[index][2:]), styles["BodyText"]))
                index += 1
            continue
        if line.startswith("|"):
            table_lines = []
            while index < len(lines) and lines[index].startswith("|"):
                if not re.match(r"^\|\s*:?-+", lines[index]):
                    cells = [cell.strip() for cell in lines[index].strip("|").split("|")]
                    table_lines.append([Paragraph(inline(cell), styles["Small"]) for cell in cells])
                index += 1
            table = Table(table_lines, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.extend((Spacer(1, 4), table, Spacer(1, 6)))
            continue
        if line.startswith("```"):
            code = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                code.append(lines[index])
                index += 1
            index += 1
            story.append(Paragraph(inline("<br/>".join(code)), styles["Small"]))
            continue
        paragraph = [line]
        index += 1
        while index < len(lines) and lines[index].strip() and not lines[index].startswith(("#", "- ", "|", "```")):
            paragraph.append(lines[index])
            index += 1
        story.extend((Paragraph(inline(" ".join(paragraph)), styles["BodyText"]), Spacer(1, 5)))
    return story


def main():
    root = Path(__file__).resolve().parents[1]
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCustom", parent=styles["Title"], alignment=TA_CENTER, spaceAfter=18))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10))
    story = build_story((root / "report/report.md").read_text(), styles)
    story.append(PageBreak())
    story.append(Paragraph("Graficos de desempenho", styles["Heading2"]))
    for path in sorted((root / "results/plots").glob("report_*.png")):
        story.extend((Paragraph(path.name, styles["Heading3"]), Image(str(path), width=17 * cm, height=9.4 * cm)))
    output = root / "report/report.pdf"
    SimpleDocTemplate(str(output), pagesize=A4, rightMargin=1.5 * cm, leftMargin=1.5 * cm,
                      topMargin=1.4 * cm, bottomMargin=1.4 * cm).build(story)
    print(f"pdf={output} bytes={output.stat().st_size}")


if __name__ == "__main__":
    main()
