# -*- coding: utf-8 -*-
"""Generate a PNG flow diagram of the AELON request pipeline."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BLUE = (10, 61, 145)
GOLD = (212, 175, 55)
DARK = (27, 34, 51)
WHITE = (255, 255, 255)
GREY = (102, 112, 133)
BG = (245, 247, 250)
GREEN = (30, 122, 76)

STEPS = [
    "Utilisateur",
    "FastAPI",
    "Orchestrator",
    "Privacy / Sentiment / Fraud",
    "Retrieval Agent",
    "Embeddings",
    "Databricks Vector Search",
    "Top 3 Chunks",
    "Contexte RAG",
    "GPT-4",
    "Humanization",
    "Compliance",
    "Reponse",
]

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "images" / "aelon-flow-diagram.png"

BOX_W, BOX_H = 460, 80
GAP = 34
MARGIN_TOP = 60
MARGIN_BOTTOM = 60
WIDTH = 900


def load_font(size, bold=False):
    candidates = ["segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def build() -> Path:
    n = len(STEPS)
    height = MARGIN_TOP + n * BOX_H + (n - 1) * GAP + MARGIN_BOTTOM

    img = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)

    title_font = load_font(30, bold=True)
    box_font = load_font(20, bold=True)

    draw.text((WIDTH / 2, 26), "Parcours d'une requete utilisateur - AELON",
              font=title_font, fill=DARK, anchor="mm")

    x = (WIDTH - BOX_W) / 2
    y = MARGIN_TOP
    centers = []
    for i, step in enumerate(STEPS):
        color = GREEN if i == n - 1 else (BLUE if i % 2 == 0 else GOLD)
        text_color = WHITE if color in (BLUE, GREEN) else DARK

        draw.rounded_rectangle(
            [x, y, x + BOX_W, y + BOX_H], radius=16, fill=color
        )
        draw.text((x + BOX_W / 2, y + BOX_H / 2), step,
                  font=box_font, fill=text_color, anchor="mm")

        centers.append((x + BOX_W / 2, y, y + BOX_H))
        y += BOX_H + GAP

    # Arrows between consecutive boxes.
    for i in range(n - 1):
        cx, _, bottom = centers[i]
        _, top_next, _ = centers[i + 1]
        arrow_top = bottom + 4
        arrow_bottom = top_next - 4
        draw.line([(cx, arrow_top), (cx, arrow_bottom)], fill=GREY, width=4)
        # Arrow head
        head_size = 10
        draw.polygon([
            (cx - head_size, arrow_bottom - head_size),
            (cx + head_size, arrow_bottom - head_size),
            (cx, arrow_bottom),
        ], fill=GREY)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUTPUT_PATH)
    return OUTPUT_PATH


if __name__ == "__main__":
    out = build()
    print(f"Diagram generated: {out}")
