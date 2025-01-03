import numpy as np
import pandas as pd
import streamlit as st
from paddleocr import PaddleOCR
from stqdm import stqdm

from utils.screenshot_reader import read_image

ocr = PaddleOCR(use_angle_cls=False, lang="en", show_log=False)


def get_player_type(img):
    player_types = ["batter", "pitcher"]
    boxes = [(1610, 170, 1930, 250), (1940, 170, 2250, 250)]
    avg_colors = [np.array(img.crop(box)).mean() for box in boxes]
    player_type = player_types[np.argmax(avg_colors)]
    return player_type


def get_cols(img):
    box = (870, 270, 2240, 315)
    cols = img.crop(box)
    return [
        col[1][0] for col in ocr.ocr(np.array(cols), cls=False)[0] if col[1][0] != "V"
    ]


def get_stats(img):
    stats = img.crop((400, 400, 2240, 970))
    return [stat[1][0] for stat in ocr.ocr(np.array(stats), cls=False)[0]]


def create_stat_table(img):
    cols = ["Player"] + get_cols(img)
    stats = get_stats(img)
    stats = np.array(stats).reshape(-1, len(cols))
    return pd.DataFrame(stats, columns=cols)


def fix_pitcher_types(stats):
    type_map = {
        "ERA": float,
        "WHIP": float,
        "IP": float,
        "OPS": float,
        "K/9": float,
        "BB/9": float,
        "HR/9": float,
        "K/BB": float,
        "W": "Int64",
        "SV": "Int64",
        "HLD": "Int64",
        "L": "Int64",
        "AVG": float,
        "OBP": float,
        "SLG": float,
        "QS": "Int64",
        "3B": "Int64",
        "HR": "Int64",
        "R": "Int64",
        "BB": "Int64",
        "G": "Int64",
        "SO": "Int64",
        "2B": "Int64",
        "H": "Int64",
    }
    type_map = {key: val for (key, val) in type_map.items() if key in stats.columns}
    stats = stats.astype(type_map)
    stats.Player = stats.Player.str.replace(" ", "")
    return stats


def fix_batter_types(stats):
    type_map = {
        "OPS": float,
        "HR%": float,
        "OBP": float,
        "SLG": float,
        "BABIP": float,
        "BB/K": float,
        "HR": "Int64",
        "RISP": float,
        "G": "Int64",
        "H": "Int64",
        "2B": "Int64",
        "RBI": "Int64",
        "SO": "Int64",
        "BB": "Int64",
        "3B": "Int64",
        "AVG": "Int64",
        "SB": "Int64",
        "SB%": "Int64",
        "GIDP": "Int64",
        "HSP": "Int64",
        "R": "Int64",
        "ISOD": float,
        "ISOP": float,
        "AB": "Int64",
    }
    type_map = {key: val for (key, val) in type_map.items() if key in stats.columns}
    stats = stats.astype(type_map)
    stats.Player = stats.Player.str.replace(" ", "")
    return stats


st.title("Ranked Stats")
st.markdown(
    "Upload screenshots from Ranked stats and this tool will aggregate the data into a single table."
)
st.warning(
    "This has only been tested with screenshots from an iPhone 13. Screenshots from other devices may or may not be compatible."
)

files = st.file_uploader("Ranked Stats Screenshots", accept_multiple_files=True)

pitcher_data = pd.DataFrame()
batter_data = pd.DataFrame()

process_screenshots = st.button("Process Screenshots")
if process_screenshots:
    for file in stqdm(files):
        img = read_image(file)
        stat_table = create_stat_table(img)
        player_type = get_player_type(img)

        if player_type == "batter":
            batter_data = pd.concat((batter_data, stat_table), ignore_index=True)
            batter_data = batter_data.drop_duplicates()
        else:
            pitcher_data = pd.concat((pitcher_data, stat_table), ignore_index=True)
            pitcher_data = pitcher_data.drop_duplicates()

if len(pitcher_data):
    pitcher_data = fix_pitcher_types(pitcher_data)
    st.header("Pitcher Data")
    pitcher_data

if len(batter_data):
    batter_data = fix_batter_types(batter_data)
    st.header("Batter Data")
    batter_data

if len(pitcher_data):
    st.header("Average Pitcher Stats")
    avg_pitcher_stats = (
        pitcher_data.groupby("Player").mean().sort_values("ERA", ascending=True)
    )
    avg_pitcher_stats

if len(batter_data):
    st.header("Average Batter Stats")
    avg_batter_stats = (
        batter_data.groupby("Player").mean().sort_values("OPS", ascending=False)
    )
    avg_batter_stats
