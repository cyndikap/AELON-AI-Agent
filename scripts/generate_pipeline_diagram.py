# -*- coding: utf-8 -*-
"""Generate a PNG diagram of the AELON documentary pipeline (PDF -> RAG answer)."""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BLUE = (10, 61, 145)
GOLD = (212, 175, 55)
DARK = (27, 34, 51)
WHITE = (255, 255, 255)
GREY = (102, 112, 133)
BG = (245, 247, 250)
GREEN = (30, 122, 76)

FONTS_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "images" / "aelon-pipeline-documentaire.png"

WIDTH = 900
BOX_W = 700
BOX_H = 132
GAP = 46
MARGIN_TOP = 70
MARGIN_BOTTOM = 50

# (title, [description lines], color)
STEPS = [
    ("Document PDF", ["Reglementation, FAQ, procedure bancaire"], BLUE),
    ("Extraction du contenu", ["Conversion du document en texte exploitable",
                               "Suppression des elements inutiles"], GOLD),
    ("Chunking", ["Decoupage du document en plusieurs",
                  "segments de taille adaptee au RAG"], BLUE),
    ("Generation des Embeddings", ["Transformation de chaque chunk en vecteur",
                                    "a l'aide du modele databricks-gte-large-en"], GOLD),
    ("Databricks Vector Search", ["Indexation des vecteurs et recherche",
                                  "des documents les plus pertinents"], BLUE),
    ("Moteur RAG", ["Construction du contexte documentaire",
                     "et generation de la reponse"], GOLD),
    ("Reponse Contextualisee", ["Reponse fondee sur les documents",
                                 "les plus pertinents retrouves"], GREEN),
]


def load_font(name, size):
    try:
        return ImageFont.truetype(str(FONTS_DIR / name), size)
    except Exception:
        return ImageFont.load_default()


def text_color_for(bg):
    return WHITE if bg in (BLUE, GREEN) else DARK


def build() -> Path:
    n = len(STEPS)
    height = MARGIN_TOP + n * BOX_H + (n - 1) * GAP + MARGIN_BOTTOM

    img = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)

    title_font = load_font("segoeuib.ttf", 28)
    box_title_font = load_font("segoeuib.ttf", 19)
    desc_font = load_font("segoeui.ttf", 14)

    cx = WIDTH / 2
    draw.text((cx, 30), "Pipeline documentaire AELON", font=title_font, fill=DARK, anchor="mm")

    x = (WIDTH - BOX_W) / 2
    y = MARGIN_TOP
    centers = []
    for title, desc_lines, color in STEPS:
        fg = text_color_for(color)
        draw.rounded_rectangle([x, y, x + BOX_W, y + BOX_H], radius=16, fill=color)

        n_desc = len(desc_lines)
        title_y = y + (28 if n_desc else BOX_H / 2)
        draw.text((cx, title_y), title, font=box_title_font, fill=fg, anchor="mm")

        desc_start_y = y + 66
        line_gap = 24
        for i, line in enumerate(desc_lines):
            draw.text((cx, desc_start_y + i * line_gap), line, font=desc_font, fill=fg, anchor="mm")

        centers.append((cx, y, y + BOX_H))
        y += BOX_H + GAP

    for i in range(n - 1):
        _, _, bottom = centers[i]
        _, top_next, _ = centers[i + 1]
        arrow_top = bottom + 4
        arrow_bottom = top_next - 4
        draw.line([(cx, arrow_top), (cx, arrow_bottom)], fill=GREY, width=4)
        head = 10
        draw.polygon([
            (cx - head, arrow_bottom - head),
            (cx + head, arrow_bottom - head),
            (cx, arrow_bottom),
        ], fill=GREY)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUTPUT_PATH)
    return OUTPUT_PATH


if __name__ == "__main__":
    out = build()
    print(f"Diagram generated: {out}")
