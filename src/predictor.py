import joblib
from team_profiles import get_latest_team_profile
import pandas as pd

model = joblib.load(
    "../models/catboost_v3.pkl"
)

feature_columns = joblib.load(
    "../models/feature_columns.pkl"
)
features_df = pd.read_csv(
    "../data/processed/features_v3.csv"
)

def get_latest_team_stats(team):

    home_matches = features_df[
        features_df["home_team"] == team
    ]

    away_matches = features_df[
        features_df["away_team"] == team
    ]

    latest_home = (
        home_matches.sort_values("date")
        .tail(1)
    )

    latest_away = (
        away_matches.sort_values("date")
        .tail(1)
    )

    if len(latest_home) == 0:
        return None

    if len(latest_away) == 0:
        return None

    if latest_home["date"].iloc[0] > latest_away["date"].iloc[0]:
        return latest_home.iloc[0]

    return latest_away.iloc[0]

def build_match_features(
    home_team,
    away_team,
    neutral=True,
    tournament="world_cup"
):

    home = get_latest_team_profile(home_team)
    away = get_latest_team_profile(away_team)

    row = {}

    # --------------------------
    # Base Features
    # --------------------------

    row["neutral"] = int(neutral)

    row["year"] = 2026
    row["month"] = 6

    row["home_matches_played"] = home["home_matches_played"]
    row["away_matches_played"] = away["away_matches_played"]

    row["home_win_rate"] = home["home_win_rate"]
    row["away_win_rate"] = away["away_win_rate"]

    row["home_draw_rate"] = home["home_draw_rate"]
    row["away_draw_rate"] = away["away_draw_rate"]

    row["home_loss_rate"] = home["home_loss_rate"]
    row["away_loss_rate"] = away["away_loss_rate"]

    row["home_avg_goals_scored"] = home["home_avg_goals_scored"]
    row["away_avg_goals_scored"] = away["away_avg_goals_scored"]

    row["home_avg_goals_conceded"] = home["home_avg_goals_conceded"]
    row["away_avg_goals_conceded"] = away["away_avg_goals_conceded"]

    row["home_last5_win_rate"] = home["home_last5_win_rate"]
    row["away_last5_win_rate"] = away["away_last5_win_rate"]

    row["home_last5_avg_goals_scored"] = home["home_last5_avg_goals_scored"]
    row["away_last5_avg_goals_scored"] = away["away_last5_avg_goals_scored"]

    row["home_last5_avg_goals_conceded"] = home["home_last5_avg_goals_conceded"]
    row["away_last5_avg_goals_conceded"] = away["away_last5_avg_goals_conceded"]

    row["home_elo"] = home["home_elo"]
    row["away_elo"] = away["away_elo"]

    # --------------------------
    # Difference Features
    # --------------------------

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

    row["elo_diff"] = (
        row["home_elo"]
        - row["away_elo"]
    )

    # --------------------------
    # Goal Balance
    # --------------------------

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

    # --------------------------
    # Absolute Features
    # --------------------------

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
        abs(
            row["home_win_rate"]
            - row["away_win_rate"]
        )
        +
        abs(
            row["home_last5_win_rate"]
            - row["away_last5_win_rate"]
        )
    )

    # --------------------------
    # H2H placeholders
    # --------------------------

    row["h2h_matches"] = 0
    row["h2h_home_win_rate"] = 0
    row["h2h_away_win_rate"] = 0
    row["h2h_draw_rate"] = 0
    row["h2h_win_rate_diff"] = 0
    row["abs_h2h_diff"] = 0

    # --------------------------
    # Tournament Features
    # --------------------------

    row["tournament_world_cup"] = 1
    row["tournament_friendly"] = 0
    row["tournament_other"] = 0
    row["tournament_nations_league"] = 0
    row["tournament_continental_championship"] = 0
    row["tournament_world_cup_qualifier"] = 0

    return pd.DataFrame([row])

def predict_match(
    home_team,
    away_team,
    neutral=True
):

    X = build_match_features(
        home_team,
        away_team,
        neutral
    )

    X = X.reindex(
        columns=feature_columns,
        fill_value=0
    )

    probs = model.predict_proba(X)[0]

    return {
        "Home Win": float(round(probs[2] * 100, 2)),
        "Draw": float(round(probs[1] * 100, 2)),
        "Away Win": float(round(probs[0] * 100, 2))
    }

# print(predict_match("Brazil", "India"))
# print(predict_match("Argentina", "Brazil"))
# print(predict_match("France", "Germany"))
# print(predict_match("San Marino", "Spain"))

joblib.dump(
    model,
    "../models/catboost_worldcup_v3.pkl"
)

joblib.dump(
    feature_columns,
    "../models/feature_columns.pkl"
)