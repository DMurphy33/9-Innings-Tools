import pandas as pd
import streamlit as st
from stqdm import stqdm

from utils.screenshot_reader import (
    fix_batter_types,
    fix_pitcher_types,
    get_player_type,
    get_ovr_analysis_data,
    read_image,
)

st.title("OVR Analysis")
st.markdown(
    "Upload screenshots from OVR Analysis stats and this tool will aggregate the data into a single table."
)
st.warning(
    "This has only been tested with screenshots from an iPhone 13. Screenshots from other devices may or may not be compatible."
)

files = st.file_uploader("OVR Analysis Screenshots", accept_multiple_files=True)

pitcher_data = pd.DataFrame()
batter_data = pd.DataFrame()

process_screenshots = st.button("Process Screenshots")
if process_screenshots:
    for file in stqdm(files):
        img = read_image(file)
        data = get_ovr_analysis_data(img)
        player_type = get_player_type(img)

        if player_type == "batter":
            batter_data = pd.concat((batter_data, data))
            batter_data = batter_data.drop_duplicates()
        else:
            pitcher_data = pd.concat((pitcher_data, data))
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
