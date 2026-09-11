"""Resolución segura de rutas internas del subsistema."""

from __future__ import annotations

from pathlib import Path


RAIZ_SUPERESTRUCTURA = Path(__file__).resolve().parents[1]
RAIZ_CASOS = RAIZ_SUPERESTRUCTURA / "casos"
RAIZ_TEMPORAL = RAIZ_SUPERESTRUCTURA / ".tmp"


def asegurar_interna(ruta: str | Path) -> Path:
    """Impide que un nombre de caso o revisión escape del subsistema."""
    resuelta = Path(ruta).resolve()
    if resuelta != RAIZ_SUPERESTRUCTURA and RAIZ_SUPERESTRUCTURA not in resuelta.parents:
        raise ValueError(f"Ruta fuera de analisis_superestructura: {resuelta}")
    return resuelta


def carpeta_caso(caso: str, revision: str) -> Path:
    if not caso.strip() or not revision.strip():
        raise ValueError("El caso y la revisión no pueden estar vacíos")
    return asegurar_interna(RAIZ_CASOS / caso / revision)


def entrada_caso(caso: str, revision: str) -> Path:
    ruta = carpeta_caso(caso, revision) / "entrada.yaml"
    if not ruta.is_file():
        raise FileNotFoundError(f"No existe la entrada del caso: {ruta}")
    return ruta

