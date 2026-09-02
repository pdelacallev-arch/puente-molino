"""Compatibilidad: ejecuta el renderizador ubicado en herramientas/documentos."""

from herramientas.documentos.render_ies import *  # noqa: F401,F403


if __name__ == "__main__":
    render()
