import io
import re
import os

import google.generativeai as genai
import pandas as pd
import streamlit as st

FIVE_TOOL_CHART = pd.DataFrame(
    data=[
        [78, 1, 2, 3, 4, 5, 6, 7, 8],
        [79, 1, 2, 3, 4, 5, 6, 7, 8],
        [80, 1, 2, 3, 4, 5, 6, 7, 8],
        [81, 1, 2, 3, 4, 5, 6, 7, 8],
        [82, 1, 2, 3, 4, 5, 6, 7, 8],
        [83, 2, 3, 4, 5, 6, 7, 8, 9],
        [84, 2, 3, 4, 5, 6, 7, 8, 9],
        [85, 2, 3, 4, 5, 6, 7, 8, 9],
        [86, 2, 3, 4, 5, 6, 7, 8, 9],
        [87, 2, 3, 4, 5, 6, 7, 8, 9],
        [88, 2, 4, 5, 6, 7, 8, 9, 11],
        [89, 2, 4, 5, 6, 7, 8, 10, 11],
        [90, 3, 4, 5, 6, 8, 9, 10, 12],
        [91, 3, 4, 5, 6, 8, 9, 10, 12],
        [92, 3, 4, 5, 6, 8, 9, 11, 12],
        [93, 3, 4, 5, 6, 8, 9, 11, 13],
        [94, 3, 4, 5, 6, 8, 9, 11, 13],
        [95, 3, 4, 6, 7, 9, 10, 12, 14],
        [96, 3, 4, 6, 7, 9, 10, 12, 14],
        [97, 3, 4, 6, 7, 9, 10, 12, 14],
        [98, 3, 5, 7, 8, 10, 11, 13, 15],
        [99, 3, 5, 7, 8, 10, 11, 13, 15],
        [100, 4, 5, 7, 8, 10, 12, 14, 16],
        [101, 4, 5, 7, 8, 10, 12, 14, 16],
        [102, 4, 5, 7, 8, 10, 12, 14, 16],
        [103, 4, 6, 7, 9, 11, 13, 15, 17],
        [104, 4, 6, 7, 9, 11, 13, 15, 17],
        [105, 4, 6, 8, 9, 11, 13, 15, 18],
        [106, 5, 7, 8, 10, 12, 14, 16, 18],
    ],
    columns=[
        "lowest_stat",
        "level_1",
        "level_2",
        "level_3",
        "level_4",
        "level_5",
        "level_6",
        "level_7",
        "level_8",
    ],
)


class CsvNotFoundError(IndexError):
    pass


def create_stat_table(img, model):
    prompt = (
        "Extract the text from this screenshot under the 'Grade Increase' box and the 'Basic Stats' box. "
        "Only the numbers in those boxes should be included, not the normal lineup stats or the final values. "
        "The column names should be ('category', 'con', 'pow', 'eye', 'spd', 'fld'). "
        "The values for the 'category' column should be ('grade_increase', 'basic'). "
        "If the values for basic stats include any parentheses with + or - in them, those should be included. "
        "However, the + signs in the grade increase row should not be included. "
        "Format it as a csv that could easily be copy and pasted into a text file and saved as a csv."
    )
    res = model.generate_content([prompt, {"mime_type": "image/png", "data": img}])
    try:
        pattern = r"```csv\n(.*?)```"
        table_contents = re.findall(pattern, res.text, re.DOTALL)[0]
    except IndexError:
        raise CsvNotFoundError

    return pd.read_csv(io.StringIO(table_contents)).astype(str)


def get_normal_value(val):
    if pd.isna(val):
        return None
    val = val.strip()
    # Match the format like '56(+3)' or '78(-4)'
    match = re.fullmatch(r"(\d+)\(([-+]\d+)\)", val)
    if match:
        outer, inner = match.groups()
        return int(outer) - int(inner)
    else:
        try:
            return int(val)
        except ValueError:
            # Don't apply function to non-int-like values
            return val


def get_adjusted_value(val):
    if pd.isna(val):
        return None
    val = val.strip()
    # Match the format like '56(+3)' or '78(-4)'
    match = re.fullmatch(r"(\d+)\(([-+]\d+)\)", val)
    if match:
        outer, inner = match.groups()
        return int(outer)
    else:
        try:
            return int(val)
        except ValueError:
            # Don't apply function to non-int-like values
            return val


def get_trains(stat_values: pd.Series, *, is_supreme: bool = False) -> pd.DataFrame:
    total_points = 3 * 29 if is_supreme else 3 * 19

    index = stat_values.index
    result_rows = []

    # Track how much was added to each stat
    added = pd.Series(0, index=index, dtype=int)
    current = stat_values.copy()

    while total_points > 0:
        min_val = current.min()
        min_indices = current[current == min_val].index
        num_min = len(min_indices)

        # If not enough points to raise all min values by 1, break
        if total_points < num_min:
            break

        # Add 1 point to each of the lowest-value categories
        for stat in min_indices:
            current[stat] += 1
            added[stat] += 1
        total_points -= num_min

        # After increasing, check if the minimum increased
        new_min = current.min()
        if new_min > min_val:
            row = added.copy()
            row["lowest_stat"] = new_min
            row["leftover_points"] = total_points
            result_rows.append(row)

    trains = pd.DataFrame(result_rows).reset_index(drop=True)
    return trains[
        trains.lowest_stat.between(
            FIVE_TOOL_CHART.lowest_stat.min(),
            FIVE_TOOL_CHART.lowest_stat.max(),
            inclusive="both",
        )
    ].reset_index(drop=True)


genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")

st.title('"Five Tool Player" Train Calculator')

st.markdown(
    (
        "Upload a screenshot of a players stat breakdown, making sure their base stats and GI are visible. "
        "Or, enter stats manually. "
        'This tool will calculate the necessary trains for various thresholds of "Five Tool Player".'
    )
)

is_supreme = st.toggle("Is player Supreme?", value=False)

use_manual_entry = st.toggle("Enter stats manually?", value=False)

if "stat_table" not in st.session_state:
    st.session_state.stat_table = None

if use_manual_entry:
    st.markdown("### Manual Stat Entry")

    # Default table values (can be adjusted or loaded from session state)
    default_manual_data = pd.DataFrame(
        {
            "con": [0, 0],
            "pow": [0, 0],
            "eye": [0, 0],
            "spd": [0, 0],
            "fld": [0, 0],
        },
        index=["Basic", "Grade Increase"],
    )

    edited_df = st.data_editor(
        default_manual_data,
        use_container_width=True,
        num_rows="fixed",
    )

    if st.button("Submit Manual Stats"):
        edited_df = edited_df.reset_index().rename(columns={"index": "category"})
        edited_df = edited_df.astype(str)  # match expected format for later parsing
        st.session_state.stat_table = edited_df

else:
    st.markdown("### Screenshot Based Stat Entry")
    file = st.file_uploader("Player Stats", accept_multiple_files=False)
    if file is not None:
        st.image(file.getvalue())

    if st.button("Process Stats"):
        if file:
            img = file.getvalue()
            try:
                st.session_state.stat_table = create_stat_table(img, model)
            except CsvNotFoundError:
                st.error(
                    f"Unable to read data from {file.name}, please enter stats manually."
                )
        else:
            st.warning("Please upload a file.")

stat_table = st.session_state.stat_table

if stat_table is not None:
    use_normal = st.toggle("Use adjusted stats?", value=False)
    map_fn = get_normal_value if use_normal else get_adjusted_value
    stat_values = stat_table.map(map_fn).drop(columns="category").sum()

    trains = get_trains(stat_values, is_supreme=is_supreme)
    target = st.selectbox(
        "Target Five Tool Value", sorted(trains.lowest_stat.tolist(), reverse=True)
    )
    st.markdown("### Train Values")
    st.dataframe(trains[trains.lowest_stat == target], hide_index=True)
