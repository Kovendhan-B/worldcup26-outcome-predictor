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
from src.flags import flag

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
            "data/fixtures/worldcup2026_fixtures.csv",
            upset_chance=0.15
        )

    st.success("Tournament Simulation Complete!")

    # ==============================
    # GROUP STAGE STANDINGS
    # ==============================

    st.header("📊 Group Stage Standings")

    groups = sorted(data["group_standings"].keys())

    for row_start in range(0, len(groups), 3):

        cols = st.columns(3)

        for i, col in enumerate(cols):

            idx = row_start + i

            if idx < len(groups):

                group = groups[idx]
                standings = data["group_standings"][group]

                with col:
                    st.subheader(f"Group {group}")

                    # Build HTML table with flags
                    html = (
                        '<table style="width:100%; '
                        'border-collapse:collapse; '
                        'font-size:14px;">'
                        '<tr style="border-bottom:2px solid #444;">'
                        '<th style="text-align:left; padding:6px;">Team</th>'
                        '<th style="padding:6px;">P</th>'
                        '<th style="padding:6px;">W</th>'
                        '<th style="padding:6px;">D</th>'
                        '<th style="padding:6px;">L</th>'
                        '<th style="padding:6px;">Pts</th>'
                        '</tr>'
                    )

                    for _, row in standings.iterrows():
                        html += (
                            '<tr style="border-bottom:1px solid #333;">'
                            f'<td style="text-align:left; padding:6px;">'
                            f'{flag(row["Team"])}</td>'
                            f'<td style="text-align:center; padding:6px;">'
                            f'{row["P"]}</td>'
                            f'<td style="text-align:center; padding:6px;">'
                            f'{row["W"]}</td>'
                            f'<td style="text-align:center; padding:6px;">'
                            f'{row["D"]}</td>'
                            f'<td style="text-align:center; padding:6px;">'
                            f'{row["L"]}</td>'
                            f'<td style="text-align:center; padding:6px; '
                            f'font-weight:bold;">'
                            f'{row["Pts"]}</td>'
                            '</tr>'
                        )

                    html += '</table>'

                    st.markdown(
                        html,
                        unsafe_allow_html=True
                    )

    # ==============================
    # QUALIFIED TEAMS
    # ==============================

    st.header("Qualified for Knockout Stage")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Group Winners")
        for g in sorted(data["group_winners"].keys()):
            st.markdown(
                f"**{g}**: {flag(data['group_winners'][g])}",
                unsafe_allow_html=True
            )

    with col2:
        st.subheader("Runners-up")
        for g in sorted(data["group_runners_up"].keys()):
            st.markdown(
                f"**{g}**: {flag(data['group_runners_up'][g])}",
                unsafe_allow_html=True
            )

    with col3:
        st.subheader("Best 3rd Place")
        for entry in data["best_thirds"]:
            st.markdown(
                f"**{entry['group']}**: "
                f"{flag(entry['team'])} "
                f"({entry['pts']} pts)",
                unsafe_allow_html=True
            )

    # ==============================
    # KNOCKOUT BRACKET
    # ==============================

    bracket = build_bracket(data)

    knockout_stages = [
        ("Round of 32", "Round of 32"),
        ("Round of 16", "Round of 16"),
        ("Quarterfinals", "Quarterfinal"),
        ("Semifinals", "Semifinal"),
        ("Final", "Final"),
    ]

    for display_name, stage_key in knockout_stages:

        st.header(display_name)

        matches = bracket[stage_key]

        num_cols = min(len(matches), 4)
        cols = st.columns(num_cols)

        for i, match in enumerate(matches):

            col = cols[i % num_cols]

            with col:

                is_winner_home = (
                    match["winner"] == match["home"]
                )

                home_label = (
                    f'<span style="color:#4CAF50; font-weight:bold;">'
                    f'{flag(match["home"])}</span>'
                    if is_winner_home
                    else f'<span style="opacity:0.6;">'
                    f'{flag(match["home"])}</span>'
                )

                away_label = (
                    f'<span style="color:#4CAF50; font-weight:bold;">'
                    f'{flag(match["away"])}</span>'
                    if not is_winner_home
                    else f'<span style="opacity:0.6;">'
                    f'{flag(match["away"])}</span>'
                )

                st.markdown(
                    f"{home_label} vs {away_label}",
                    unsafe_allow_html=True
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

    st.markdown(
        f"### 🏆 Predicted Champion: {flag(data['champion'])}",
        unsafe_allow_html=True
    )

    st.markdown(
        f"### 🥈 Runner-up: {flag(data['runner_up'])}",
        unsafe_allow_html=True
    )

    # ==============================
    # GROUP STAGE MATCH RESULTS
    # ==============================

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
                        f"{flag(match['winner'])} wins"
                    )

                st.markdown(
                    f"{flag(match['home_team'])} vs "
                    f"{flag(match['away_team'])} → "
                    f"*{result_text}*",
                    unsafe_allow_html=True
                )