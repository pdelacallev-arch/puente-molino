"""Compatibilidad: ejecuta el renderizador ubicado en herramientas/documentos."""

from herramientas.documentos.render_calc import *  # noqa: F401,F403
from herramientas.documentos.render_calc import main


if __name__ == "__main__":
    main()
