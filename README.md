# FIFA World Cup 2026 — Outcome Predictor

A machine learning system that predicts international football match outcomes and simulates the full FIFA World Cup 2026 tournament. Built with CatBoost, engineered features derived from 25+ years of international match history, and a Monte Carlo simulation engine that quantifies each team's probability of reaching every knockout stage.

---

## Why Football Prediction Is Hard

Football is a low-scoring sport with high variance. A single goal separates most outcomes, draws occur in ~25% of matches, and an upset at any stage collapses all downstream predictions. Traditional accuracy benchmarks are misleading — a model that always predicts the home team wins can score 45%+ accuracy while being operationally useless.

The real challenge is three-class prediction (Home Win / Draw / Away Win) with a heavily imbalanced draw class, compounded by the fact that World Cup matches are neutral-venue knockout games where historical home advantage is irrelevant.

---

## Key Features

### Data Engineering
- 25+ years of international match history (~47,000 matches, 2000–2025)
- Chronological train/test split to prevent data leakage
- Historical team name normalization via `former_names.csv` (e.g., Zaire → DR Congo)
- Versioned feature sets (`features_v1`, `v2`, `v3`) tracking iterative improvements

### Machine Learning
- CatBoost classifier with `auto_class_weights="Balanced"` to address draw underrepresentation
- 54 engineered features spanning Elo ratings, rolling form, goal statistics, and tournament context
- Three model versions tracked with classification reports and feature importance exports
- `@lru_cache` on match predictions to eliminate redundant inference during simulation

### Tournament Simulation
- Deterministic mode: always picks the highest-probability outcome
- Stochastic mode: probability-weighted sampling with a tunable `upset_chance` parameter
- Full 48-team, 12-group bracket following the official FIFA 2026 format (Round of 32 → Final)
- Proper third-place qualification logic: top 8 best third-place teams advance by points and wins

### Streamlit Application
- **Match Predictor**: Select any two of the 48 qualified teams, get win/draw/loss probabilities with a stacked bar chart
- **Tournament Simulator**: Run the full tournament in one click; view group standings, knockout bracket, and match probabilities at each stage
- **Monte Carlo Simulator**: Run up to 10,000 full tournament simulations and view aggregated championship probabilities ranked by Champion %, Runner-Up %, SF %, etc.

---

## System Pipeline

```
Raw Data (results.csv)
    │
    ▼
Preprocessing (01_preprocessing.ipynb)
    │  • Filter 2000–2025
    │  • Normalize team names via former_names.csv
    │  • Categorize tournaments into 6 buckets
    │
    ▼
Feature Engineering (02_feature_engineering.ipynb)
    │  • Rolling cumulative stats per team (win rate, goals)
    │  • Last-5 form window
    │  • Elo rating calculation
    │  • Head-to-head stats
    │  • Differential features (home − away for each stat)
    │
    ▼
Model Training (03_model_training.ipynb)
    │  • CatBoost MultiClass, 500 iterations, depth 6
    │  • Balanced class weights
    │  • Chronological 80/20 split
    │
    ▼
Team Profile Lookup (team_profiles.py)
    │  • Fetch each team's most recent feature row
    │
    ▼
Match Prediction (predictor.py)
    │  • Build feature vector from two team profiles
    │  • model.predict_proba() → {Home Win %, Draw %, Away Win %}
    │
    ▼
Tournament Simulation (tournament.py)
    │  • Simulate group stage → compute standings → advance teams
    │  • Round of 32 → R16 → QF → SF → Final
    │
    ▼
Monte Carlo Engine (monte_carlo.py)
    │  • Run N full simulations using probability-weighted sampling
    │  • Aggregate across simulations → championship probability table
    │
    ▼
Streamlit App (app/)
       • Interactive predictions, bracket, and Monte Carlo visualizations
```

---

## Dataset

| Property | Detail |
|---|---|
| **Source** | [International Football Results](https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017) (Kaggle) |
| **Raw size** | ~47,000 matches |
| **Training window** | 2000 – 2025 |
| **Target variable** | `result` — 3-class: `Home Win`, `Draw`, `Away Win` |
| **Train / Test split** | Chronological 80/20 (no shuffling) |

**Key preprocessing steps:**
- **Name normalization**: Teams that changed names (e.g., Zaire → DR Congo) are mapped via `former_names.csv` to avoid treating the same national team as two different entities.
- **Tournament categorization**: Raw tournament strings are bucketed into 6 categories (`world_cup`, `world_cup_qualifier`, `continental_championship`, `nations_league`, `friendly`, `other`) to reduce noise while preserving competition context as a signal.
- **Chronological split**: Using `iloc[:split_idx]` / `iloc[split_idx:]` ensures the model is evaluated only on matches that occurred after its training window — the correct analogue to real-world deployment.

---

## Feature Engineering

Features are computed cumulatively up to (but not including) each match date, so no future information leaks into training.

### Elo Ratings
A single continuous score summarizing a team's historical performance adjusted for opponent strength. `elo_diff` is the **top-ranked feature** (10.85% importance), outperforming raw win rates because it carries the compounded history of quality-adjusted wins and losses.

### Recent Form (Last 5 Matches)
`last5_win_rate`, `last5_avg_goals_scored`, `last5_avg_goals_conceded` — a short rolling window that captures momentum independent of long-term historical averages. Crucial for detecting teams in form or slumps that their overall career stats would obscure.

### Goal Statistics
`avg_goals_scored`, `avg_goals_conceded`, `goal_balance` (scored − conceded) per team. `abs_goals_conceded_diff` ranks second in feature importance (4.46%), reflecting that defensive solidity is a stronger predictor of knockout results than attacking output.

### Team Strength Differentials
Every base stat is paired with a `_diff` feature (home − away). Providing both the raw values and the differential gives the model flexibility to weight the gap vs. absolute performance level independently. `strength_gap = |win_rate_diff| + |last5_win_rate_diff|` is a composite mismatch indicator.

### Tournament Context
One-hot encoded tournament category is included as a feature. A World Cup match carries different predictive dynamics than a friendly — teams prioritize differently, tactics differ, and draws have different strategic value. H2H features are included as a feature group (currently zero-filled for inference — a known improvement area).

---

## Model

### Why CatBoost

| Criterion | Rationale |
|---|---|
| **Native multi-class support** | `MultiClass` loss function handles 3-class prediction directly |
| **Balanced class weights** | `auto_class_weights="Balanced"` corrects for the draw class being underrepresented (~25%) |
| **No feature scaling required** | Gradient boosting on trees is scale-invariant; no normalization pipeline needed |
| **Robust to noisy labels** | Football results have high inherent variance; CatBoost's regularized trees resist overfitting |

### Training Configuration

```python
CatBoostClassifier(
    iterations=500,
    depth=6,
    learning_rate=0.05,
    auto_class_weights="Balanced",
    loss_function="MultiClass",
    random_state=42
)
```

### Model Iteration History

| Version | Model | Accuracy | Draw Recall | Key Change |
|---|---|---|---|---|
| V1 | Random Forest | 59.28% | 4% | Baseline — rarely predicted draws |
| V2 | CatBoost | 55.26% | 29% | Balanced weights + draw-oriented features |
| V3 | CatBoost | **56.55%** | **28%** | Added Elo ratings — best overall balance |

### Evaluation (V3, Test Set — 5,049 matches)

| Class | Precision | Recall | F1 |
|---|---|---|---|
| Away Win | 0.56 | 0.66 | 0.60 |
| Draw | 0.29 | 0.28 | 0.29 |
| Home Win | 0.71 | 0.64 | 0.68 |
| **Overall** | **—** | **0.57** | **0.57** |

### The Draw Problem

Draws are the hardest outcome to predict in football — they represent a near-tie in quality between two teams, where variance dominates. V1's Random Forest, without balancing, achieved 59% accuracy but had **4% draw recall** — it almost never predicted draws. Switching to CatBoost with `auto_class_weights="Balanced"` dropped overall accuracy slightly (~3 points) but raised draw recall to **28–29%**, producing a model that actually represents all three outcomes rather than treating draws as a rounding error.

---

## Monte Carlo Simulation

A single tournament simulation produces one deterministic path through 64 matches. That path is sensitive to every early upset — one wrong group-stage result cascades into a completely different bracket.

Monte Carlo addresses this by running **N independent full-tournament simulations** (100–10,000), each using probability-weighted random sampling for every match. The draw probability is redistributed proportionally to Home Win and Away Win in knockout rounds where draws are not allowed.

The output is a ranking table showing each team's probability of reaching each stage:

| Team | Champion % | Runner-Up % | SF % | QF % | R16 % | R32 % |
|---|---|---|---|---|---|---|
| France | 14.2 | 22.1 | 38.4 | 55.7 | 72.3 | 88.1 |
| Brazil | 12.8 | 19.5 | 35.2 | 51.3 | 69.8 | 85.4 |
| ... | ... | ... | ... | ... | ... | ... |

*Sample output — actual values vary per simulation run.*

**Performance optimization**: predictions are cached with `@lru_cache(maxsize=10000)`. Since model inference is deterministic for any given team pair, each unique matchup is computed once and reused across all N simulations — making 10,000-simulation runs practical within seconds.

---

## Project Structure

```
worldcup26-outcome-predictor/
│
├── app/                               # Streamlit application
│   ├── streamlit_app.py               # Page 1: Match Predictor
│   └── pages/
│       ├── 2_Tournament_Simulator.py  # Full bracket simulation
│       └── 3_Monte_Carlo.py           # N-simulation probability engine
│
├── data/
│   ├── raw/
│   │   ├── results.csv                # ~47,000 international matches (2000–2025)
│   │   └── former_names.csv           # Team name normalization map
│   ├── processed/
│   │   ├── cleaned_matches.csv        # Preprocessed match data
│   │   ├── features_v1.csv            # Feature set v1
│   │   ├── features_v2.csv            # + draw-oriented features
│   │   └── features_v3.csv            # + Elo ratings (final)
│   ├── fixtures/
│   │   └── worldcup2026_fixtures.csv  # Official WC 2026 group fixtures
│   └── worldcup_teams.py              # List of 48 qualified teams
│
├── models/
│   ├── catboost_v1.pkl                # Baseline CatBoost
│   ├── catboost_v2.pkl                # + balanced weights
│   ├── catboost_v3.pkl                # + Elo features (production)
│   └── feature_columns.pkl            # Ordered feature list for inference
│
├── notebooks/
│   ├── 01_preprocessing.ipynb         # Data cleaning and normalization
│   ├── 02_feature_engineering.ipynb   # Feature construction
│   ├── 03_model_training.ipynb        # Training, evaluation, experiments
│   └── 04_prediction_pipeline.ipynb   # End-to-end prediction walkthrough
│
├── src/                               # Core Python package
│   ├── feature_engineering.py         # Build feature vector for a single match
│   ├── predictor.py                   # Load model + predict match probabilities
│   ├── team_profiles.py               # Fetch latest team stats from feature data
│   ├── tournament.py                  # Full tournament simulation (deterministic/stochastic)
│   ├── monte_carlo.py                 # Monte Carlo engine with LRU-cached predictions
│   ├── standings.py                   # Calculate group stage standings
│   ├── bracket.py                     # Structure knockout results for display
│   └── flags.py                       # Country code → flag image mapping
│
├── reports/
│   ├── experiment_summary.md          # Model iteration notes
│   ├── experiments.csv                # Metrics per version
│   ├── catboost_v1_classification_report.txt
│   └── catboost_v1_feature_importance.csv
│
├── assets/
│   └── banner.png                     # App header image
│
├── pyproject.toml                     # Project metadata and dependencies
└── requirements.txt                   # Pip-compatible dependency list
```

---

## Installation & Usage

**Requirements:** Python 3.10+

```bash
# 1. Clone the repository
git clone https://github.com/Kovendhan-B/worldcup26-outcome-predictor.git
cd worldcup26-outcome-predictor

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Retrain the model
#    Pre-trained models are already included in models/
python -m src.train

# 4. Launch the Streamlit app
streamlit run app/streamlit_app.py
```

The app opens at `http://localhost:8501`. Use the sidebar to navigate between Match Predictor, Tournament Simulator, and Monte Carlo pages.

---

## Future Improvements

| Area | Improvement |
|---|---|
| **Explainability** | SHAP values to show which features drove each prediction per match |
| **H2H Features** | Replace placeholder zeros with real historical head-to-head stats |
| **Data Pipeline** | Script to pull new results from an API and rebuild feature sets incrementally |
| **Score Prediction** | Poisson regression on expected goals for realistic scoreline simulation |
| **Hyperparameter Tuning** | Optuna / BayesSearchCV on CatBoost depth, iterations, and learning rate |
| **Docker Support** | Containerize the Streamlit app for reproducible one-command deployment |
| **CI/CD** | GitHub Actions to run notebook tests and validate model metrics on each push |

---

## Tech Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **ML Model** | CatBoost 1.2+ |
| **Data Processing** | Pandas 2.0+ |
| **Model Serialization** | joblib |
| **ML Utilities** | scikit-learn |
| **Web Application** | Streamlit 1.30+ |
| **Visualization** | Plotly |
| **Package Manager** | uv / pip |
| **Notebooks** | Jupyter |

---

> **Recruiter Note — Suggested Enhancements:**
> The strongest immediate additions would be: **(1)** SHAP explainability plots in the notebook and app — this is the most common ask for DS portfolio projects; **(2)** replacing H2H placeholder zeros with real data, since it is already proven to be a meaningful feature group; **(3)** adding a live demo link (Streamlit Community Cloud) to maximize recruiter engagement without requiring a local setup.
