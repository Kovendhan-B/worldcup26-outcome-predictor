import pandas as pd


def calculate_group_standings(group_results):
    """
    Calculate group standings from match results.

    Args:
        group_results: list of dicts with keys:
            home_team, away_team, winner
            (winner is a team name or "Draw")

    Returns:
        DataFrame with columns:
            Team, P, W, D, L, Pts
        sorted by Pts desc, then W desc.
    """

    standings = {}

    for match in group_results:

        home = match["home_team"]
        away = match["away_team"]
        winner = match["winner"]

        if home not in standings:
            standings[home] = {
                "Team": home,
                "P": 0,
                "W": 0,
                "D": 0,
                "L": 0,
                "Pts": 0
            }

        if away not in standings:
            standings[away] = {
                "Team": away,
                "P": 0,
                "W": 0,
                "D": 0,
                "L": 0,
                "Pts": 0
            }

        standings[home]["P"] += 1
        standings[away]["P"] += 1

        if winner == "Draw":
            standings[home]["D"] += 1
            standings[home]["Pts"] += 1
            standings[away]["D"] += 1
            standings[away]["Pts"] += 1

        elif winner == home:
            standings[home]["W"] += 1
            standings[home]["Pts"] += 3
            standings[away]["L"] += 1

        elif winner == away:
            standings[away]["W"] += 1
            standings[away]["Pts"] += 3
            standings[home]["L"] += 1

    df = pd.DataFrame(
        list(standings.values())
    )

    df = df.sort_values(
        ["Pts", "W"],
        ascending=[False, False]
    ).reset_index(drop=True)

    df.index += 1

    return df
