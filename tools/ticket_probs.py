import numpy as np
import scipy.stats as stats
import streamlit as st

st.title("Blue/Green Success Chances")

st.markdown(
    "Find out how likely you are to have a successful green or blue given the skills you are looking for and how many tickets you have."
)

form = st.container(border=True)

player_type = form.radio("Player Type", ["Pitcher", "Batter"])

if player_type == "Pitcher":
    skills = [
        "Finesse Pitcher",
        "Dominant Pitcher",
        "The Last Boss",
        "Cleaning Up Your Mess",
        "The Untouchable",
        "Groundballer",
        "Iron Will",
        "Ace",
        "Elite Closer",
        "Giant Crusher",
        "Inning Eater",
        "Putaway Pitch",
        "3-4-5 Specialist",
        "Control Artist",
        "Field Commander",
        "Firefighter",
        "Fixer",
        "Golden Pitcher",
        "Pace Controller",
        "Pitching Machine",
        "Power Pitcher",
        "Stability",
        "The Setup Man",
        "Warmed Up",
        "Winning Streak",
        "Breaking Ball Mastery",
        "Calm Mind",
        "Danger Zone",
        "Fearless",
        "Lefty Specialist",
        "Lightning Pitch",
        "Pickoff King",
        "Righty Specialist",
        "Seasoned Pitcher",
        "Strong Mentality",
        "Strong Stamina",
        "Thin Ice",
    ]

else:
    skills = [
        "Charisma",
        "Barrel It Up",
        "5-Tool Player",
        "Spotlight",
        "Prediction",
        "Strengthen the Strength",
        "Batting Machine",
        "Slugger Instinct",
        "Laser Beam" "Ace Specialist",
        "Master Base Thief",
        "Super Sub",
        "Endurance",
        "Exhaustion",
        "Flashing the Leather",
        "Full Swing Hitter",
        "Heavy Hitter",
        "It Ain't Over Yet",
        "Leg Day",
        "Overcome Weakness",
        "Pinpoint Strike",
        "Professional",
        "Reliable",
        "Table Setter",
        "Training Junkie",
        "Concentration",
        "Fastball Crusher",
        "Fielding Specialist",
        "Going for the First Pitch",
        "Hawk Eye",
        "Head On",
        "Lefty Specialist",
        "Pinch Hit Specialist",
        "Pull Hit",
        "Push Hit",
        "RBI Machine",
        "Righty Specialist",
    ]

desired_skills = form.multiselect("Desired Skills", skills)

ticket_type = form.radio("Ticket Type", ["Green", "Blue"])
num_tickets = form.number_input(f"Number of {ticket_type}s", min_value=1)

submitted = form.button("Find Success Chances")

if submitted:
    if not len(desired_skills):
        st.warning("Please select at least 1 desired skill")
    else:
        if ticket_type == "Green":
            p_successful_ticket = 1 - (
                ((len(skills) - len(desired_skills)) / len(skills))
                * ((len(skills) - len(desired_skills) - 1) / len(skills))
            )
        else:
            p_successful_ticket = len(desired_skills) / (len(skills) - 1)

        dist = stats.geom(p_successful_ticket)
        p_success = dist.cdf(num_tickets) * 100
        avg_tickets_required = int(np.ceil(dist.mean()))
        tickets_for_95_pct = int(np.ceil(dist.ppf(0.95)))

        st.text(
            f"""You have a {p_success:.2f}% chance of landing a desired skill with {num_tickets} {ticket_type}s.
            On average, it will take {avg_tickets_required} {ticket_type}s.
            For a 95% chance of success, you would need {tickets_for_95_pct} {ticket_type}s.
            """
        )
