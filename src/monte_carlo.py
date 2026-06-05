import random
from functools import lru_cache
import pandas as pd

from src.predictor import predict_match
from src.standings import calculate_group_standings
from src.tournament import get_knockout_teams, build_r32_matchups

# ----------------------------------
# Cached Predictor
# ----------------------------------

@lru_cache(maxsize=10000)
def cached_predict_match(home_team, away_team, neutral=True):
    """
    Caches match predictions to drastically speed up Monte Carlo simulations.
    Since predictions are deterministic for the same teams, we only need to
    run the model inference once per unique matchup.
    """
    return predict_match(home_team, away_team, neutral)


# ----------------------------------
# Monte Carlo Match Simulation
# ----------------------------------

def simulate_match_monte_carlo(home_team, away_team, allow_draw=True):
    """
    Simulate a single match using probability-weighted random sampling.
    """
    probs = cached_predict_match(home_team, away_team, neutral=True)

    outcomes = list(probs.keys())
    weights = list(probs.values())

    if not allow_draw:
        draw_idx = outcomes.index("Draw")
        draw_weight = weights[draw_idx]
        outcomes.pop(draw_idx)
        weights.pop(draw_idx)
        
        # Renormalize weights
        total = sum(weights)
        if total > 0:
            weights = [w + (w / total) * draw_weight for w in weights]
        else:
            # Fallback if somehow both win probabilities were exactly 0 (unlikely)
            weights = [0.5, 0.5]

    outcome = random.choices(outcomes, weights=weights, k=1)[0]

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


def simulate_knockout_round_mc(matchups, round_name):
    """
    Simulate a knockout round for Monte Carlo.
    """
    results = []
    winners = []

    for home, away in matchups:
        result = simulate_match_monte_carlo(home, away, allow_draw=False)
        result["stage"] = round_name
        results.append(result)
        winners.append(result["winner"])

    return results, winners


# ----------------------------------
# Monte Carlo Full Tournament
# ----------------------------------

def simulate_full_tournament_mc(fixtures_path):
    """
    Simulate a single World Cup tournament using Monte Carlo methodology.
    Returns only the necessary data for aggregated stats.
    """
    fixtures = pd.read_csv(fixtures_path)

    # --- Group Stage ---
    group_fixtures = fixtures[fixtures["stage"] == "Group"]
    groups = sorted(group_fixtures["group"].unique())

    all_results = []
    group_standings = {}

    for group in groups:
        group_matches = group_fixtures[group_fixtures["group"] == group]
        group_results = []
        for _, match in group_matches.iterrows():
            result = simulate_match_monte_carlo(
                match["home_team"], match["away_team"], allow_draw=True
            )
            result["group"] = group
            result["stage"] = "Group"
            group_results.append(result)
            all_results.append(result)

        standings = calculate_group_standings(group_results)
        group_standings[group] = standings

    # --- Qualified Teams ---
    group_winners, group_runners_up, best_thirds = get_knockout_teams(group_standings)

    # --- Round of 32 ---
    r32_matchups = build_r32_matchups(group_winners, group_runners_up, best_thirds)
    _, r32_winners = simulate_knockout_round_mc(r32_matchups, "Round of 32")

    # --- Round of 16 ---
    r16_matchups = [(r32_winners[i], r32_winners[i + 1]) for i in range(0, len(r32_winners), 2)]
    _, r16_winners = simulate_knockout_round_mc(r16_matchups, "Round of 16")

    # --- Quarterfinals ---
    qf_matchups = [(r16_winners[i], r16_winners[i + 1]) for i in range(0, len(r16_winners), 2)]
    _, qf_winners = simulate_knockout_round_mc(qf_matchups, "Quarterfinal")

    # --- Semifinals ---
    sf_matchups = [(qf_winners[i], qf_winners[i + 1]) for i in range(0, len(qf_winners), 2)]
    _, sf_winners = simulate_knockout_round_mc(sf_matchups, "Semifinal")

    # --- Final ---
    final_matchups = [(sf_winners[0], sf_winners[1])]
    _, final_winners = simulate_knockout_round_mc(final_matchups, "Final")

    # --- Output processing ---
    champion = final_winners[0]
    runner_up = sf_winners[0] if sf_winners[1] == champion else sf_winners[1]

    return {
        "champion": champion,
        "runner_up": runner_up,
        "semifinalists": sf_winners,
        "quarterfinalists": qf_winners,
        "r16_teams": r16_winners,
        "r32_teams": r32_winners
    }


# ----------------------------------
# Monte Carlo Execution Engine
# ----------------------------------

def run_monte_carlo_simulations(fixtures_path, num_simulations=1000, progress_callback=None):
    """
    Run N simulations and aggregate the results.
    """
    team_stats = {}

    for i in range(num_simulations):
        if i % 100 == 0:
            print(f"Simulation {i}/{num_simulations}...")

        if progress_callback:
            progress_callback(i, num_simulations)

        data = simulate_full_tournament_mc(fixtures_path)

        teams_to_update = set(
            [data["champion"], data["runner_up"]] +
            data["semifinalists"] +
            data["quarterfinalists"] +
            data["r16_teams"] +
            data["r32_teams"]
        )

        for team in teams_to_update:
            if team not in team_stats:
                team_stats[team] = {
                    "Champion": 0, "Runner-Up": 0, "SF": 0, "QF": 0, "R16": 0, "R32": 0
                }

        team_stats[data["champion"]]["Champion"] += 1
        team_stats[data["runner_up"]]["Runner-Up"] += 1
        
        for team in data["semifinalists"]: team_stats[team]["SF"] += 1
        for team in data["quarterfinalists"]: team_stats[team]["QF"] += 1
        for team in data["r16_teams"]: team_stats[team]["R16"] += 1
        for team in data["r32_teams"]: team_stats[team]["R32"] += 1

    if progress_callback:
        progress_callback(num_simulations, num_simulations)

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(team_stats, orient='index')
    
    # Calculate percentages
    df = (df / num_simulations) * 100
    df = df.round(2)
    
    # Ensure correct column ordering
    columns = ["Champion", "Runner-Up", "SF", "QF", "R16", "R32"]
    df = df[columns]
    
    # Rename for output
    df.columns = ["Champion %", "Runner-Up %", "SF %", "QF %", "R16 %", "R32 %"]
    
    df = df.sort_values(by=["Champion %", "Runner-Up %", "SF %"], ascending=False)
    df.reset_index(inplace=True)
    df.rename(columns={"index": "Team"}, inplace=True)

    return df
