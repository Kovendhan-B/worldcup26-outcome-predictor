import joblib
import pandas as pd

from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score


def train_model(
    feature_file="../data/processed/features_v3.csv"
):

    df = pd.read_csv(feature_file)

    drop_cols = [
        "result",
        "home_score",
        "away_score",
        "date",
        "home_team",
        "away_team",
        "city",
        "country",
        "tournament",
        "tournament_category"
    ]

    X = df.drop(
        columns=[
            c for c in drop_cols
            if c in df.columns
        ]
    )

    y = df["result"]

    split_idx = int(len(df) * 0.8)

    X_train = X.iloc[:split_idx]
    X_test = X.iloc[split_idx:]

    y_train = y.iloc[:split_idx]
    y_test = y.iloc[split_idx:]

    model = CatBoostClassifier(
        iterations=500,
        depth=6,
        learning_rate=0.05,
        auto_class_weights="Balanced",
        loss_function="MultiClass",
        verbose=0,
        random_state=42
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    print(
        "Accuracy:",
        accuracy_score(y_test, preds)
    )

    joblib.dump(
        model,
        "../models/worldcup_predictor.pkl"
    )

    joblib.dump(
        X.columns.tolist(),
        "../models/feature_columns.pkl"
    )

    return model


if __name__ == "__main__":
    train_model()