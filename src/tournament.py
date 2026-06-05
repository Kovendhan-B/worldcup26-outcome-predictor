from src.predictor import predict_match
import pandas as pd


def simulate_match(home_team, away_team):

    probs = predict_match(
        home_team,
        away_team,
        neutral=True
    )

    winner = max(
        probs,
        key=probs.get
    )

    return {
        "home_team": home_team,
        "away_team": away_team,
        "winner": winner,
        "probabilities": probs
    }


def simulate_tournament(fixtures_path):

    fixtures = pd.read_csv(fixtures_path)

    results = []

    for _, match in fixtures.iterrows():

        prediction = simulate_match(
            match["home_team"],
            match["away_team"]
        )

        results.append(prediction)

    return results