import streamlit as st


st.title("9 Innings Tools")

pages = st.navigation(
    [
        st.Page(
            "tools/stats_parser.py",
            title="Stats Parser",
            url_path="stats",
        ),
        st.Page(
            "tools/ticket_probs.py",
            title="Blue/Green Success Chances",
            url_path="blue_green_chances",
        ),
        st.Page(
            "tools/five_tool.py",
            title='"Five Tool Player" Train Calculator',
            url_path="five_tool",
        ),
    ]
)

pages.run()
