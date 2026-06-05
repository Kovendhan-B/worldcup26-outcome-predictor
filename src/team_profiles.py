import pandas as pd
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

FEATURE_PATH = _ROOT / "data" / "processed" / "features_v3.csv"

features_df = pd.read_csv(FEATURE_PATH)
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


class TeamProfiles:

    def __init__(self, feature_path=FEATURE_PATH):

        self.df = pd.read_csv(feature_path)

        self.df["date"] = pd.to_datetime(
            self.df["date"]
        )

    def get_latest(self, team):

        home_rows = self.df[
            self.df["home_team"] == team
        ]

        away_rows = self.df[
            self.df["away_team"] == team
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