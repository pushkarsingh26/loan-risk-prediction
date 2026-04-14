"""Centralized configuration constants for the loan risk pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Final

DATA_PATH: Final[Path] = Path("data/loan_data.csv")
MODEL_PATH: Final[Path] = Path("models/loan_model.pkl")

ROW_COUNT: Final[int] = 5000
RANDOM_STATE: Final[int] = 42
CV_SPLITS: Final[int] = 5

ANNUAL_INTEREST_RATE: Final[float] = 0.08
LOWER_CLIP_QUANTILE: Final[float] = 0.01
UPPER_CLIP_QUANTILE: Final[float] = 0.99
DEFAULT_RATE_QUANTILE: Final[float] = 0.88

LOGISTIC_REGRESSION_PARAMS: Final[dict[str, int]] = {
    "max_iter": 1000,
    "random_state": RANDOM_STATE,
}

RANDOM_FOREST_PARAMS: Final[dict[str, int | str]] = {
    "n_estimators": 200,
    "max_depth": 10,
    "class_weight": "balanced",
    "random_state": RANDOM_STATE,
}

GRADIENT_BOOSTING_PARAMS: Final[dict[str, int | float]] = {
    "n_estimators": 150,
    "learning_rate": 0.1,
    "random_state": RANDOM_STATE,
}

REQUIRED_FIELDS: Final[list[str]] = [
    "age",
    "income",
    "loan_amount",
    "credit_score",
    "employment_status",
    "loan_term",
    "existing_debts",
]

RISK_LABEL_THRESHOLD: Final[float] = 0.5

EMPLOYMENT_STATUSES: Final[list[str]] = ["Employed", "Self-Employed", "Part-Time", "Unemployed"]
EMPLOYMENT_STATUS_PROBABILITIES: Final[list[float]] = [0.55, 0.2, 0.18, 0.07]

LOAN_TERM_OPTIONS: Final[list[int]] = [12, 24, 36, 48, 60]
LOAN_TERM_PROBABILITIES: Final[list[float]] = [0.1, 0.2, 0.35, 0.2, 0.15]

__all__ = [
    "ANNUAL_INTEREST_RATE",
    "CV_SPLITS",
    "DATA_PATH",
    "DEFAULT_RATE_QUANTILE",
    "EMPLOYMENT_STATUSES",
    "EMPLOYMENT_STATUS_PROBABILITIES",
    "GRADIENT_BOOSTING_PARAMS",
    "LOGISTIC_REGRESSION_PARAMS",
    "LOAN_TERM_OPTIONS",
    "LOAN_TERM_PROBABILITIES",
    "LOWER_CLIP_QUANTILE",
    "MODEL_PATH",
    "RANDOM_FOREST_PARAMS",
    "RANDOM_STATE",
    "REQUIRED_FIELDS",
    "RISK_LABEL_THRESHOLD",
    "ROW_COUNT",
    "UPPER_CLIP_QUANTILE",
]