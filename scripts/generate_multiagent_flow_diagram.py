# -*- coding: utf-8 -*-
"""Generate a PNG flow diagram (with branches + layer bands) of the AELON pipeline."""
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
PURPLE = (108, 60, 181)

FONTS_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "images" / "aelon-multiagent-flow-diagram.png"

WIDTH = 1040
BOX_W = 520
BOX_H = 78
GAP = 34
BRANCH_BOX_W = 220
BRANCH_BOX_H = 90
BRANCH_GAP = 24
BAND_PAD = 22
BAND_HEADER_H = 46
MARGIN_TOP = 70
MARGIN_BOTTOM = 40

# (label, sub_label_or_None, color)
TRUNK_1 = [
    ("Utilisateur", None, BLUE),
    ("Banking Chat", None, GOLD),
]
TRUNK_1B = [
    ("FastAPI", None, BLUE),
    ("Orchestrateur", None, GOLD),
]
BRANCH_A = [
    ("Privacy Agent", BLUE),
    ("Fraud Agent", GOLD),
    ("Sentiment Agent", BLUE),
    ("Retrieval Agent", GREEN),
]
TRUNK_2 = [
    ("Databricks Vector Search", "(aelon_vs_endpoint)", BLUE),
    ("Top 3 Chunks documentaires", "(Banque de France, FAQ, ACPR)", GOLD),
    ("Construction du contexte", None, BLUE),
    ("Prompt RAG", "Question + Contexte + Instructions", GOLD),
    ("GPT-4", "(Azure OpenAI)", BLUE),
    ("Reponse contextualisee", None, GREEN),
    ("Sources citees", None, GOLD),
]
TRUNK_3 = [
    ("gold_conversations", None, DARK),
]
BRANCH_B = [
    ("Analytics Dashboard", BLUE),
    ("Governance Dashboard", PURPLE),
    ("Evaluation Dashboard", GOLD),
]

# Band tints (light pastel backgrounds).
BAND_PRESENTATION = (225, 235, 250)
BAND_APPLICATIVE = (250, 240, 214)
BAND_IA = (232, 224, 246)
BAND_DATA = (222, 226, 232)
BAND_PILOTAGE = (222, 240, 230)


def load_font(name, size):
    try:
        return ImageFont.truetype(str(FONTS_DIR / name), size)
    except Exception:
        return ImageFont.load_default()


def text_color_for(bg):
    return WHITE if bg in (BLUE, GREEN, PURPLE, DARK) else DARK


def draw_box(draw, cx, top, width, height, label, sub_label, color, box_font, sub_font):
    left = cx - width / 2
    right = cx + width / 2
    bottom = top + height
    draw.rounded_rectangle([left, top, right, bottom], radius=14, fill=color)
    fg = text_color_for(color)
    if sub_label:
        draw.text((cx, top + height * 0.38), label, font=box_font, fill=fg, anchor="mm")
        draw.text((cx, top + height * 0.72), sub_label, font=sub_font, fill=fg, anchor="mm")
    else:
        draw.text((cx, top + height / 2), label, font=box_font, fill=fg, anchor="mm")
    return left, top, right, bottom


def arrow_down(draw, cx, y_from, y_to, color=GREY, width=4):
    draw.line([(cx, y_from), (cx, y_to - 10)], fill=color, width=width)
    head = 9
    draw.polygon([(cx - head, y_to - 10), (cx + head, y_to - 10), (cx, y_to)], fill=color)


def elbow_to(draw, x_from, y_from, x_to, y_to, color=GREY, width=3):
    mid_y = (y_from + y_to) / 2
    draw.line([(x_from, y_from), (x_from, mid_y)], fill=color, width=width)
    draw.line([(x_from, mid_y), (x_to, mid_y)], fill=color, width=width)
    draw.line([(x_to, mid_y), (x_to, y_to - 8)], fill=color, width=width)
    head = 8
    draw.polygon([(x_to - head, y_to - 8), (x_to + head, y_to - 8), (x_to, y_to)], fill=color)


def draw_band(draw, y_top, y_bottom, color, title, title_font):
    draw.rectangle([0, y_top, WIDTH, y_bottom], fill=color)
    tx = 34
    draw.text((tx, y_top + 20), title, font=title_font, fill=DARK, anchor="lm")
    draw.line([(tx, y_top + 40), (tx + 260, y_top + 40)], fill=GREY, width=2)


def build() -> Path:
    box_font = load_font("segoeuib.ttf", 18)
    sub_font = load_font("segoeui.ttf", 13)
    branch_font = load_font("segoeuib.ttf", 15)
    title_font = load_font("segoeuib.ttf", 28)
    band_font = load_font("segoeuib.ttf", 19)

    cx = WIDTH / 2

    # --- Layout (dry-run): compute every y-coordinate before drawing. ---
    y = MARGIN_TOP
    band_pres_top = y - BAND_PAD
    plan_trunk1 = []
    for label, sub, color in TRUNK_1:
        top = y
        bottom = top + BOX_H
        plan_trunk1.append((label, sub, color, top, bottom))
        y = bottom + GAP
    band_pres_bottom = plan_trunk1[-1][4] + BAND_PAD

    y = band_pres_bottom + BAND_PAD + BAND_HEADER_H
    band_app_top = y - BAND_PAD - BAND_HEADER_H
    plan_trunk1b = []
    for label, sub, color in TRUNK_1B:
        top = y
        bottom = top + BOX_H
        plan_trunk1b.append((label, sub, color, top, bottom))
        y = bottom + GAP
    band_app_bottom = plan_trunk1b[-1][4] + BAND_PAD

    # COUCHE IA: branch A (agents) + trunk2 (RAG + GPT steps).
    y = band_app_bottom + BAND_PAD + BAND_HEADER_H
    band_ia_top = y - BAND_PAD - BAND_HEADER_H
    branch_a_top = y
    n_a = len(BRANCH_A)
    row_w_a = n_a * BRANCH_BOX_W + (n_a - 1) * BRANCH_GAP
    start_x_a = cx - row_w_a / 2
    branch_a_centers = [start_x_a + i * (BRANCH_BOX_W + BRANCH_GAP) + BRANCH_BOX_W / 2 for i in range(n_a)]
    branch_a_bottom = branch_a_top + BRANCH_BOX_H
    retrieval_cx = branch_a_centers[-1]

    y = branch_a_bottom + 50
    plan_trunk2 = []
    for label, sub, color in TRUNK_2:
        top = y
        bottom = top + BOX_H
        plan_trunk2.append((label, sub, color, top, bottom))
        y = bottom + GAP
    band_ia_bottom = plan_trunk2[-1][4] + BAND_PAD

    # COUCHE DATA: gold_conversations.
    y = band_ia_bottom + BAND_PAD + BAND_HEADER_H
    band_data_top = y - BAND_PAD - BAND_HEADER_H
    label, sub, color = TRUNK_3[0]
    top = y
    bottom = top + BOX_H
    plan_trunk3 = [(label, sub, color, top, bottom)]
    band_data_bottom = bottom + BAND_PAD

    # COUCHE PILOTAGE: 3 dashboards.
    y = band_data_bottom + BAND_PAD + BAND_HEADER_H
    band_pilot_top = y - BAND_PAD - BAND_HEADER_H
    branch_b_top = y
    n_b = len(BRANCH_B)
    row_w_b = n_b * BRANCH_BOX_W + (n_b - 1) * BRANCH_GAP
    start_x_b = cx - row_w_b / 2
    branch_b_centers = [start_x_b + i * (BRANCH_BOX_W + BRANCH_GAP) + BRANCH_BOX_W / 2 for i in range(n_b)]
    branch_b_bottom = branch_b_top + BRANCH_BOX_H
    band_pilot_bottom = branch_b_bottom + BAND_PAD

    total_h = int(band_pilot_bottom + MARGIN_BOTTOM)

    # --- Render. ---
    img = Image.new("RGB", (WIDTH, total_h), BG)
    draw = ImageDraw.Draw(img)

    draw_band(draw, band_pres_top, band_pres_bottom, BAND_PRESENTATION, "COUCHE PRESENTATION", band_font)
    draw_band(draw, band_app_top, band_app_bottom, BAND_APPLICATIVE, "COUCHE APPLICATIVE", band_font)
    draw_band(draw, band_ia_top, band_ia_bottom, BAND_IA, "COUCHE IA", band_font)
    draw_band(draw, band_data_top, band_data_bottom, BAND_DATA, "COUCHE DATA", band_font)
    draw_band(draw, band_pilot_top, band_pilot_bottom, BAND_PILOTAGE, "COUCHE PILOTAGE", band_font)

    draw.text((cx, 30), "Architecture en couches - AELON", font=title_font, fill=DARK, anchor="mm")

    # Trunk 1 (Presentation).
    last_bottom = None
    for label, sub, color, top, bottom in plan_trunk1:
        if last_bottom is not None:
            arrow_down(draw, cx, last_bottom, top)
        draw_box(draw, cx, top, BOX_W, BOX_H, label, sub, color, box_font, sub_font)
        last_bottom = bottom

    # Trunk 1B (Applicative).
    for label, sub, color, top, bottom in plan_trunk1b:
        arrow_down(draw, cx, last_bottom, top)
        draw_box(draw, cx, top, BOX_W, BOX_H, label, sub, color, box_font, sub_font)
        last_bottom = bottom

    # Branch A (agents) under Orchestrateur.
    for i, (label, color) in enumerate(BRANCH_A):
        bx = branch_a_centers[i]
        elbow_to(draw, cx, last_bottom, bx, branch_a_top)
        draw_box(draw, bx, branch_a_top, BRANCH_BOX_W, BRANCH_BOX_H, label, None, color, branch_font, sub_font)

    # Trunk 2 (RAG + GPT), continued from Retrieval Agent.
    last_bottom = None
    for idx, (label, sub, color, top, bottom) in enumerate(plan_trunk2):
        if idx == 0:
            elbow_to(draw, retrieval_cx, branch_a_bottom, cx, top)
        else:
            arrow_down(draw, cx, last_bottom, top)
        draw_box(draw, cx, top, BOX_W, BOX_H, label, sub, color, box_font, sub_font)
        last_bottom = bottom

    # Trunk 3 (Data).
    for label, sub, color, top, bottom in plan_trunk3:
        arrow_down(draw, cx, last_bottom, top)
        draw_box(draw, cx, top, BOX_W, BOX_H, label, sub, color, box_font, sub_font)
        last_bottom = bottom

    # Branch B (dashboards) under gold_conversations.
    for i, (label, color) in enumerate(BRANCH_B):
        bx = branch_b_centers[i]
        elbow_to(draw, cx, last_bottom, bx, branch_b_top)
        draw_box(draw, bx, branch_b_top, BRANCH_BOX_W, BRANCH_BOX_H, label, None, color, branch_font, sub_font)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUTPUT_PATH)
    return OUTPUT_PATH


if __name__ == "__main__":
    out = build()
    print(f"Diagram generated: {out}")
