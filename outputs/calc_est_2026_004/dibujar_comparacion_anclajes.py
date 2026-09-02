from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle


OUT = Path(__file__).resolve().parent


def concreto(ax):
    # Croquis dimensional basado en la cajuela acotada: pantalla 0.40 m,
    # vuelo de cajuela 1.30 m y espesor de cajuela 0.40 m.
    ax.add_patch(Rectangle((0.0, 0.0), 0.40, 2.34, facecolor="#f2f2f2", edgecolor="black", lw=1.7))
    ax.add_patch(Rectangle((0.0, -0.40), 1.70, 0.40, facecolor="#f2f2f2", edgecolor="black", lw=1.7))
    ax.add_patch(Polygon([(0.0, -0.40), (-0.85, -1.95), (0.0, -1.95)], closed=True,
                         facecolor="#f2f2f2", edgecolor="black", lw=1.7))
    ax.set_aspect("equal")
    ax.set_xlim(-1.05, 1.90)
    ax.set_ylim(-2.10, 0.55)
    ax.axis("off")


def cotar(ax, p1, p2, texto, color="#18864b", offset=(0, 0)):
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="|-|", color=color, lw=1.5))
    xm = (p1[0] + p2[0]) / 2 + offset[0]
    ym = (p1[1] + p2[1]) / 2 + offset[1]
    ax.text(xm, ym, texto, color=color, ha="center", va="center", fontsize=9,
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1.2))


fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.4), constrained_layout=True)

# Detalle del expediente.
ax = axes[0]
concreto(ax)
ax.set_title("DETALLE DEL EXPEDIENTE", fontsize=12, fontweight="bold")
bar = [(-0.72, -1.72), (0.0, -0.40), (0.30, -0.40), (0.30, -0.705)]
ax.plot([p[0] for p in bar], [p[1] for p in bar], color="#c62828", lw=3.2)
ax.scatter([0.0], [-0.40], color="#c62828", s=22, zorder=4)
cotar(ax, (0.0, -0.25), (0.30, -0.25), r"$a_{disp}=0.300\,m$")
cotar(ax, (0.43, -0.40), (0.43, -0.705), r"$x=12d_b=0.305\,m$")
ax.text(0.85, -1.05, r"$l_{dh,req}=0.385\,m$" + "\n" + r"$D/C=1.28$  NO CUMPLE",
        ha="center", va="center", fontsize=10, color="#9b1c1c",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#fff1f0", edgecolor="#c62828"))

# Propuesta.
ax = axes[1]
concreto(ax)
ax.set_title("LA PROPUESTA", fontsize=12, fontweight="bold")
start = (-0.72, -1.72)
joint = (0.0, -0.40)
bend = (0.145, -0.113)
end = (1.587, -0.113)
ax.plot([start[0], joint[0], bend[0], end[0]],
        [start[1], joint[1], bend[1], end[1]], color="#c62828", lw=3.2)
ax.scatter([joint[0]], [joint[1]], color="#c62828", s=22, zorder=4)
cotar(ax, (0.02, -0.47), (0.165, -0.183), r"$a=0.322\,m$", offset=(-0.12, 0.0))
cotar(ax, (0.145, 0.05), (1.587, 0.05), r"$x=1.443\,m$")
ax.text(0.82, -1.08,
        r"$L_{disp}=a+x=1.764\,m$" + "\n" +
        r"$l_{d,req}=1.465\,m$" + "\n" + r"$D/C=0.83$  CUMPLE",
        ha="center", va="center", fontsize=10, color="#176c3a",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#effaf3", edgecolor="#18864b"))

fig.suptitle("COMPARACIÓN DEL ANCLAJE SUPERIOR DE 4Ø1\" DEL CONTRAFUERTE", fontsize=13,
             fontweight="bold")
fig.savefig(OUT / "comparacion_anclajes_contrafuerte.png", dpi=220, bbox_inches="tight")
plt.close(fig)


# Control de constructibilidad de la sección de 0.40 m.
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.5), constrained_layout=True)

ax = axes[0]
ax.add_patch(Rectangle((0, 0), 400, 180, facecolor="#f5f5f5", edgecolor="black", lw=1.7))
centros = [87.7, 153.1, 218.5, 283.9]
for xc in centros:
    ax.add_patch(plt.Circle((xc, 90), 12.7, color="#b71c1c"))
ax.annotate("", xy=(0, 25), xytext=(400, 25), arrowprops=dict(arrowstyle="|-|", lw=1.4))
ax.text(200, 12, "400 mm", ha="center", va="center", fontsize=9)
ax.text(200, 155, "75 + 4×25.4 + 3×40 + 75 = 371.6 mm", ha="center", fontsize=9)
ax.text(200, 140, "Remanente geométrico: 28.4 mm", ha="center", fontsize=9, color="#176c3a")
ax.set_title("Una fila: cabida nominal", fontsize=10, fontweight="bold")
ax.set_xlim(-20, 420); ax.set_ylim(-5, 195); ax.set_aspect("equal"); ax.axis("off")

ax = axes[1]
ax.add_patch(Rectangle((0, 0), 400, 180, facecolor="#f5f5f5", edgecolor="black", lw=1.7))
for xc in (87.7, 153.1, 218.5, 283.9):
    ax.add_patch(plt.Circle((xc, 90), 12.7, color="#b71c1c"))
ax.add_patch(Rectangle((70, 55), 232, 70, fill=False, edgecolor="#1565c0", lw=2))
ax.text(200, 155, "Una fila: confinamiento efectivo", ha="center", fontsize=10)
ax.text(200, 140, "Horizontales Ø1/2\" @ 300 mm de las 2 mallas", ha="center", fontsize=9)
ax.set_title("", fontsize=10, fontweight="bold")
ax.set_xlim(-20, 420); ax.set_ylim(-5, 255); ax.set_aspect("equal"); ax.axis("off")

fig.suptitle("CONTROL DE CABIDA DE 4Ø1\" EN ESPESOR DE 0.40 m", fontsize=12, fontweight="bold")
fig.savefig(OUT / "constructibilidad_4barras_1pulg.png", dpi=220, bbox_inches="tight")
plt.close(fig)
