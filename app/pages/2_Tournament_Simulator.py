import sys
from pathlib import Path

import streamlit as st

# ----------------------------------
# Project Imports
# ----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.tournament import simulate_tournament
from src.bracket import build_bracket

# ----------------------------------
# Page Config
# ----------------------------------

st.set_page_config(
    page_title="Tournament Simulator - FIFA World Cup 2026",
    page_icon="🏆",
    layout="wide"
)

# ----------------------------------
# Title
# ----------------------------------

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

    # --------------------------
    # Knockout Bracket
    # --------------------------

    bracket = build_bracket(results)

    st.subheader("🏆 Knockout Bracket")

    for home, away, winner in bracket:

        st.markdown(
            f"""
            **{home}**
            
            vs
            
            **{away}**
            
            ➜ Winner: **{winner}**
            """
        )

    # --------------------------
    # Champion Prediction
    # --------------------------

    champion = results[-1]["winner"]

    st.success(
        f"🏆 Predicted Champion: {champion}"
    )