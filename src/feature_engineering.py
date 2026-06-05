import pandas as pd


def build_match_features(
    home,
    away,
    neutral=True,
    tournament="world_cup"
):

    row = {}

    row["neutral"] = int(neutral)

    row["year"] = 2026
    row["month"] = 6

    # Base stats

    base_features = [
        "matches_played",
        "win_rate",
        "draw_rate",
        "loss_rate",
        "avg_goals_scored",
        "avg_goals_conceded",
        "last5_win_rate",
        "last5_avg_goals_scored",
        "last5_avg_goals_conceded",
        "elo"
    ]

    for feature in base_features:

        row[f"home_{feature}"] = home[f"home_{feature}"]

        corresponding_away = (
            feature
            if feature == "elo"
            else feature
        )

        if f"away_{feature}" in away.index:
            row[f"away_{feature}"] = away[f"away_{feature}"]
        else:
            row[f"away_{feature}"] = away[f"home_{feature}"]

    # Elo

    row["home_elo"] = home["home_elo"]
    row["away_elo"] = away["away_elo"]

    row["elo_diff"] = (
        row["home_elo"]
        - row["away_elo"]
    )

    # Differences

    row["win_rate_diff"] = (
        row["home_win_rate"]
        - row["away_win_rate"]
    )

    row["draw_rate_diff"] = (
        row["home_draw_rate"]
        - row["away_draw_rate"]
    )

    row["loss_rate_diff"] = (
        row["home_loss_rate"]
        - row["away_loss_rate"]
    )

    row["goals_scored_diff"] = (
        row["home_avg_goals_scored"]
        - row["away_avg_goals_scored"]
    )

    row["goals_conceded_diff"] = (
        row["home_avg_goals_conceded"]
        - row["away_avg_goals_conceded"]
    )

    row["matches_played_diff"] = (
        row["home_matches_played"]
        - row["away_matches_played"]
    )

    row["last5_win_rate_diff"] = (
        row["home_last5_win_rate"]
        - row["away_last5_win_rate"]
    )

    row["last5_goals_scored_diff"] = (
        row["home_last5_avg_goals_scored"]
        - row["away_last5_avg_goals_scored"]
    )

    row["last5_goals_conceded_diff"] = (
        row["home_last5_avg_goals_conceded"]
        - row["away_last5_avg_goals_conceded"]
    )

    # Goal Balance

    row["home_goal_balance"] = (
        row["home_avg_goals_scored"]
        - row["home_avg_goals_conceded"]
    )

    row["away_goal_balance"] = (
        row["away_avg_goals_scored"]
        - row["away_avg_goals_conceded"]
    )

    row["goal_balance_diff"] = (
        row["home_goal_balance"]
        - row["away_goal_balance"]
    )

    # Absolute features

    row["abs_win_rate_diff"] = abs(
        row["win_rate_diff"]
    )

    row["abs_last5_diff"] = abs(
        row["last5_win_rate_diff"]
    )

    row["abs_goals_scored_diff"] = abs(
        row["goals_scored_diff"]
    )

    row["abs_goals_conceded_diff"] = abs(
        row["goals_conceded_diff"]
    )

    row["strength_gap"] = (
        abs(row["win_rate_diff"])
        + abs(row["last5_win_rate_diff"])
    )

    # H2H placeholders

    row["h2h_matches"] = 0
    row["h2h_home_win_rate"] = 0
    row["h2h_away_win_rate"] = 0
    row["h2h_draw_rate"] = 0
    row["h2h_win_rate_diff"] = 0
    row["abs_h2h_diff"] = 0

    # Tournament

    tournaments = [
        "continental_championship",
        "friendly",
        "nations_league",
        "other",
        "world_cup",
        "world_cup_qualifier"
    ]

    for t in tournaments:
        row[f"tournament_{t}"] = (
            1 if t == tournament else 0
        )

    return pd.DataFrame([row])