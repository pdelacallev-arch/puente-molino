"""Renderiza un informe de remisión de RFI desde Markdown a DOCX.

Estilo (confi_aspecto.txt): A4 vertical, márgenes 2.5 cm, Calibri 11 pt,
interlineado 1.15, texto justificado, H3 = 12 pt bold, H4 = 11 pt bold,
tablas con bordes grises finos, encabezado #D9D9D9 en negrita, autofit,
cantSplit, centrado vertical; títulos de tabla en cursiva centrada;
notas destacadas (blockquote) con recuadro gris; numeración jerárquica
literal respetada del Markdown.
"""

import argparse
import re
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = str(PROJECT_ROOT / "plantillas" / "plantilla_IES2.docx")
MARKDOWN = str(PROJECT_ROOT / "informes_rfis" / "informe_003_remision_rfis_2026-07-24.md")
OUTPUT = str(PROJECT_ROOT / "entregables" / "04_borradores" / "informe_003_remision_rfis_2026-07-24.docx")

FONT = "Calibri"
BLACK = RGBColor(0x00, 0x00, 0x00)
HEADER_BG = "D9D9D9"
NOTE_BG = "F2F2F2"
BORDER_COLOR = "BFBFBF"
BODY_SIZE = Pt(11)
TABLE_SIZE = Pt(8)
CAPTION_SIZE = Pt(10)
NOTE_SIZE = Pt(10)
PAGE_W_CM = 16.0  # ancho útil A4 con márgenes 2.5 cm


# ────────────────────────── helpers ──────────────────────────

def parse_md(filepath):
    with open(filepath, encoding="utf-8") as f:
        return f.readlines()


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


def cell_margin(cell, top=20, bottom=20, left=60, right=60):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'  <w:top w:w="{top}" w:type="dxa"/>'
        f'  <w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'  <w:start w:w="{left}" w:type="dxa"/>'
        f'  <w:end w:w="{right}" w:type="dxa"/>'
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


def set_table_geometry(tbl, widths_cm):
    """Anchos fijos para que las tablas no queden desbordadas."""
    widths_dxa = [round(w * 567) for w in widths_cm]
    total_dxa = sum(widths_dxa)
    tbl.autofit = False
    tblPr = tbl._tbl.tblPr
    for tag in ("tblW", "tblLayout", "tblInd"):
        for node in list(tblPr.findall(qn(f"w:{tag}"))):
            tblPr.remove(node)
    tblPr.append(parse_xml(
        f'<w:tblW {nsdecls("w")} w:w="{total_dxa}" w:type="dxa"/>'
    ))
    tblPr.append(parse_xml(
        f'<w:tblInd {nsdecls("w")} w:w="0" w:type="dxa"/>'
    ))
    tblPr.append(parse_xml(
        f'<w:tblLayout {nsdecls("w")} w:type="fixed"/>'
    ))
    grid = tbl._tbl.tblGrid
    for node in list(grid):
        grid.remove(node)
    for width in widths_dxa:
        grid.append(parse_xml(
            f'<w:gridCol {nsdecls("w")} w:w="{width}"/>'
        ))
    for row in tbl.rows:
        for cell, width in zip(row.cells, widths_dxa):
            tcPr = cell._tc.get_or_add_tcPr()
            for node in list(tcPr.findall(qn("w:tcW"))):
                tcPr.remove(node)
            tcPr.insert(0, parse_xml(
                f'<w:tcW {nsdecls("w")} w:w="{width}" w:type="dxa"/>'
            ))


def table_widths(headers):
    n = len(headers)
    if n == 7:  # Tabla de cambios CG-06 a CG-09
        return [1.1, 2.0, 2.4, 2.5, 2.4, 2.9, 2.7]
    if n == 4:  # tablas comparativas geotécnica/hidrológica
        return [2.9, 3.9, 3.9, 5.3]
    return [PAGE_W_CM / n] * n


def add_inline_runs(paragraph, text, size, bold=False, italic=False):
    """Renderiza **negrita**, *cursiva* y `código` sin exponer la sintaxis."""
    text = text.replace(r'\"', '"')
    parts = re.split(r'(\*\*.*?\*\*|\*[^*]+?\*|`[^`]+`)', text)
    for part in parts:
        if not part:
            continue
        part_bold = bold
        part_italic = italic
        if part.startswith("**") and part.endswith("**"):
            part = part[2:-2]
            part_bold = True
        elif part.startswith("*") and part.endswith("*"):
            part = part[1:-1]
            part_italic = True
        elif part.startswith("`") and part.endswith("`"):
            part = part[1:-1]
        run = paragraph.add_run(part)
        run.bold = part_bold
        run.italic = part_italic
        run.font.size = size
        run.font.name = FONT
        run.font.color.rgb = BLACK


def render(markdown=MARKDOWN, output=OUTPUT):
    lines = parse_md(markdown)
    doc = Document(TEMPLATE)

    # ── márgenes y página A4 ──
    for sec in doc.sections:
        sec.top_margin = Cm(2.5)
        sec.bottom_margin = Cm(2.5)
        sec.left_margin = Cm(2.5)
        sec.right_margin = Cm(2.5)
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)

    # ── estilos ──
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

    cfg("Normal", fname=FONT, size=BODY_SIZE, color=BLACK,
        line_spacing=1.15, space_after=Pt(6), space_before=Pt(0))
    cfg("Heading 3", fname=FONT, size=Pt(12), bold=True, color=BLACK,
        space_before=Pt(12), space_after=Pt(6), alignment=WD_ALIGN_PARAGRAPH.LEFT)
    cfg("List Paragraph", fname=FONT, size=BODY_SIZE, color=BLACK,
        line_spacing=1.15, space_after=Pt(6))

    # quitar numeración heredada de títulos de la plantilla
    for style_name in ("Heading 1", "Heading 2", "Heading 3", "Heading 4"):
        if style_name in [st.name for st in doc.styles]:
            pPr = doc.styles[style_name].element.get_or_add_pPr()
            numPr = pPr.find(qn("w:numPr"))
            if numPr is not None:
                pPr.remove(numPr)

    # ── viñetas (numId 1) ──
    numbering_part = doc.part.numbering_part
    nlm = numbering_part.element
    for child in list(nlm):
        tag = child.tag
        if 'abstractNum' in tag or 'num' in tag:
            nlm.remove(child)

    abs_num = parse_xml(
        f'<w:abstractNum {nsdecls("w")} w:abstractNumId="0">'
        f'  <w:multiLevelType w:val="multilevel"/>'
        f'  <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/>'
        f'    <w:lvlText w:val="\u2022"/><w:lvlJc w:val="left"/>'
        f'    <w:pPr><w:ind w:left="567" w:hanging="283"/></w:pPr>'
        f'  </w:lvl>'
        f'</w:abstractNum>'
    )
    nlm.append(abs_num)
    num_elm = parse_xml(
        f'<w:num {nsdecls("w")} w:numId="1">'
        f'  <w:abstractNumId w:val="0"/>'
        f'</w:num>'
    )
    nlm.append(num_elm)

    # ── limpiar cuerpo ──
    body = doc.element.body
    for child in list(body):
        if child.tag in (qn('w:p'), qn('w:tbl')):
            body.remove(child)

    # ── escribir contenido ──
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()

        if not s:
            i += 1
            continue

        # ── encabezados (### / ####) ──
        if s.startswith("###"):
            level = len(s.split(" ")[0])
            text = s[level:].strip()
            is_h4 = level >= 4
            if is_h4 and "Heading 4" in [st.name for st in doc.styles]:
                style = "Heading 4"
            elif is_h4:
                style = "Normal"
            else:
                style = "Heading 3"
            p = doc.add_paragraph(style=style)
            if is_h4 and style == "Normal":
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(4)
            run = p.add_run(text)
            run.bold = True
            run.font.size = Pt(11) if is_h4 else Pt(12)
            run.font.name = FONT
            run.font.color.rgb = BLACK
            keep_next(p)
            i += 1
            continue

        # ── tablas ──
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
                set_table_geometry(t, table_widths(hdrs))

                # fila de encabezado
                row_header(t.rows[0])
                for ci, h in enumerate(hdrs):
                    cell = t.rows[0].cells[ci]
                    cell.text = ""
                    set_cell_vertical_center(cell)
                    cell_margin(cell)
                    shade(cell, HEADER_BG)
                    p = cell.paragraphs[0]
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.space_before = Pt(1)
                    p.paragraph_format.space_after = Pt(1)
                    add_inline_runs(p, h, TABLE_SIZE, bold=True)

                # filas de datos
                for ri, rd in enumerate(rows):
                    try:
                        row_cant_split(t.rows[ri + 1])
                    except Exception:
                        pass
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
                        # primera columna (ID o parámetro) en negrita
                        force_bold = ci == 0
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                        add_inline_runs(p, val, TABLE_SIZE, bold=force_bold)

                # espaciador posterior
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

        # ── blockquote: nota destacada ──
        if s.startswith(">"):
            text = s[1:].strip()
            p = doc.add_paragraph(style="Normal")
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.15
            add_inline_runs(p, text, NOTE_SIZE)
            pPr = p._element.get_or_add_pPr()
            pPr.append(parse_xml(f'<w:ind {nsdecls("w")} w:left="283" w:right="283"/>'))
            pPr.append(parse_xml(
                f'<w:pBdr {nsdecls("w")}>'
                f'  <w:top w:val="single" w:sz="6" w:space="6" w:color="{BORDER_COLOR}"/>'
                f'  <w:bottom w:val="single" w:sz="6" w:space="6" w:color="{BORDER_COLOR}"/>'
                f'  <w:left w:val="single" w:sz="12" w:space="8" w:color="{BORDER_COLOR}"/>'
                f'  <w:right w:val="single" w:sz="6" w:space="6" w:color="{BORDER_COLOR}"/>'
                f'</w:pBdr>'
            ))
            pPr.append(parse_xml(
                f'<w:shd {nsdecls("w")} w:fill="{NOTE_BG}"/>'
            ))
            keep_lines(p)
            i += 1
            continue

        # ── título de tabla en cursiva (*Tabla N.° X — ...*) ──
        if s.startswith("*") and s.endswith("*") and len(s) > 2 and not s.startswith("**"):
            p = doc.add_paragraph(style="Normal")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(2)
            add_inline_runs(p, s, CAPTION_SIZE, italic=True)
            keep_next(p)
            i += 1
            continue

        # ── viñetas (* ) ──
        is_bullet = s.startswith("* ") or s.startswith("- ")
        if is_bullet:
            text_content = s[2:]
            p = doc.add_paragraph(style="Normal")
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            pPr = p._element.get_or_add_pPr()
            pPr.append(parse_xml(
                f'<w:numPr {nsdecls("w")}>'
                f'  <w:ilvl w:val="0"/>'
                f'  <w:numId w:val="1"/>'
                f'</w:numPr>'
            ))
            add_inline_runs(p, text_content, BODY_SIZE)
            keep_next(p)
            i += 1
            continue

        # ── lista numerada literal (1. 2. 3.) con sangría ──
        if re.match(r'^\d+\.\s+', s):
            p = doc.add_paragraph(style="Normal")
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            pPr = p._element.get_or_add_pPr()
            pPr.append(parse_xml(f'<w:ind {nsdecls("w")} w:left="567" w:hanging="283"/>'))
            add_inline_runs(p, s, BODY_SIZE)
            keep_next(p)
            i += 1
            continue

        # ── regla horizontal ──
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

        # ── párrafo regular ──
        p = doc.add_paragraph(style="Normal")
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_inline_runs(p, s, BODY_SIZE)

        if len(s) < 200:
            keep_next(p)

        i += 1

    # ── pie de página con números ──
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

    doc.save(output)
    print(f"Documento generado: {output}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Renderiza un informe de remisión de RFI desde Markdown.")
    parser.add_argument("--input", default=MARKDOWN, help="Ruta del Markdown de entrada")
    parser.add_argument("--output", default=OUTPUT, help="Ruta del DOCX de salida")
    args = parser.parse_args()
    render(args.input, args.output)