"""Convert screenshots of player stats into a table."""

import io
import re
import os
from typing import Literal

import google.generativeai as genai
import pandas as pd
import streamlit as st
from stqdm import stqdm


PlayerType = Literal["batter", "pitcher"]


class CsvNotFoundError(IndexError):
    pass


def create_stat_table(img, model):
    prompt = (
        "Extract the text from the table in this screenshot. Format it as a csv that could easily be copy and pasted "
        'into a text file and saved as a csv. Exclude the row that beings with "TEAM RECORD". Exclude the "Rank" '
        "column if it exists."
    )
    res = model.generate_content([prompt, {"mime_type": "image/png", "data": img}])
    try:
        pattern = r"```csv\n(.*?)```"
        table_contents = re.findall(pattern, res.text, re.DOTALL)[0]
    except IndexError:
        raise CsvNotFoundError

    stats = pd.read_csv(io.StringIO(table_contents))
    stats.columns = stats.columns.str.replace(" ", "")
    stats.Players = stats.Players.str.replace(" ", "")
    return stats


def get_player_type(stats: pd.DataFrame) -> PlayerType:
    pitcher_cols = [
        "ERA",
        "WHIP",
        "IP",
        "K/9",
        "BB/9",
        "HR/9",
        "K/BB",
        "W",
        "SV",
        "HLD",
        "L",
        "QS",
        "RA",
    ]
    for col in stats.columns:
        if col in pitcher_cols:
            return "pitcher"
    return "batter"


genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")


st.title("Stats Parser")
st.markdown(
    (
        "Upload screenshots from Ranked stats or OVR Analysis stats and this tool will aggregate the data into a single"
        " table."
    )
)

files = st.file_uploader("Stats Screenshots", accept_multiple_files=True)

pitcher_data = pd.DataFrame()
batter_data = pd.DataFrame()

process_screenshots = st.button("Process Screenshots")
if process_screenshots:
    for file in stqdm(files):
        img = file.getvalue()
        try:
            stat_table = create_stat_table(img, model)
        except CsvNotFoundError:
            st.error(f"Unable to read data from {file}")
            continue

        player_type = get_player_type(stat_table)

        if player_type == "batter":
            batter_data = pd.concat((batter_data, stat_table), ignore_index=True)
            batter_data = batter_data.drop_duplicates()
        else:
            pitcher_data = pd.concat((pitcher_data, stat_table), ignore_index=True)
            pitcher_data = pitcher_data.drop_duplicates()

if len(pitcher_data):
    st.header("Pitcher Data")
    pitcher_data

if len(batter_data):
    st.header("Batter Data")
    batter_data

if len(pitcher_data):
    st.header("Average Pitcher Stats")
    avg_pitcher_stats = pitcher_data.groupby("Players").mean()
    avg_pitcher_stats

if len(batter_data):
    st.header("Average Batter Stats")
    avg_batter_stats = batter_data.groupby("Players").mean()
    avg_batter_stats
