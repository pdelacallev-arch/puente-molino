"""Renderiza informe de valorización agosto 2026 usando plantilla IES2."""

import re
import os
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

PROJECT_ROOT = Path(__file__).resolve().parent
TEMPLATE = str(PROJECT_ROOT / "plantillas" / "plantilla_IES2.docx")
MARKDOWN = str(PROJECT_ROOT / "informes_actividades" / "informe_valorizacion_agosto_2026.md")
OUTPUT = str(PROJECT_ROOT / "informes_actividades" / "INFORME-VALORIZACION-AGOSTO-2026.docx")

FONT = "Calibri"
BLACK = RGBColor(0x00, 0x00, 0x00)
HEADER_BG = "D9D9D9"
BORDER_COLOR = "BFBFBF"
IMG_RE = re.compile(r'^!\[([^\]]*)\]\(([^)]+)\)$')


def parse_md(filepath):
    with open(filepath, encoding="utf-8") as f:
        return f.readlines()


def resolve_image_path(img_relpath):
    """Resolve an image path relative to the Markdown source file."""
    if os.path.isabs(img_relpath):
        return img_relpath
    return os.path.normpath(os.path.join(os.path.dirname(MARKDOWN), img_relpath.replace('/', os.sep)))


def is_table_line(line):
    return line.strip().startswith("|") and line.strip().endswith("|")


def parse_table(lines, i):
    while i < len(lines) and not lines[i].strip().startswith("|"):
        i += 1
    if i >= len(lines):
        return None, i
    headers = [h.strip() for h in lines[i].strip().split("|")[1:-1]]
    i += 1
    if i < len(lines) and re.match(r'^\|[\s\-:|]+\|$', lines[i].strip()):
        i += 1
    rows = []
    while i < len(lines):
        s = lines[i].strip()
        if not s.startswith("|"):
            break
        cells = [c.strip() for c in s.split("|")[1:-1]]
        if cells:
            rows.append(cells)
        i += 1
    return {"headers": headers, "rows": rows}, i


def shade(cell, color):
    cell._tc.get_or_add_tcPr().append(
        parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    )


def cell_margin(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'  <w:top w:w="30" w:type="dxa"/>'
        f'  <w:bottom w:w="30" w:type="dxa"/>'
        f'  <w:start w:w="60" w:type="dxa"/>'
        f'  <w:end w:w="60" w:type="dxa"/>'
        f'</w:tcMar>'
    ))


def table_borders(tbl):
    tbl._tbl.tblPr.append(parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="{BORDER_COLOR}"/>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{BORDER_COLOR}"/>'
        f'  <w:left w:val="single" w:sz="4" w:space="0" w:color="{BORDER_COLOR}"/>'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="{BORDER_COLOR}"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{BORDER_COLOR}"/>'
        f'  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="{BORDER_COLOR}"/>'
        f'</w:tblBorders>'
    ))


def keep_next(p):
    p._element.get_or_add_pPr().append(parse_xml(f'<w:keepNext {nsdecls("w")}/>'))


def keep_lines(p):
    p._element.get_or_add_pPr().append(parse_xml(f'<w:keepLines {nsdecls("w")}/>'))


def keep_with_next(p):
    keep_next(p)


def row_cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))


def row_header(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))


def set_cell_vertical_center(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:vAlign {nsdecls("w")} w:val="center"/>'))


def page_break_before(p):
    pPr = p._element.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:pageBreakBefore {nsdecls("w")}/>'))


def autofit_table(tbl):
    tblPr = tbl._tbl.tblPr
    tblPr.append(parse_xml(f'<w:tblW {nsdecls("w")} w:w="0" w:type="auto"/>'))
    tblPr.append(parse_xml(f'<w:tblLayout {nsdecls("w")} w:type="autofit"/>'))


def render():
    lines = parse_md(MARKDOWN)
    doc = Document(TEMPLATE)

    # ── margins 2.5 cm ──
    for sec in doc.sections:
        sec.top_margin = Cm(2.5)
        sec.bottom_margin = Cm(2.5)
        sec.left_margin = Cm(2.5)
        sec.right_margin = Cm(2.5)
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)

    # ── configure styles — all black, no colors ──
    def cfg(name, fname=None, size=None, bold=None, color=None,
            space_before=None, space_after=None, line_spacing=None,
            alignment=None):
        s = doc.styles[name]
        if fname:
            s.font.name = fname
            rPr = s.element.get_or_add_rPr()
            rf = rPr.find(qn('w:rFonts'))
            if rf is None:
                rf = parse_xml(f'<w:rFonts {nsdecls("w")}/>')
                rPr.insert(0, rf)
            rf.set(qn('w:eastAsia'), fname)
        if size:
            s.font.size = size
        if bold is not None:
            s.font.bold = bold
        if color:
            s.font.color.rgb = color
        if space_before is not None:
            s.paragraph_format.space_before = space_before
        if space_after is not None:
            s.paragraph_format.space_after = space_after
        if line_spacing is not None:
            s.paragraph_format.line_spacing = line_spacing
        if alignment is not None:
            s.paragraph_format.alignment = alignment

    cfg("Normal", fname=FONT, size=Pt(11), color=BLACK,
        line_spacing=1.15, space_after=Pt(6), space_before=Pt(0))
    cfg("Heading 1", fname=FONT, size=Pt(16), bold=True, color=BLACK,
        space_before=Pt(24), space_after=Pt(10), alignment=WD_ALIGN_PARAGRAPH.LEFT)
    cfg("Heading 2", fname=FONT, size=Pt(14), bold=True, color=BLACK,
        space_before=Pt(16), space_after=Pt(8), alignment=WD_ALIGN_PARAGRAPH.LEFT)
    cfg("Heading 3", fname=FONT, size=Pt(12), bold=True, color=BLACK,
        space_before=Pt(12), space_after=Pt(6), alignment=WD_ALIGN_PARAGRAPH.LEFT)
    cfg("List Paragraph", fname=FONT, size=Pt(11), color=BLACK,
        line_spacing=1.15, space_after=Pt(6))

    # ── numbering ──
    numbering_part = doc.part.numbering_part
    nlm = numbering_part.element
    for child in list(nlm):
        tag = child.tag
        if 'abstractNum' in tag or 'num' in tag:
            nlm.remove(child)

    abs_num = parse_xml(
        f'<w:abstractNum {nsdecls("w")} w:abstractNumId="0">'
        f'  <w:multiLevelType w:val="multilevel"/>'
        f'  <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="0" w:hanging="0"/></w:pPr></w:lvl>'
        f'  <w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1.%2."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="0" w:hanging="0"/></w:pPr></w:lvl>'
        f'  <w:lvl w:ilvl="2"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1.%2.%3."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="0" w:hanging="0"/></w:pPr></w:lvl>'
        f'</w:abstractNum>'
    )
    nlm.append(abs_num)
    num_elm = parse_xml(
        f'<w:num {nsdecls("w")} w:numId="1">'
        f'  <w:abstractNumId w:val="0"/>'
        f'</w:num>'
    )
    nlm.append(num_elm)

    # abstract numbering for bullet list (numId=2)
    abs_num2 = parse_xml(
        f'<w:abstractNum {nsdecls("w")} w:abstractNumId="1">'
        f'  <w:multiLevelType w:val="multilevel"/>'
        f'  <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="\u2022"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="567" w:hanging="283"/></w:pPr></w:lvl>'
        f'</w:abstractNum>'
    )
    nlm.append(abs_num2)
    num_elm2 = parse_xml(
        f'<w:num {nsdecls("w")} w:numId="2">'
        f'  <w:abstractNumId w:val="1"/>'
        f'</w:num>'
    )
    nlm.append(num_elm2)

    # ── clean body ──
    body = doc.element.body
    for child in list(body):
        if child.tag in (qn('w:p'), qn('w:tbl')):
            body.remove(child)

    # ── write content ──
    i = 0
    h1_counter = 0
    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()

        if not s:
            i += 1
            continue

        # ── headings ──
        if s.startswith("#"):
            level = len(s.split(" ")[0])
            text = s[level:].strip()
            style = {1: "Heading 1", 2: "Heading 2", 3: "Heading 3"}.get(level, "Heading 3")

            # page break before each H1
            if level == 1 and h1_counter > 0:
                p = doc.add_paragraph(style=style)
                page_break_before(p)
                p.clear()
            else:
                p = doc.add_paragraph(style=style)

            if level == 1:
                h1_counter += 1
                # H1: no numbering, plain title (INFORME DE ESTADO SITUACIONAL...)
                if not p.runs:
                    pass  # text will be added below
            elif level >= 2 and re.match(r'^\d', text):
                pPr = p._element.get_or_add_pPr()
                lvl_idx = level - 1  # 2->0, 3->1
                numPr = parse_xml(
                    f'<w:numPr {nsdecls("w")}>'
                    f'  <w:ilvl w:val="{lvl_idx}"/>'
                    f'  <w:numId w:val="1"/>'
                    f'</w:numPr>'
                )
                pPr.append(numPr)
                p.clear()

            # set heading text with black color
            if not p.text:
                run = p.add_run(text)
                sizes = {1: Pt(16), 2: Pt(14), 3: Pt(12)}
                run.bold = True
                run.font.size = sizes.get(level, Pt(12))
                run.font.name = FONT
                run.font.color.rgb = BLACK

            keep_next(p)
            i += 1
            continue

        # ── images embedded in Markdown ──
        img_match = IMG_RE.match(s)
        if img_match:
            alt_text, img_relpath = img_match.groups()
            p = doc.add_paragraph(style="Normal")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            img_path = resolve_image_path(img_relpath)
            if os.path.exists(img_path):
                run = p.add_run()
                run.add_picture(img_path, width=Cm(14.0))
            else:
                run = p.add_run(f"[Imagen no encontrada: {alt_text}]")
                run.italic = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)
            keep_next(p)
            i += 1
            continue

        # ── table captions ──
        if s.startswith("*") and s.endswith("*") and "Tabla" in s:
            text = s[1:-1]
            p = doc.add_paragraph(style="Normal")
            run = p.add_run(text)
            run.italic = True
            run.bold = True
            run.font.size = Pt(10)
            run.font.name = FONT
            run.font.color.rgb = BLACK
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            keep_next(p)
            i += 1
            continue

        # ── tables ──
        if is_table_line(s):
            result, nxt = parse_table(lines, i)
            if result:
                hdrs = result["headers"]
                rows = result["rows"]
                nc = len(hdrs)
                nr = 1 + len(rows)

                t = doc.add_table(rows=nr, cols=nc)
                t.style = "Table Grid"
                t.alignment = WD_TABLE_ALIGNMENT.CENTER
                table_borders(t)
                autofit_table(t)

                # header row
                for ci, h in enumerate(hdrs):
                    cell = t.rows[0].cells[ci]
                    cell.text = ""
                    set_cell_vertical_center(cell)
                    cell_margin(cell)
                    shade(cell, HEADER_BG)
                    row_header(t.rows[0])

                    p = cell.paragraphs[0]
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.space_before = Pt(1)
                    p.paragraph_format.space_after = Pt(1)
                    run = p.add_run(h)
                    run.bold = True
                    run.font.size = Pt(9)
                    run.font.name = FONT
                    run.font.color.rgb = BLACK

                # data rows — no shading, left-aligned
                for ri, rd in enumerate(rows):
                    row_cant_split(t.rows[ri + 1])
                    for ci, val in enumerate(rd):
                        if ci >= nc:
                            continue
                        cell = t.rows[ri + 1].cells[ci]
                        cell.text = ""
                        set_cell_vertical_center(cell)
                        cell_margin(cell)

                        p = cell.paragraphs[0]
                        p.paragraph_format.space_before = Pt(1)
                        p.paragraph_format.space_after = Pt(1)
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT

                        run = p.add_run(val)
                        run.font.size = Pt(8.5)
                        run.font.name = FONT
                        run.font.color.rgb = BLACK

                # spacer after table (minimal)
                sp = doc.add_paragraph()
                sp.paragraph_format.space_before = Pt(2)
                sp.paragraph_format.space_after = Pt(2)
                r = sp.add_run("")
                r.font.size = Pt(1)

                i = nxt
                continue
            else:
                i += 1
                continue

        # ── blockquotes ──
        if s.startswith(">"):
            text = s[1:].strip()
            p = doc.add_paragraph(style="Normal")
            run = p.add_run(text)
            run.italic = True
            run.font.size = Pt(10)
            run.font.name = FONT
            run.font.color.rgb = BLACK
            pPr = p._element.get_or_add_pPr()
            pPr.append(parse_xml(f'<w:ind {nsdecls("w")} w:left="567" w:right="567"/>'))
            pPr.append(parse_xml(
                f'<w:pBdr {nsdecls("w")}>'
                f'  <w:left w:val="single" w:sz="8" w:space="6" w:color="C0C0C0"/>'
                f'</w:pBdr>'
            ))
            keep_lines(p)
            i += 1
            continue

        # ── horizontal rule ──
        if s.startswith("---") and len(s) >= 3:
            p = doc.add_paragraph()
            pPr = p._element.get_or_add_pPr()
            pPr.append(parse_xml(
                f'<w:pBdr {nsdecls("w")}>'
                f'  <w:bottom w:val="single" w:sz="6" w:space="4" w:color="BBBBBB"/>'
                f'</w:pBdr>'
            ))
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(10)
            i += 1
            continue

        # ── regular paragraph ──
        p = doc.add_paragraph(style="Normal")
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        # detect bullet lines (starting with "- ")
        is_bullet = s.startswith("- ")
        if is_bullet:
            pPr = p._element.get_or_add_pPr()
            numPr = parse_xml(
                f'<w:numPr {nsdecls("w")}>'
                f'  <w:ilvl w:val="0"/>'
                f'  <w:numId w:val="2"/>'
                f'</w:numPr>'
            )
            pPr.append(numPr)

        # inline formatting: **bold** — restore original text exactly
        parts = re.split(r'(\*\*.*?\*\*)', s)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                run = p.add_run(part[2:-2])
                run.bold = True
            else:
                run = p.add_run(part)

        for run in p.runs:
            run.font.size = Pt(11)
            run.font.name = FONT
            run.font.color.rgb = BLACK

        # Keep with next for short lines
        if len(s) < 200:
            keep_next(p)

        i += 1

    # ── header — preserve government header from template ──
    # (already kept since we didn't modify header paragraphs)

    # ── footer page numbers ──
    for sec in doc.sections:
        footer = sec.footer
        footer.is_linked_to_previous = False
        for fp in footer.paragraphs:
            fp.clear()

        if footer.paragraphs:
            fp = footer.paragraphs[0]
        else:
            fp = footer.add_paragraph()
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fp.paragraph_format.space_before = Pt(4)

        def fld(code):
            r = fp.add_run()
            r._element.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>'))
            r2 = fp.add_run()
            r2._element.append(parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> {code} </w:instrText>'))
            r3 = fp.add_run()
            r3._element.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>'))

        fld("PAGE")
        fp.add_run(" / ")
        fld("NUMPAGES")

        for r in fp.runs:
            r.font.size = Pt(8)
            r.font.name = FONT
            r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    doc.save(OUTPUT)
    print(f"Documento generado: {OUTPUT}")


if __name__ == "__main__":
    render()