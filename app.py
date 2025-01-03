import streamlit as st


st.title("9 Innings Tools")

pages = st.navigation(
    [
        st.Page("tools/ovr_analysis.py", title="OVR Analysis"),
        st.Page("tools/ticket_probs.py", title="Blue/Green Success Chances"),
    ]
)

pages.run()
