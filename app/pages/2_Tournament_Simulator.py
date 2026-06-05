import sys
from pathlib import Path

import streamlit as st

# ----------------------------------
# Project Imports
# ----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.tournament import simulate_full_tournament
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

st.markdown(
    """
    Simulate the entire FIFA World Cup 2026 —
    from group stage through the knockout rounds
    to the final.
    """
)

if st.button("⚡ Start Tournament"):

    with st.spinner("Simulating tournament..."):

        data = simulate_full_tournament(
            "data/fixtures/worldcup2026_fixtures.csv"
        )

    st.success("Tournament Simulation Complete!")

    # ==============================
    # GROUP STAGE STANDINGS
    # ==============================

    st.header("📊 Group Stage Standings")

    groups = sorted(data["group_standings"].keys())

    # Display groups in rows of 3
    for row_start in range(0, len(groups), 3):

        cols = st.columns(3)

        for i, col in enumerate(cols):

            idx = row_start + i

            if idx < len(groups):

                group = groups[idx]
                standings = data["group_standings"][group]

                with col:
                    st.subheader(f"Group {group}")
                    st.dataframe(
                        standings[["Team", "P", "W", "D", "L", "Pts"]],
                        width="stretch",
                        hide_index=True
                    )

    # ==============================
    # QUALIFIED TEAMS
    # ==============================

    st.header("✅ Qualified for Knockout Stage")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🥇 Group Winners")
        for g in sorted(data["group_winners"].keys()):
            st.write(
                f"**{g}**: {data['group_winners'][g]}"
            )

    with col2:
        st.subheader("🥈 Runners-up")
        for g in sorted(data["group_runners_up"].keys()):
            st.write(
                f"**{g}**: {data['group_runners_up'][g]}"
            )

    with col3:
        st.subheader("🎯 Best 3rd Place")
        for entry in data["best_thirds"]:
            st.write(
                f"**{entry['group']}**: "
                f"{entry['team']} "
                f"({entry['pts']} pts)"
            )

    # ==============================
    # KNOCKOUT BRACKET
    # ==============================

    bracket = build_bracket(data)

    knockout_stages = [
        ("🏟️ Round of 32", "Round of 32"),
        ("⚔️ Round of 16", "Round of 16"),
        ("🔥 Quarterfinals", "Quarterfinal"),
        ("💥 Semifinals", "Semifinal"),
        ("🏆 Final", "Final"),
    ]

    for display_name, stage_key in knockout_stages:

        st.header(display_name)

        matches = bracket[stage_key]

        # Use columns for compact display
        num_cols = min(len(matches), 4)
        cols = st.columns(num_cols)

        for i, match in enumerate(matches):

            col = cols[i % num_cols]

            with col:

                is_winner_home = (
                    match["winner"] == match["home"]
                )

                home_label = (
                    f"✅ **{match['home']}**"
                    if is_winner_home
                    else match["home"]
                )

                away_label = (
                    f"✅ **{match['away']}**"
                    if not is_winner_home
                    else match["away"]
                )

                st.markdown(
                    f"{home_label} vs {away_label}"
                )

                st.caption(
                    f"H: {match['probabilities']['Home Win']:.1f}% · "
                    f"D: {match['probabilities']['Draw']:.1f}% · "
                    f"A: {match['probabilities']['Away Win']:.1f}%"
                )

                st.divider()

    # ==============================
    # CHAMPION
    # ==============================

    st.header("")

    st.success(
        f"🏆 Predicted Champion: {data['champion']}"
    )

    st.info(
        f"🥈 Runner-up: {data['runner_up']}"
    )

    st.header("📋 Group Stage Match Results")

    for group in sorted(data["group_standings"].keys()):

        group_matches = [
            m for m in data["group_results"]
            if m["group"] == group
        ]

        with st.expander(f"Group {group}"):

            for match in group_matches:

                if match["winner"] == "Draw":
                    result_text = "🤝 Draw"
                else:
                    result_text = (
                        f"✅ {match['winner']} wins"
                    )

                st.markdown(
                    f"{match['home_team']} vs "
                    f"{match['away_team']} → "
                    f"*{result_text}*"
                )