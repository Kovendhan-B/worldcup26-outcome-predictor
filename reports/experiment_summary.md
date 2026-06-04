# World Cup Outcome Predictor - Experiment Summary

## V1 - Random Forest

Features:

* Historical Statistics
* Recent Form
* Head-to-Head
* Tournament Features

Results:

* Accuracy: 59.28%
* Draw Recall: 4%

Observation:

* Strong overall accuracy.
* Rarely predicted draws.

---

## V2 - CatBoost + Balanced Weights

Features:

* V1 Features
* Draw-Oriented Features
* Goal Balance Features

Results:

* Accuracy: 55.26%
* Draw Recall: 29%

Observation:

* Significant improvement in draw prediction.
* More balanced class performance.

---

## V3 - CatBoost + Elo Ratings

Features:

* V2 Features
* Elo Ratings

Results:

* Accuracy: 56.55%
* Draw Recall: 28%

Observation:

* Elo improved overall accuracy.
* Maintained balanced class predictions.
* Best overall model.
