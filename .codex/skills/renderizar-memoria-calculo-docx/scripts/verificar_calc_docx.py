#!/usr/bin/env python3
"""Verifica imágenes y ecuaciones al convertir una memoria Markdown a DOCX."""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}
IMAGE_RE = re.compile(r"!\[(?P<alt>[^]]*)\]\((?P<path>[^)]+)\)")
INLINE_MATH_RE = re.compile(r"(?<!\$)\$([^$\n]+)\$(?!\$)")
VISIBLE_LATEX_RE = re.compile(
    r"\$\$|(?<!\$)\$[^$\n]+\$(?!\$)|\\(?:frac|sqrt|sum|int|begin|end)\b"
)


def markdown_inventory(markdown: Path) -> tuple[list[Path], int]:
    lines = markdown.read_text(encoding="utf-8").splitlines()
    images: list[Path] = []
    math_count = 0
    in_math = False
    block_has_content = False
    for line in lines:
        stripped = line.strip()
        for match in IMAGE_RE.finditer(line):
            raw = match.group("path").strip().replace("\\", "/")
            images.append((markdown.parent / raw).resolve())
        if stripped.startswith("$$"):
            if in_math:
                if block_has_content:
                    math_count += 1
                in_math = False
                block_has_content = False
            else:
                in_math = True
            continue
        if in_math:
            block_has_content = block_has_content or bool(stripped)
        else:
            math_count += len(INLINE_MATH_RE.findall(line))
    if in_math:
        raise ValueError("Hay un bloque LaTeX $$ sin cierre en el Markdown.")
    return images, math_count


def docx_inventory(docx: Path) -> tuple[int, int, str]:
    with zipfile.ZipFile(docx) as package:
        document_xml = package.read("word/document.xml")
    root = ET.fromstring(document_xml)
    image_count = len(root.findall(".//a:blip", NS))
    math_count = len(root.findall(".//m:oMath", NS))
    visible_text = "\n".join(node.text or "" for node in root.findall(".//w:t", NS))
    return image_count, math_count, visible_text


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compara imágenes y LaTeX de un Markdown con su DOCX renderizado."
    )
    parser.add_argument("markdown", type=Path)
    parser.add_argument("docx", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    for path, label in ((args.markdown, "Markdown"), (args.docx, "DOCX")):
        if not path.is_file():
            errors.append(f"No existe {label}: {path}")
    if errors:
        print("\n".join(f"ERROR: {item}" for item in errors), file=sys.stderr)
        return 1
    try:
        images, expected_math = markdown_inventory(args.markdown.resolve())
        docx_images, docx_math, visible_text = docx_inventory(args.docx.resolve())
    except (ValueError, KeyError, ET.ParseError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    errors.extend(f"Imagen fuente inexistente: {path}" for path in images if not path.is_file())
    if docx_images != len(images):
        errors.append(f"Imágenes insertadas: DOCX={docx_images}, Markdown={len(images)}.")
    if docx_math != expected_math:
        errors.append(f"Ecuaciones OMML: DOCX={docx_math}, LaTeX esperado={expected_math}.")
    suspicious = sorted(set(match.group(0) for match in VISIBLE_LATEX_RE.finditer(visible_text)))
    if suspicious:
        errors.append(
            "Quedaron marcadores LaTeX visibles en el DOCX: " + ", ".join(suspicious[:8])
        )
    if re.search(r"(?:^|\n)#{1,6}\s|\*\*|!\[|`", visible_text):
        errors.append("Quedaron marcadores Markdown visibles en el DOCX.")
    print(f"Imágenes Markdown: {len(images)}; imágenes en cuerpo DOCX: {docx_images}")
    print(f"Expresiones LaTeX: {expected_math}; ecuaciones OMML en DOCX: {docx_math}")
    if errors:
        for item in errors:
            print(f"ERROR: {item}", file=sys.stderr)
        return 1
    print("VERIFICACIÓN ESTRUCTURAL: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
