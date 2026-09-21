"""Genera la imagen comparacion_secciones_vigas.png — cota exacta al borde de la viga."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

beam_data = [
    {
        "title": "Anexo 2 (ET)",
        "subtitle": "As = 815.5 cm² | canto = 1832 mm",
        "top_label": "450×25",
        "web_label": "1750×19",
        "bot_label": "650×25",
        "plat_label": "650×32 (platabanda)",
        "height_label": "1832 mm",
        "alasup_w": 450, "alasup_h": 25,
        "alma_w": 19, "alma_h": 1750,
        "alainf_w": 650, "alainf_h": 25,
        "plat_w": 650, "plat_h": 32,
    },
    {
        "title": "PLANO E-02",
        "subtitle": "As = 635.7 cm² | canto = 1825 mm",
        "top_label": "450×20",
        "web_label": "1755×14",
        "bot_label": "600×50",
        "height_label": "1825 mm",
        "alasup_w": 450, "alasup_h": 20,
        "alma_w": 14, "alma_h": 1755,
        "alainf_w": 600, "alainf_h": 50,
    },
    {
        "title": "PROPUESTA",
        "subtitle": "As = 791.2 cm² | canto = 1825 mm",
        "top_label": "500×32",
        "web_label": "1743×19",
        "bot_label": "600×50",
        "height_label": "1825 mm",
        "alasup_w": 500, "alasup_h": 32,
        "alma_w": 19, "alma_h": 1743,
        "alainf_w": 600, "alainf_h": 50,
    },
]

scale = 0.70
gap   = 1100

fig, ax = plt.subplots(figsize=(28, 14))
ax.set_aspect("equal")
ax.axis("off")

total_h_mm = 2000

for i, b in enumerate(beam_data):
    cx = i * gap
    has_plat = "plat_w" in b

    top_h = b["alasup_h"] * scale
    web_h = b["alma_h"]   * scale
    bot_h = b["alainf_h"] * scale
    total_beam_h = top_h + web_h + bot_h

    y_base    = (total_h_mm * scale - total_beam_h) / 2
    y_bot_top = y_base + bot_h
    y_web_top = y_bot_top + web_h
    y_top_top = y_web_top + top_h          # borde superior del ala superior

    # --- platabanda (detrás) ---
    if has_plat:
        y_plat = y_base - b["plat_h"] * scale
        ax.add_patch(Rectangle(
            (cx - b["plat_w"]/2, y_plat), b["plat_w"], b["plat_h"]*scale,
            facecolor="#D2691E", edgecolor="black", linewidth=0.8))

    # --- sección I ---
    ax.add_patch(Rectangle(
        (cx - b["alainf_w"]/2, y_base), b["alainf_w"], bot_h,
        facecolor="#4682B4", edgecolor="black", linewidth=0.8))

    ax.add_patch(Rectangle(
        (cx - b["alma_w"]/2, y_bot_top), b["alma_w"], web_h,
        facecolor="#F0F0F0", edgecolor="black", linewidth=0.8))

    ax.add_patch(Rectangle(
        (cx - b["alasup_w"]/2, y_web_top), b["alasup_w"], top_h,
        facecolor="#4682B4", edgecolor="black", linewidth=0.8))

    # --- etiquetas de dimensión (derecha) ---
    ax.text(cx + b["alasup_w"]/2 + 30, y_web_top + top_h/2,
            b["top_label"], va="center", ha="left",
            fontsize=22, fontweight="bold")

    ax.text(cx + b["alma_w"]/2 + 30, y_bot_top + web_h/2,
            b["web_label"], va="center", ha="left",
            fontsize=22, fontweight="bold")

    ax.text(cx + b["alainf_w"]/2 + 30, y_base + bot_h/2,
            b["bot_label"], va="center", ha="left",
            fontsize=22, fontweight="bold")

    if has_plat:
        ax.text(cx + b["plat_w"]/2 + 30,
                y_plat - 5,
                b["plat_label"], va="top", ha="left",
                fontsize=18, color="#8B4513", fontweight="bold")

    # --- cota vertical ---
    # La cota mide del BORDE SUPERIOR del ala superior al BORDE INFERIOR del ala inferior
    dim_x = cx - b["alasup_w"]/2 - 100
    ext_end = cx - b["alasup_w"]/2 - 10

    arr_top = y_top_top                # borde superior del ala superior
    arr_bot = y_base                   # borde inferior del ala inferior

    # líneas de extensión desde el borde de la sección hasta la cota
    ax.plot([ext_end, dim_x + 8], [arr_top, arr_top], color="black", lw=1.0)
    ax.plot([ext_end, dim_x + 8], [arr_bot, arr_bot], color="black", lw=1.0)

    # flecha doble
    ax.annotate("", xy=(dim_x, arr_top), xytext=(dim_x, arr_bot),
                arrowprops=dict(arrowstyle="<->", color="black", lw=1.4,
                                shrinkA=0, shrinkB=0))

    # texto de cota
    ax.text(dim_x - 18, (arr_top + arr_bot)/2,
            b["height_label"], rotation=90, va="center", ha="center",
            fontsize=20, fontweight="bold")

    # --- título ---
    ax.text(cx, y_top_top + 115, b["title"],
            ha="center", va="center", fontsize=24, fontweight="bold")
    ax.text(cx, y_top_top + 75, b["subtitle"],
            ha="center", va="center", fontsize=20)

ax.set_title(
    "Comparación de secciones metálicas — Puente Molinohuayco (corte C-C)",
    fontsize=28, fontweight="bold", pad=24)

ax.set_xlim(-1100, (len(beam_data)-1)*gap + 1100)
ax.set_ylim(-500, total_h_mm*scale + 400)

plt.tight_layout()
plt.savefig(
    "analisis_superestructura/documentos/vigas_principales/comparacion_secciones_vigas.png",
    dpi=180, bbox_inches="tight", facecolor="white")
plt.close()
print("OK")
