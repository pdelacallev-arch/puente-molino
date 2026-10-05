"""Rutas seguras del subsistema de estabilidad."""

from __future__ import annotations

from pathlib import Path


RAIZ_ESTABILIDAD = Path(__file__).resolve().parents[1]
RAIZ_CASOS = RAIZ_ESTABILIDAD / "casos"
RAIZ_TEMPORAL = RAIZ_ESTABILIDAD / ".tmp"


def asegurar_interna(ruta: str | Path) -> Path:
    """Resuelve una ruta y rechaza cualquier salida del subsistema."""
    candidata = Path(ruta)
    if not candidata.is_absolute():
        # Permite las dos formas naturales de invocación:
        #   analisis_estabilidad/casos/... (relativa al proyecto)
        #   casos/...                      (relativa al subsistema)
        desde_cwd = (Path.cwd() / candidata).resolve()
        try:
            desde_cwd.relative_to(RAIZ_ESTABILIDAD.resolve())
        except ValueError:
            candidata = RAIZ_ESTABILIDAD / candidata
        else:
            candidata = desde_cwd
    candidata = candidata.resolve()
    try:
        candidata.relative_to(RAIZ_ESTABILIDAD.resolve())
    except ValueError as exc:
        raise ValueError(
            f"La ruta debe permanecer dentro de {RAIZ_ESTABILIDAD}: {candidata}"
        ) from exc
    return candidata


def carpeta_caso(caso: str, revision: str) -> Path:
    if not caso or not revision or ".." in caso or ".." in revision:
        raise ValueError("Caso y revisión deben ser identificadores válidos")
    candidata_rev = RAIZ_CASOS / Path(caso) / revision.upper()
    if (candidata_rev / "entrada.yaml").exists():
        return asegurar_interna(candidata_rev)
    candidata_sin_rev = RAIZ_CASOS / Path(caso)
    if (candidata_sin_rev / "entrada.yaml").exists():
        return asegurar_interna(candidata_sin_rev)
    return asegurar_interna(candidata_rev)
