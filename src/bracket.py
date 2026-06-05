def build_bracket(matches):

    bracket = []

    for match in matches:

        bracket.append(
            (
                match["home_team"],
                match["away_team"],
                match["winner"]
            )
        )

    return bracket