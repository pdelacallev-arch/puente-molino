import argparse, re, os, io, shutil, subprocess, tempfile, zipfile
from copy import deepcopy
from pathlib import Path
from lxml import etree
import matplotlib.pyplot as plt
import matplotlib
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = str(PROJECT_ROOT / "plantillas" / "plantilla_IES2.docx")
MARKDOWN = str(PROJECT_ROOT / "entregables" / "04_borradores" / "CALC-EST-2026-001-R01.md")
OUTPUT = str(PROJECT_ROOT / "entregables" / "04_borradores" / "CALC-EST-2026-001-R01.docx")
BASE = str(PROJECT_ROOT)

FONT = "Calibri"
BLACK = RGBColor(0x00, 0x00, 0x00)
HEADER_BG = "D9D9D9"
BORDER_COLOR = "BFBFBF"
MATH_CACHE = {}
OMML_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def build_math_cache(lines):
    """Convierte las fórmulas una sola vez a OMML sin reconstruir el DOCX."""
    global MATH_CACHE
    formulas = []
    in_math = False
    block = []
    inline_pattern = re.compile(r'(?<!\$)\$([^$\n]+)\$(?!\$)')
    for raw in lines:
        text = raw.rstrip()
        if text.strip().startswith("$$"):
            if in_math:
                expression = "\n".join(block).strip()
                if expression and expression not in formulas:
                    formulas.append(expression)
                block = []
                in_math = False
            else:
                in_math = True
            continue
        if in_math:
            block.append(text.strip())
        else:
            for match in inline_pattern.finditer(text):
                expression = match.group(1).strip()
                if expression and expression not in formulas:
                    formulas.append(expression)

    if not formulas:
        MATH_CACHE = {}
        return
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("Pandoc es necesario para convertir LaTeX a ecuaciones nativas de Word.")
    with tempfile.TemporaryDirectory() as tmp:
        source = os.path.join(tmp, "formulas.md")
        output = os.path.join(tmp, "formulas.docx")
        with open(source, "w", encoding="utf-8") as f:
            for expression in formulas:
                f.write(f"$$\n{expression}\n$$\n\n")
        subprocess.run([
            pandoc, source, "--from", "markdown+tex_math_dollars", "--to", "docx",
            "--output", output,
        ], check=True)
        with zipfile.ZipFile(output) as package:
            root = etree.fromstring(package.read("word/document.xml"))
        equations = root.xpath(".//m:oMath", namespaces={"m": OMML_NS})
        if len(equations) != len(formulas):
            raise RuntimeError("No fue posible convertir todas las fórmulas LaTeX a OMML.")
        MATH_CACHE = dict(zip(formulas, equations))


def add_omml(paragraph, expression):
    """Inserta una ecuación nativa Word conservando el estilo del párrafo."""
    formula = MATH_CACHE.get(expression.strip())
    if formula is None:
        raise RuntimeError(f"Fórmula no encontrada en la caché OMML: {expression}")
    anchor = paragraph.add_run()
    anchor._element.addnext(deepcopy(formula))


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
    header_line = lines[i].strip()
    # Detect alignment markers in separator line
    headers = [h.strip() for h in header_line.split("|")[1:-1]]
    i += 1
    alignments = None
    if i < len(lines) and re.match(r'^\|[\s\-:|]+\|$', lines[i].strip()):
        sep = lines[i].strip()
        parts = sep.split("|")[1:-1]
        alignments = []
        for p in parts:
            p = p.strip()
            if p.startswith(":") and p.endswith(":"):
                alignments.append("center")
            elif p.endswith(":"):
                alignments.append("right")
            else:
                alignments.append("left")
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
    return {"headers": headers, "rows": rows, "alignments": alignments}, i


def shade(cell, color):
    cell._tc.get_or_add_tcPr().append(
        parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    )


def cell_margin(cell, top=30, bottom=30, left=60, right=60):
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


def autofit_table(tbl):
    tblPr = tbl._tbl.tblPr
    tblPr.append(parse_xml(f'<w:tblW {nsdecls("w")} w:w="0" w:type="auto"/>'))
    tblPr.append(parse_xml(f'<w:tblLayout {nsdecls("w")} w:type="autofit"/>'))


def page_break_before(p):
    p._element.get_or_add_pPr().append(parse_xml(f'<w:pageBreakBefore {nsdecls("w")}/>'))


def is_numeric(val):
    """Check if a value is numeric (for right-alignment)."""
    v = val.strip().replace(',', '').replace('.', '').replace('-', '').replace('−', '').replace('+', '').replace('%', '').replace(' ', '')
    if not v:
        return False
    # Check for common numeric patterns
    if re.match(r'^[\d]+$', v):
        return True
    if re.match(r'^[\d.]+$', val.strip().replace(',', '.').replace('−', '-').replace('+', '').replace('%', '').replace(' ', '').replace('—', '')):
        return True
    # Units
    if any(kw in val for kw in ['tf', 'm', 'cm', 'mm', 'kgf', 'MPa', '%', '°', 'tf/m', 'tf·m']):
        return True
    return False


def latex_to_image(math_lines, fontsize=11, dpi=150):
    """Render LaTeX display math to a PNG image buffer using matplotlib mathtext.

    Falls back to None if rendering fails (caller handles fallback).
    """
    expr = ' '.join(math_lines).strip()
    # Remove surrounding $$ or $ delimiters
    for prefix in ('$$', '$'):
        if expr.startswith(prefix):
            expr = expr[len(prefix):]
        if expr.endswith(prefix):
            expr = expr[:-len(prefix)]
    expr = expr.strip()

    if not expr:
        return None

    # Escape underscores in text mode — matplotlib mathtext handles \text{}
    # natively in recent versions, but we keep the expression as-is.
    # Replace \text{...} → \mathrm{...} for broader mathtext compatibility.
    expr_clean = re.sub(r'\\text\{([^}]*)\}', r'\\mathrm{\1}', expr)

    # Determine a reasonable figsize based on expression complexity
    n_chars = len(expr_clean)
    n_frac = expr_clean.count('\\frac')
    n_int = expr_clean.count('\\int') + expr_clean.count('\\sum')
    fig_w = min(max(n_chars * 0.055, 3.0), 14.0)
    fig_h = 0.5 + n_frac * 0.22 + n_int * 0.15

    times_font = r"C:\Windows\Fonts\times.ttf"
    if os.path.exists(times_font):
        matplotlib.font_manager.fontManager.addfont(times_font)

    try:
        fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
        plt.text(
            0.5, 0.5, f'${expr_clean}$',
            fontsize=fontsize + 1,
            ha='center', va='center',
            transform=fig.transFigure,
            fontfamily='serif',
        )
        plt.axis('off')
        buf = io.BytesIO()
        plt.savefig(
            buf, format='png', dpi=dpi,
            bbox_inches='tight', pad_inches=0.08,
            facecolor='white', edgecolor='none',
        )
        plt.close(fig)
        buf.seek(0)
        return buf
    except Exception as exc:
        print(f"  [aviso] No se pudo renderizar LaTeX como imagen: {exc}")
        print(f"         Expresión: {expr}")
        return None


def add_inline_latex(paragraph, text, size=Pt(11), bold=False):
    """Agrega texto y expresiones $...$ como imágenes matemáticas en línea."""
    parts = re.split(r'(\$[^$]+\$)', text)
    for part in parts:
        if not part:
            continue
        if part.startswith('$') and part.endswith('$'):
            add_omml(paragraph, part[1:-1])
            continue
        run = paragraph.add_run(part)
        run.bold = bold
        run.font.size = size
        run.font.name = FONT
        run.font.color.rgb = BLACK


def render(markdown=None, output=None, template=None):
    global MARKDOWN, OUTPUT, TEMPLATE
    if markdown is not None:
        MARKDOWN = str(Path(markdown).resolve())
    if output is not None:
        OUTPUT = str(Path(output).resolve())
    if template is not None:
        TEMPLATE = str(Path(template).resolve())

    for required, label in ((MARKDOWN, "Markdown"), (TEMPLATE, "plantilla DOCX")):
        if not os.path.isfile(required):
            raise FileNotFoundError(f"No existe {label}: {required}")
    Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)

    lines = parse_md(MARKDOWN)
    build_math_cache(lines)
    doc = Document(TEMPLATE)

    # ── margins 2.5 cm ──
    for sec in doc.sections:
        sec.top_margin = Cm(2.5)
        sec.bottom_margin = Cm(2.5)
        sec.left_margin = Cm(2.5)
        sec.right_margin = Cm(2.5)
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)

    # ── configure styles ──
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
    # Create Heading 4 style if not present
    if "Heading 4" not in [st.name for st in doc.styles]:
        h4 = doc.styles.add_style("Heading 4", 1)  # 1 = paragraph style
    cfg("Heading 4", fname=FONT, size=Pt(11), bold=True, color=BLACK,
        space_before=Pt(10), space_after=Pt(4), alignment=WD_ALIGN_PARAGRAPH.LEFT)

    # ── clean body ──
    body = doc.element.body
    for child in list(body):
        if child.tag in (qn('w:p'), qn('w:tbl')):
            body.remove(child)

    # ── write content ──
    i = 0
    in_math = False
    math_lines = []
    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()

        if not s:
            i += 1
            continue

        # Explicit pagination control for long calculation memos.
        if s == "<!-- pagebreak -->":
            p = doc.add_paragraph()
            page_break_before(p)
            i += 1
            continue

        # ── Math block ──
        if s.startswith("$$"):
            if in_math:
                in_math = False
                p = doc.add_paragraph(style="Normal")
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                add_omml(p, "\n".join(math_lines))
                math_lines = []
                i += 1
                continue
            else:
                in_math = True
                i += 1
                continue

        if in_math:
            math_lines.append(s)
            i += 1
            continue

        # ── headings ──
        if s.startswith("#"):
            level = len(s.split(" ")[0])
            text = s[level:].strip()
            style_map = {1: "Heading 1", 2: "Heading 2", 3: "Heading 3", 4: "Heading 4"}
            style = style_map.get(level, "Heading 4")

            p = doc.add_paragraph(style=style)
            run = p.add_run(text)
            run.bold = True
            sizes = {1: Pt(16), 2: Pt(14), 3: Pt(12), 4: Pt(11)}
            run.font.size = sizes.get(level, Pt(11))
            run.font.name = FONT
            run.font.color.rgb = BLACK
            keep_next(p)
            i += 1
            continue

        # ── images ──
        if s.startswith("!["):
            alt_match = re.match(r'^!\[(.*?)\]\((.*?)\)', s)
            if alt_match:
                alt_text = alt_match.group(1)
                rel_path = alt_match.group(2).replace("\\", "/")
                # Resolve path relative to markdown location
                abs_path = os.path.normpath(os.path.join(os.path.dirname(MARKDOWN), rel_path))
                if not os.path.isfile(abs_path):
                    raise FileNotFoundError(
                        f"No se pudo insertar la imagen '{rel_path}' resuelta como: {abs_path}"
                    )
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(abs_path, width=Cm(14))
                keep_next(p)
                i += 1
                continue

        # ── figure captions (italic lines like *Figura A3-5 ...*) ──
        if s.startswith("*") and s.endswith("*") and ("Figura" in s or "figura" in s):
            text = s[1:-1]
            p = doc.add_paragraph(style="Normal")
            run = p.add_run(text)
            run.italic = True
            run.bold = True
            run.font.size = Pt(10)
            run.font.name = FONT
            run.font.color.rgb = BLACK
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(8)
            keep_next(p)
            i += 1
            continue

        # ── tables ──
        if is_table_line(s):
            result, nxt = parse_table(lines, i)
            if result:
                hdrs = result["headers"]
                rows = result["rows"]
                alignments = result.get("alignments")
                nc = len(hdrs)
                nr = 1 + len(rows)

                t = doc.add_table(rows=nr, cols=nc)
                t.style = "Table Grid"
                t.alignment = WD_TABLE_ALIGNMENT.CENTER
                table_borders(t)
                autofit_table(t)

                # header row
                row_header(t.rows[0])
                for ci, h in enumerate(hdrs):
                    cell = t.rows[0].cells[ci]
                    cell.text = ""
                    set_cell_vertical_center(cell)
                    cell_margin(cell)
                    shade(cell, HEADER_BG)
                    cp = cell.paragraphs[0]
                    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    cp.paragraph_format.space_before = Pt(1)
                    cp.paragraph_format.space_after = Pt(1)
                    add_inline_latex(cp, h, size=Pt(9), bold=True)

                # data rows
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
                        cp = cell.paragraphs[0]
                        cp.paragraph_format.space_before = Pt(1)
                        cp.paragraph_format.space_after = Pt(1)

                        # Determine alignment
                        if alignments and ci < len(alignments):
                            al = alignments[ci]
                            if al == "center":
                                cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            elif al == "right":
                                cp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                            else:
                                cp.alignment = WD_ALIGN_PARAGRAPH.LEFT
                        else:
                            # Auto-detect: numeric right-aligned, others left
                            if is_numeric(val):
                                cp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                            else:
                                cp.alignment = WD_ALIGN_PARAGRAPH.LEFT

                        is_id = ci == 0 and re.match(r'^[A-Z]', val.strip()) and 'tf' not in val
                        add_inline_latex(cp, val, size=Pt(8), bold=is_id)

                # spacer
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

        # Handle inline bold, code spans and LaTeX in inline math delimiters.
        parts = re.split(r'(\*\*.*?\*\*|`[^`]+`)', s)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                add_inline_latex(p, part[2:-2], size=Pt(11), bold=True)
            elif part.startswith("`") and part.endswith("`"):
                add_inline_latex(p, part[1:-1], size=Pt(11), bold=False)
            else:
                add_inline_latex(p, part, size=Pt(11), bold=False)

        if len(s) < 150:
            keep_next(p)

        i += 1

    # ── footer page numbers ──
    def configure_footer(footer):
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

        fp.add_run("Página ")
        fld("PAGE")
        fp.add_run(" de ")
        fld("NUMPAGES")
        for r in fp.runs:
            r.font.size = Pt(8)
            r.font.name = FONT
            r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    for sec in doc.sections:
        configure_footer(sec.footer)
        configure_footer(sec.even_page_footer)
        configure_footer(sec.first_page_footer)

    doc.save(OUTPUT)
    print(f"Documento generado: {OUTPUT}")


def render_native_math():
    """Renderiza Markdown a DOCX conservando LaTeX como ecuaciones OMML nativas."""
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError(
            "Pandoc no está disponible; se requiere para convertir LaTeX a OMML nativo de Word."
        )
    command = [
        pandoc,
        MARKDOWN,
        "--from", "markdown+tex_math_dollars+pipe_tables",
        "--to", "docx",
        "--reference-doc", TEMPLATE,
        "--resource-path", f"{BASE};{os.path.dirname(MARKDOWN)}",
        "--output", OUTPUT,
    ]
    subprocess.run(command, check=True)
    print(f"Documento generado con ecuaciones nativas de Word: {OUTPUT}")


def main():
    parser = argparse.ArgumentParser(
        description="Renderiza una memoria de cálculo Markdown a DOCX con ecuaciones OMML."
    )
    parser.add_argument("--input", default=MARKDOWN, help="Archivo Markdown de entrada")
    parser.add_argument("--output", help="DOCX de salida; por defecto usa el nombre del Markdown")
    parser.add_argument("--template", default=TEMPLATE, help="Plantilla DOCX de referencia")
    args = parser.parse_args()
    output = args.output or str(Path(args.input).with_suffix(".docx"))
    render(args.input, output, args.template)


if __name__ == "__main__":
    main()
