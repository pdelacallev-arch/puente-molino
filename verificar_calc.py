"""Compatibilidad: ejecuta la verificación ubicada en herramientas/verificacion."""

import runpy


if __name__ == "__main__":
    runpy.run_module("herramientas.verificacion.verificar_calc", run_name="__main__")
