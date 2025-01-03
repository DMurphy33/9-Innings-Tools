import streamlit as st


st.title("9 Innings Tools")

pages = st.navigation(
    [
        st.Page("tools/ranked_stats.py", title="Ranked Stats", url_path="ranked_stats"),
        st.Page("tools/ovr_analysis.py", title="OVR Analysis", url_path="ovr_analysis"),
        st.Page(
            "tools/ticket_probs.py",
            title="Blue/Green Success Chances",
            url_path="blue_green_chances",
        ),
    ]
)

pages.run()
