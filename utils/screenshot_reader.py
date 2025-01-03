import numpy as np
from paddleocr import PaddleOCR
import pandas as pd
from PIL import Image

ocr = PaddleOCR(use_angle_cls=False, lang="en", show_log=False)


def read_image(file):
    img = Image.open(file)
    img = img.resize((2532, 1170))

    return img


def get_player_type(img):
    header_box = (290, 270, 2235, 310)
    header = img.crop(header_box)
    header_text = [text[1][0] for text in ocr.ocr(np.array(header), cls=False)[0]]

    if "IP" in header_text:
        return "pitcher"
    return "batter"


def get_row_bounds(start=0, end=7):
    row_height = 80
    rows = [400, 480, 560, 640, 720, 800, 880]
    row_bounds = [(start, start + row_height) for start in rows]

    return row_bounds[start:end]


def get_col_bounds(player_type):
    if player_type == "batter":
        cols = [
            (290, 350),
            (650, 120),
            (780, 150),
            (940, 170),
            (1120, 150),
            (1280, 150),
            (1450, 150),
            (1620, 160),
            (1800, 160),
            (1970, 150),
            (2120, 115),
        ]
    else:
        cols = [
            (290, 350),
            (690, 160),
            (890, 160),
            (1070, 160),
            (1240, 160),
            (1420, 150),
            (1590, 150),
            (1760, 150),
            (1930, 150),
            (2105, 135),
        ]
    col_bounds = [(start, start + end) for (start, end) in cols]

    return col_bounds


def get_cols(player_type):
    if player_type == "batter":
        cols = [
            "Player",
            "RISP",
            "H",
            "HR%",
            "AVG",
            "OBP",
            "SLG",
            "OPS",
            "R",
            "RBI",
            "SB",
        ]
    else:
        cols = [
            "Player",
            "W/L/SV",
            "IP",
            "ERA",
            "WHIP",
            "HR/9",
            "SO",
            "K/9",
            "B/9",
            "RA",
        ]

    return cols


def get_ovr_analysis_data(img, row_start=0, row_end=7):
    player_type = get_player_type(img)
    row_bounds = get_row_bounds()
    col_bounds = get_col_bounds(player_type)
    cols = get_cols(player_type)

    table_data = []
    for top, bottom in row_bounds:
        player_data = {}
        for (left, right), col in zip(col_bounds, cols):
            text = ocr.ocr(np.array(img.crop((left, top, right, bottom))), cls=False)[0]
            text = text[0][1][0] if text is not None else None
            player_data[col] = text
        table_data.append(player_data)

    ovr_analysis_data = pd.DataFrame.from_records(table_data)

    return ovr_analysis_data


def fix_batter_types(batter_data):
    batter_data = batter_data.astype(
        {
            "RISP": float,
            "H": "Int64",
            "HR%": float,
            "AVG": float,
            "OBP": float,
            "SLG": float,
            "OPS": float,
            "R": "Int64",
            "RBI": "Int64",
            "SB": "Int64",
        }
    )
    batter_data.Player = batter_data.Player.str.replace(" ", "")

    return batter_data


def fix_pitcher_types(pitcher_data):
    pitcher_data[["W", "L", "SV"]] = (
        pitcher_data["W/L/SV"].str.split("-").apply(pd.Series)
    )
    pitcher_data = pitcher_data[
        [
            "Player",
            "W",
            "L",
            "SV",
            "IP",
            "ERA",
            "WHIP",
            "HR/9",
            "SO",
            "K/9",
            "B/9",
            "RA",
        ]
    ]
    pitcher_data = pitcher_data.astype(
        {
            "W": "Int64",
            "L": "Int64",
            "SV": "Int64",
            "IP": float,
            "ERA": float,
            "WHIP": float,
            "HR/9": float,
            "SO": "Int64",
            "K/9": float,
            "B/9": float,
            "RA": "Int64",
        }
    )
    pitcher_data.Player = pitcher_data.Player.str.replace(" ", "")

    return pitcher_data
