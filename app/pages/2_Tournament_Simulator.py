import streamlit as st

from src.tournament import simulate_tournament

st.title("🏆 Tournament Simulator")

mode = st.radio(
    "Simulation Mode",
    [
        "Automatic AI Prediction",
        "Step-by-Step Prediction"
    ]
)

if st.button("Start Tournament"):

    results = simulate_tournament(
        "data/fixtures/worldcup2026_fixtures.csv"
    )

    st.success(
        "Tournament Simulation Complete"
    )

    for match in results:

        with st.expander(
            f"{match['home_team']} vs {match['away_team']}"
        ):

            st.write(
                f"Winner: {match['winner']}"
            )

            st.json(
                match["probabilities"]
            )