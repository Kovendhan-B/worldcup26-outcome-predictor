import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# ----------------------------------
# Project Imports
# ----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.predictor import predict_match
from src.team_profiles import TeamProfiles
from data.worldcup_teams import WORLD_CUP_2026_TEAMS

# ----------------------------------
# Page Config
# ----------------------------------

st.set_page_config(
    page_title="FIFA World Cup 2026 Predictor",
    page_icon="⚽",
    layout="wide"
)

# ----------------------------------
# Sidebar
# ----------------------------------

with st.sidebar:

    st.title("⚽ About")

    st.markdown(
        """
        ### FIFA World Cup 2026 Match Predictor

        **Model**
        - CatBoost Classifier

        **Features**
        - Historical Team Statistics
        - Recent Form (Last 5 Matches)
        - Head-to-Head Statistics
        - Elo Ratings
        - Tournament Features

        **Dataset**
        - International Football Results (2000–2025)

        **Performance**
        - Accuracy: ~56.5%
        - Balanced Draw Prediction
        """
    )

# ----------------------------------
# Load Teams
# ----------------------------------

profiles = TeamProfiles()

available_teams = set(
    profiles.df["home_team"]
).union(
    set(profiles.df["away_team"])
)

teams = sorted([
    team
    for team in WORLD_CUP_2026_TEAMS
    if team in available_teams
])

# ----------------------------------
# Banner
# ----------------------------------

BANNER_PATH = PROJECT_ROOT / "assets" / "banner.jpg"

if BANNER_PATH.exists():
    st.image(
        str(BANNER_PATH),
        use_container_width=True
    )

# ----------------------------------
# Title
# ----------------------------------

st.title("⚽ FIFA World Cup 2026 Match Predictor")

st.markdown(
    """
    Predict the outcome of international football matches
    using historical statistics, recent form, and Elo ratings.
    """
)

st.caption(
    f"Available Teams: {len(teams)}"
)


# ----------------------------------
# Team Selection
# ----------------------------------

col1, col2 = st.columns(2)

with col1:
    home_team = st.selectbox(
        "🏠 Home Team",
        teams
    )

with col2:
    away_team = st.selectbox(
        "✈️ Away Team",
        teams,
        index=min(1, len(teams) - 1)
    )

neutral = st.checkbox(
    "🏟️ Neutral Venue",
    value=True
)

# ----------------------------------
# Validation
# ----------------------------------

if home_team == away_team:
    st.error(
        "Please select two different teams."
    )
    st.stop()

# ----------------------------------
# Prediction
# ----------------------------------

if st.button("🔮 Predict Match Outcome"):

    try:

        result = predict_match(
            home_team,
            away_team,
            neutral
        )

        winner = max(
            result,
            key=result.get
        )

        winner_prob = result[winner]

        st.success(
            f"🏆 Predicted Outcome: {winner} ({winner_prob:.2f}%)"
        )

        st.divider()

        # --------------------------
        # Metrics
        # --------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "🏠 Home Win",
                f"{result['Home Win']:.2f}%"
            )

        with col2:
            st.metric(
                "🤝 Draw",
                f"{result['Draw']:.2f}%"
            )

        with col3:
            st.metric(
                "✈️ Away Win",
                f"{result['Away Win']:.2f}%"
            )

        # --------------------------
        # Probability Chart
        # --------------------------

        st.subheader(
            "📊 Match Outcome Probabilities"
        )

        chart_df = pd.DataFrame({
            "Outcome": [
                "Home Win",
                "Draw",
                "Away Win"
            ],
            "Probability": [
                result["Home Win"],
                result["Draw"],
                result["Away Win"]
            ]
        })

        st.bar_chart(
            chart_df.set_index("Outcome")
        )

        # --------------------------
        # Raw Values
        # --------------------------

        with st.expander(
            "View Raw Probabilities"
        ):
            st.json(result)

    except Exception as e:

        st.error(
            f"Prediction failed: {e}"
        )