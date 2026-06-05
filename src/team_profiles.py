import pandas as pd

features_df = pd.read_csv("../data/processed/features_v3.csv")
features_df["date"] = pd.to_datetime(features_df["date"])


def get_latest_team_profile(team):

    home_rows = features_df[
        features_df["home_team"] == team
    ]

    away_rows = features_df[
        features_df["away_team"] == team
    ]

    combined = pd.concat([
        home_rows,
        away_rows
    ])

    if combined.empty:
        raise ValueError(f"No data found for team: {team}")

    latest = (
        combined
        .sort_values("date")
        .iloc[-1]
    )

    return latest