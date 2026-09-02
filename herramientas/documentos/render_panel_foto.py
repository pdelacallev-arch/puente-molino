#!/usr/bin/env python3
"""
render_panel_foto.py - Renderiza Panel Fotográfico (Markdown → DOCX)
con imágenes embebidas en las tablas.

Plantilla: plantilla_IES2.docx
Configuración: confi_aspecto.txt
"""

import re
import os
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

# ── Configuración ──
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASE = str(PROJECT_ROOT)
TEMPLATE = os.path.join(BASE, "plantillas", "plantilla_IES2.docx")
MARKDOWN = os.path.join(BASE, "entregables", "04_borradores", "panel_fotografico_ies_2026-07-15.md")
OUTPUT = os.path.join(BASE, "entregables", "04_borradores",
                      "ANEXO4-PANEL-FOTOGRAFICO-IES-001-EST-PRDV-GRA-2026_R00-BORRADOR.docx")
MARKDOWN_DIR = os.path.dirname(MARKDOWN)

FONT = "Calibri"
BLACK = RGBColor(0x00, 0x00, 0x00)
HEADER_BG = "D9D9D9"
BORDER_COLOR = "BFBFBF"
IMG_WIDTH_CM = 14.0  # image width in cm for photo panel

IMG_RE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
BR_RE = re.compile(r'<br\s*/?>', re.IGNORECASE)


def resolve_image_path(img_relpath):
    """Resolve a relative image path against the markdown file location."""
    if os.path.isabs(img_relpath):
        return img_relpath
    # Normalize path separators
    img_relpath = img_relpath.replace("/", os.sep).replace("\\", os.sep)
    full = os.path.normpath(os.path.join(MARKDOWN_DIR, img_relpath))
    return full


def parse_md(filepath):
    with open(filepath, encoding="utf-8") as f:
        return f.readlines()


def is_table_line(line):
    return line.strip().startswith("|") and line.strip().endswith("|")


def parse_table(lines, i):
    """Parse a markdown table starting at line i."""
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


# ── XML helpers ──
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


def row_cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))


def row_header(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))


def set_cell_vertical_center(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:vAlign {nsdecls("w")} w:val="center"/>'))


def set_cell_vertical_top(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:vAlign {nsdecls("w")} w:val="top"/>'))


def page_break_before(p):
    pPr = p._element.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:pageBreakBefore {nsdecls("w")}/>'))


def autofit_table(tbl):
    tblPr = tbl._tbl.tblPr
    tblPr.append(parse_xml(f'<w:tblW {nsdecls("w")} w:w="0" w:type="auto"/>'))
    tblPr.append(parse_xml(f'<w:tblLayout {nsdecls("w")} w:type="autofit"/>'))


def add_run_to_paragraph(paragraph, text, bold=False, size=Pt(11), italic=False, font_name=FONT, color=BLACK):
    """Add a formatted run to a paragraph."""
    run = paragraph.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = size
    run.font.name = font_name
    run.font.color.rgb = color
    return run


def create_paragraph(doc, style="Normal", alignment=WD_ALIGN_PARAGRAPH.LEFT,
                     space_before=Pt(0), space_after=Pt(0)):
    """Create and return a new paragraph with given formatting."""
    p = doc.add_paragraph(style=style)
    p.alignment = alignment
    p.paragraph_format.space_before = space_before
    p.paragraph_format.space_after = space_after
    return p


def embed_image_in_cell(cell, img_path, alt_text="", img_width_cm=IMG_WIDTH_CM):
    """Embed an image in a table cell, clearing existing content."""
    cell.text = ""
    set_cell_vertical_center(cell)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    if os.path.exists(img_path):
        run = p.add_run()
        run.add_picture(img_path, width=Cm(img_width_cm))
    else:
        # Fallback: show alt text if image not found
        run = p.add_run(f"[Imagen no encontrada: {alt_text}]")
        run.font.size = Pt(9)
        run.font.name = FONT
        run.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)
        run.italic = True


def fill_cell_with_text(cell, text, font_size=Pt(9), bold=False, alignment=WD_ALIGN_PARAGRAPH.LEFT):
    """Fill a table cell with text, handling <br> line breaks and **bold** formatting."""
    cell.text = ""
    set_cell_vertical_center(cell)

    # Split by <br>
    parts = BR_RE.split(text)

    for pi, part in enumerate(parts):
        if pi == 0:
            p = cell.paragraphs[0]
        else:
            p = cell.add_paragraph()

        p.alignment = alignment
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)

        # Handle inline **bold** markers
        segments = re.split(r'(\*\*.*?\*\*)', part)
        for seg in segments:
            if seg.startswith("**") and seg.endswith("**"):
                add_run_to_paragraph(p, seg[2:-2], bold=True, size=font_size)
            else:
                add_run_to_paragraph(p, seg, bold=bold, size=font_size)


def merge_all_cells_in_row(table, row_idx, num_cols):
    """Merge all cells in a given row into one."""
    if num_cols >= 2:
        start = table.rows[row_idx].cells[0]
        end = table.rows[row_idx].cells[num_cols - 1]
        start.merge(end)


def render():
    lines = parse_md(MARKDOWN)
    doc = Document(TEMPLATE)

    # ── Page setup: A4, 2.5 cm margins ──
    for sec in doc.sections:
        sec.top_margin = Cm(2.5)
        sec.bottom_margin = Cm(2.5)
        sec.left_margin = Cm(2.5)
        sec.right_margin = Cm(2.5)
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)

    # ── Configure styles ──
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

    # ── Numbering ──
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

    # ── Clean body (keep header from template) ──
    body = doc.element.body
    for child in list(body):
        if child.tag in (qn('w:p'), qn('w:tbl')):
            body.remove(child)

    # ── Write content ──
    i = 0
    h1_counter = 0
    photo_counter = 0  # track photo tables for formatting

    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()

        if not s:
            i += 1
            continue

        # ── Headings ──
        if s.startswith("#"):
            level = len(s.split(" ")[0])
            text = s[level:].strip()
            style = {1: "Heading 1", 2: "Heading 2", 3: "Heading 3"}.get(level, "Heading 3")

            if level == 1 and h1_counter > 0:
                p = doc.add_paragraph(style=style)
                page_break_before(p)
                p.clear()
            else:
                p = doc.add_paragraph(style=style)

            if level == 1:
                h1_counter += 1
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

            # Set heading text
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

        # ── Tables (photo panel) ──
        if is_table_line(s):
            result, nxt = parse_table(lines, i)
            if result:
                hdrs = result["headers"]
                rows = result["rows"]
                nc = len(hdrs) if hdrs else 1
                nr = 1 + len(rows)

                t = doc.add_table(rows=nr, cols=nc)
                t.style = "Table Grid"
                t.alignment = WD_TABLE_ALIGNMENT.CENTER
                table_borders(t)
                autofit_table(t)

                # Set column widths: if 2 cols, first 85%, second 15%
                if nc >= 2:
                    col_widths = [Cm(13.0), Cm(2.0)]
                    for ci, w in enumerate(col_widths[:nc]):
                        for row in t.rows:
                            row.cells[ci].width = w

                # ── Row 0: Header (Fotografía N.° XX) ──
                for ci, h in enumerate(hdrs):
                    cell = t.rows[0].cells[ci]
                    cell.text = ""
                    set_cell_vertical_center(cell)
                    cell_margin(cell)
                    if ci == 0:
                        shade(cell, HEADER_BG)

                    p = cell.paragraphs[0]
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    run = p.add_run(h)
                    run.bold = True
                    run.font.size = Pt(10)
                    run.font.name = FONT
                    run.font.color.rgb = BLACK

                row_header(t.rows[0])

                # ── Data rows ──
                for ri, rd in enumerate(rows):
                    dr = ri + 1  # actual row index in table
                    row_cant_split(t.rows[dr])

                    # Merge all cells in this row for a cleaner photo panel look
                    merge_all_cells_in_row(t, dr, nc)
                    cell = t.rows[dr].cells[0]
                    cell.text = ""
                    cell_margin(cell)

                    # Process the first column content (merged, so only cell 0 matters)
                    val = rd[0] if rd else ""

                    # Check for image markdown
                    img_match = IMG_RE.search(val)
                    if img_match:
                        alt_text = img_match.group(1)
                        img_relpath = img_match.group(2)
                        img_fullpath = resolve_image_path(img_relpath)

                        # Remove image syntax from the text
                        remaining = IMG_RE.sub('', val).strip().lstrip(',').strip()

                        # Embed the image
                        embed_image_in_cell(cell, img_fullpath, alt_text)
                        set_cell_vertical_center(cell)

                        # If there's remaining text after the image, add it
                        if remaining:
                            p2 = cell.add_paragraph()
                            p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
                            p2.paragraph_format.space_before = Pt(2)
                            p2.paragraph_format.space_after = Pt(2)
                            segments = re.split(r'(\*\*.*?\*\*)', remaining)
                            for seg in segments:
                                if seg.startswith("**") and seg.endswith("**"):
                                    add_run_to_paragraph(p2, seg[2:-2], bold=True, size=Pt(9))
                                else:
                                    add_run_to_paragraph(p2, seg, size=Pt(9))
                    else:
                        # Regular text cell (description rows)
                        fill_cell_with_text(cell, val, font_size=Pt(9))
                        # If it's the last row (description), align left
                        p = cell.paragraphs[0]
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                        for paragraph in cell.paragraphs:
                            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

                # Minimal spacer after table
                sp = doc.add_paragraph()
                sp.paragraph_format.space_before = Pt(6)
                sp.paragraph_format.space_after = Pt(6)
                r = sp.add_run("")
                r.font.size = Pt(1)

                i = nxt
                continue
            else:
                i += 1
                continue

        # ── Blockquotes ──
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

        # ── Horizontal rule ──
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

        # ── Regular paragraph ──
        p = doc.add_paragraph(style="Normal")
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        # Inline formatting: **bold**
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

    # ── Footer with page numbers ──
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
