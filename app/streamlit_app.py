import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ----------------------------------
# Project Imports
# ----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.predictor import predict_match
from src.team_profiles import TeamProfiles
from src.flags import flag, flag_label
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

@st.cache_resource
def load_team_profiles():
    return TeamProfiles()

@st.cache_data
def get_available_teams():
    p = load_team_profiles()
    available = set(
        p.df["home_team"]
    ).union(
        set(p.df["away_team"])
    )
    return sorted([
        team
        for team in WORLD_CUP_2026_TEAMS
        if team in available
    ])

profiles = load_team_profiles()
teams = get_available_teams()

# ----------------------------------
# Banner
# ----------------------------------

BANNER_PATH = PROJECT_ROOT / "assets" / "banner.png"

if BANNER_PATH.exists():
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.image(
            str(BANNER_PATH),
            width="stretch"
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
        teams,
        format_func=flag_label
    )

with col2:
    away_team = st.selectbox(
        "✈️ Away Team",
        teams,
        index=min(1, len(teams) - 1),
        format_func=flag_label
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

@st.cache_data
def cached_predict(h_team, a_team, is_neutral):
    return predict_match(h_team, a_team, is_neutral)

if st.button("🔮 Predict Match Outcome"):

    try:

        result = cached_predict(
            home_team,
            away_team,
            neutral
        )

        winner = max(
            result,
            key=result.get
        )

        winner_prob = result[winner]

        with st.container(border=True):
            st.markdown(
                f"<h2 style='text-align: center; color: #1E88E5;'>🏆 {winner}</h2>"
                f"<p style='text-align: center; font-size: 1.2rem; color: #555;'>Predicted Outcome ({winner_prob:.2f}%)</p>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<h4 style='text-align: center;'>{flag(home_team)} {home_team} <span style='color:#888;'>vs</span> {away_team} {flag(away_team)}</h4>",
                unsafe_allow_html=True
            )

            st.divider()

            # --------------------------
            # Metrics
            # --------------------------
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"🏠 {home_team}", f"{result['Home Win']:.2f}%")
            with col2:
                st.metric("🤝 Draw", f"{result['Draw']:.2f}%")
            with col3:
                st.metric(f"✈️ {away_team}", f"{result['Away Win']:.2f}%")

            # --------------------------
            # Probability Chart
            # --------------------------
            st.markdown("<br>", unsafe_allow_html=True)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[result['Home Win']], y=[''], orientation='h',
                name=f"{home_team} Win", marker=dict(color='#1E88E5', line=dict(width=1, color='rgba(0,0,0,0.1)')),
                text=f"{result['Home Win']:.1f}%", textposition='auto'
            ))
            fig.add_trace(go.Bar(
                x=[result['Draw']], y=[''], orientation='h',
                name="Draw", marker=dict(color='#B0BEC5', line=dict(width=1, color='rgba(0,0,0,0.1)')),
                text=f"{result['Draw']:.1f}%", textposition='auto'
            ))
            fig.add_trace(go.Bar(
                x=[result['Away Win']], y=[''], orientation='h',
                name=f"{away_team} Win", marker=dict(color='#FF8A65', line=dict(width=1, color='rgba(0,0,0,0.1)')),
                text=f"{result['Away Win']:.1f}%", textposition='auto'
            ))
            
            fig.update_layout(
                barmode='stack',
                height=150,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, 100]),
                yaxis=dict(showgrid=False, zeroline=False, visible=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                    font=dict(size=12)
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)

        # --------------------------
        # Raw Values
        # --------------------------
        with st.expander("View Raw Probabilities"):
            st.json(result)

    except Exception as e:

        st.error(
            f"Prediction failed: {e}"
        )