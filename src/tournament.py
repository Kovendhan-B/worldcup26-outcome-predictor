from src.predictor import predict_match
from src.standings import calculate_group_standings
import pandas as pd
import random


# ----------------------------------
# Match Simulation
# ----------------------------------

def simulate_match(home_team, away_team, allow_draw=True, upset_chance=0.0):
    """
    Simulate a single match.

    upset_chance: 0.0 = always pick favorite (realistic)
                  1.0 = fully weighted random (chaotic)

    Returns dict with:
        home_team, away_team, winner, outcome, probabilities

    winner = team name or "Draw" (group stage only)
    outcome = "Home Win" / "Draw" / "Away Win"
    """

    probs = predict_match(
        home_team,
        away_team,
        neutral=True
    )

    # Decide: deterministic or random?
    use_random = random.random() < upset_chance

    if use_random:
        outcomes = list(probs.keys())
        weights = list(probs.values())

        if not allow_draw:
            draw_idx = outcomes.index("Draw")
            draw_weight = weights[draw_idx]
            outcomes.pop(draw_idx)
            weights.pop(draw_idx)
            total = sum(weights)
            weights = [
                w + (w / total) * draw_weight
                for w in weights
            ]

        outcome = random.choices(
            outcomes, weights=weights, k=1
        )[0]

    else:
        # Deterministic: pick highest probability
        if not allow_draw:
            knockout_probs = {
                k: v for k, v in probs.items()
                if k != "Draw"
            }
            outcome = max(
                knockout_probs, key=knockout_probs.get
            )
        else:
            outcome = max(probs, key=probs.get)

    if outcome == "Home Win":
        winner = home_team
    elif outcome == "Away Win":
        winner = away_team
    else:
        winner = "Draw"

    return {
        "home_team": home_team,
        "away_team": away_team,
        "winner": winner,
        "outcome": outcome,
        "probabilities": probs
    }


# Group Stage

def simulate_group_stage(fixtures_path, upset_chance=0.0):
    """
    Simulate all group stage matches.

    Returns:
        all_results: list of match result dicts
        group_standings: dict of group -> DataFrame
    """

    fixtures = pd.read_csv(fixtures_path)

    group_fixtures = fixtures[
        fixtures["stage"] == "Group"
    ]

    groups = sorted(
        group_fixtures["group"].unique()
    )

    all_results = []
    group_standings = {}

    for group in groups:

        group_matches = group_fixtures[
            group_fixtures["group"] == group
        ]

        group_results = []

        for _, match in group_matches.iterrows():

            result = simulate_match(
                match["home_team"],
                match["away_team"],
                allow_draw=True,
                upset_chance=upset_chance
            )

            result["group"] = group
            result["stage"] = "Group"

            group_results.append(result)
            all_results.append(result)

        standings = calculate_group_standings(
            group_results
        )

        group_standings[group] = standings

    return all_results, group_standings


# ----------------------------------
# Knockout Qualification
# ----------------------------------

def get_knockout_teams(group_standings):
    """
    Determine 32 teams for the knockout stage.

    Returns:
        group_winners: dict group -> team
        group_runners_up: dict group -> team
        best_thirds: list of dicts (team, group, pts, w)
    """

    group_winners = {}
    group_runners_up = {}
    third_place_teams = []

    for group, standings in group_standings.items():

        teams = standings["Team"].tolist()

        group_winners[group] = teams[0]
        group_runners_up[group] = teams[1]

        if len(teams) >= 3:

            third_row = standings.iloc[2]

            third_place_teams.append({
                "team": third_row["Team"],
                "group": group,
                "pts": third_row["Pts"],
                "w": third_row["W"]
            })

    # Rank 3rd-place teams by points, then wins
    third_place_teams.sort(
        key=lambda x: (x["pts"], x["w"]),
        reverse=True
    )

    best_thirds = third_place_teams[:8]

    return group_winners, group_runners_up, best_thirds


# ----------------------------------
# Round of 32 Matchups
# ----------------------------------

def build_r32_matchups(
    group_winners,
    group_runners_up,
    best_thirds
):
    """
    Create Round of 32 matchups (16 matches).

    Bracket structure:
      - 8 matches: Group winners (A-H) vs best 3rd-place
      - 4 matches: Group winners (I-L) vs runners-up (D,C,B,A)
      - 4 matches: Remaining runners-up paired (E-L,F-K,G-J,H-I)
    """

    groups = sorted(group_winners.keys())

    third_teams = [t["team"] for t in best_thirds]

    matchups = []

    # 8 matches: 1A vs 3rd_8, 1B vs 3rd_7, ...
    for i in range(8):
        matchups.append((
            group_winners[groups[i]],
            third_teams[7 - i]
        ))

    # 4 matches: 1I vs 2D, 1J vs 2C, 1K vs 2B, 1L vs 2A
    distant = [
        groups[3], groups[2],
        groups[1], groups[0]
    ]

    for i in range(4):
        matchups.append((
            group_winners[groups[8 + i]],
            group_runners_up[distant[i]]
        ))

    # 4 matches: 2E vs 2L, 2F vs 2K, 2G vs 2J, 2H vs 2I
    ru_pairs = [
        (groups[4], groups[11]),
        (groups[5], groups[10]),
        (groups[6], groups[9]),
        (groups[7], groups[8]),
    ]

    for g1, g2 in ru_pairs:
        matchups.append((
            group_runners_up[g1],
            group_runners_up[g2]
        ))

    return matchups


# ----------------------------------
# Knockout Round
# ----------------------------------

def simulate_knockout_round(matchups, round_name, upset_chance=0.0):
    """
    Simulate a knockout round (no draws).

    Returns:
        results: list of match result dicts
        winners: list of winning team names
    """

    results = []
    winners = []

    for home, away in matchups:

        result = simulate_match(
            home, away,
            allow_draw=False,
            upset_chance=upset_chance
        )

        result["stage"] = round_name
        results.append(result)
        winners.append(result["winner"])

    return results, winners


# ----------------------------------
# Full Tournament
# ----------------------------------

def simulate_full_tournament(fixtures_path, upset_chance=0.0):
    """
    Simulate the entire World Cup 2026.

    Returns dict with:
        group_results, group_standings,
        group_winners, group_runners_up, best_thirds,
        r32_results, r16_results, qf_results,
        sf_results, final_results,
        champion, runner_up
    """

    # --- Group Stage ---

    group_results, group_standings = (
        simulate_group_stage(fixtures_path, upset_chance)
    )

    # --- Qualified Teams ---

    group_winners, group_runners_up, best_thirds = (
        get_knockout_teams(group_standings)
    )

    # --- Round of 32 (16 matches) ---

    r32_matchups = build_r32_matchups(
        group_winners,
        group_runners_up,
        best_thirds
    )

    r32_results, r32_winners = (
        simulate_knockout_round(
            r32_matchups, "Round of 32", upset_chance
        )
    )

    # --- Round of 16 (8 matches) ---

    r16_matchups = [
        (r32_winners[i], r32_winners[i + 1])
        for i in range(0, len(r32_winners), 2)
    ]

    r16_results, r16_winners = (
        simulate_knockout_round(
            r16_matchups, "Round of 16", upset_chance
        )
    )

    # --- Quarterfinals (4 matches) ---

    qf_matchups = [
        (r16_winners[i], r16_winners[i + 1])
        for i in range(0, len(r16_winners), 2)
    ]

    qf_results, qf_winners = (
        simulate_knockout_round(
            qf_matchups, "Quarterfinal", upset_chance
        )
    )

    # --- Semifinals (2 matches) ---

    sf_matchups = [
        (qf_winners[i], qf_winners[i + 1])
        for i in range(0, len(qf_winners), 2)
    ]

    sf_results, sf_winners = (
        simulate_knockout_round(
            sf_matchups, "Semifinal", upset_chance
        )
    )

    # --- Final (1 match) ---

    final_matchups = [
        (sf_winners[0], sf_winners[1])
    ]

    final_results, final_winners = (
        simulate_knockout_round(
            final_matchups, "Final", upset_chance
        )
    )

    # --- Champion & Runner-up ---

    champion = final_winners[0]

    runner_up = (
        sf_winners[0]
        if sf_winners[1] == champion
        else sf_winners[1]
    )

    return {
        "group_results": group_results,
        "group_standings": group_standings,
        "group_winners": group_winners,
        "group_runners_up": group_runners_up,
        "best_thirds": best_thirds,
        "r32_results": r32_results,
        "r16_results": r16_results,
        "qf_results": qf_results,
        "sf_results": sf_results,
        "final_results": final_results,
        "champion": champion,
        "runner_up": runner_up,
    }