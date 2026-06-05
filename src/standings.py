import pandas as pd


def calculate_group_standings(group_results):
    """
    Calculate group standings from match results.

    Args:
        group_results: list of dicts with keys:
            home_team, away_team, winner, probabilities

    Returns:
        DataFrame with columns:
            Team, W, D, L, Pts
        sorted by Pts descending.
    """

    standings = {}

    for match in group_results:

        home = match["home_team"]
        away = match["away_team"]
        winner = match["winner"]

        if home not in standings:
            standings[home] = {
                "Team": home,
                "W": 0,
                "D": 0,
                "L": 0,
                "Pts": 0
            }

        if away not in standings:
            standings[away] = {
                "Team": away,
                "W": 0,
                "D": 0,
                "L": 0,
                "Pts": 0
            }

        if winner == "Draw":
            standings[home]["D"] += 1
            standings[home]["Pts"] += 1
            standings[away]["D"] += 1
            standings[away]["Pts"] += 1

        elif winner == "Home Win":
            standings[home]["W"] += 1
            standings[home]["Pts"] += 3
            standings[away]["L"] += 1

        elif winner == "Away Win":
            standings[away]["W"] += 1
            standings[away]["Pts"] += 3
            standings[home]["L"] += 1

    df = pd.DataFrame(
        list(standings.values())
    )

    df = df.sort_values(
        "Pts",
        ascending=False
    ).reset_index(drop=True)

    df.index += 1

    return df


def get_group_winners(standings_df, top_n=2):
    """
    Return top N teams from a group standings DataFrame.
    """

    return standings_df.head(top_n)[
        "Team"
    ].tolist()
