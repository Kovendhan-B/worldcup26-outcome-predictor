def build_bracket(tournament_data):
    """
    Build structured bracket data from tournament results.

    Args:
        tournament_data: dict returned by simulate_full_tournament

    Returns:
        dict with knockout stage names as keys,
        each containing list of match dicts
        (home, away, winner, probabilities)
    """

    stages = [
        ("Round of 32", "r32_results"),
        ("Round of 16", "r16_results"),
        ("Quarterfinal", "qf_results"),
        ("Semifinal", "sf_results"),
        ("Final", "final_results"),
    ]

    bracket = {}

    for stage_name, results_key in stages:

        bracket[stage_name] = []

        for match in tournament_data[results_key]:

            bracket[stage_name].append({
                "home": match["home_team"],
                "away": match["away_team"],
                "winner": match["winner"],
                "probabilities": match["probabilities"]
            })

    return bracket