"""Train and compare loan default classification models."""

from __future__ import annotations

import logging
from typing import Any, Final

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold

try:
    from .config import (
        CV_SPLITS,
        DATA_PATH,
        GRADIENT_BOOSTING_PARAMS,
        LOGISTIC_REGRESSION_PARAMS,
        MODEL_PATH,
        RANDOM_FOREST_PARAMS,
        RANDOM_STATE,
    )
except ImportError:
    from config import (  # type: ignore[no-redef]
        CV_SPLITS,
        DATA_PATH,
        GRADIENT_BOOSTING_PARAMS,
        LOGISTIC_REGRESSION_PARAMS,
        MODEL_PATH,
        RANDOM_FOREST_PARAMS,
        RANDOM_STATE,
    )

try:
    from .preprocess import LabelEncoder, preprocess_loan_data
except ImportError:
    from preprocess import LabelEncoder, preprocess_loan_data  # type: ignore[no-redef]

LOGGER = logging.getLogger(__name__)
METRIC_KEYS: Final[tuple[str, ...]] = ("Accuracy", "Precision", "Recall", "F1", "ROC-AUC")


def evaluate_model(model: Any, x_test: pd.DataFrame, y_test: pd.Series) -> dict[str, float]:
    """Compute evaluation metrics for a fitted binary classifier.

    Args:
        model: A trained model exposing `predict` and `predict_proba`.
        x_test: Test-set features.
        y_test: Test-set labels.

    Returns:
        Dictionary of core classification metrics.
    """
    y_pred = model.predict(x_test)
    y_proba = model.predict_proba(x_test)[:, 1]

    return {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred, zero_division=0),
        "Recall": recall_score(y_test, y_pred, zero_division=0),
        "F1": f1_score(y_test, y_pred, zero_division=0),
        "ROC-AUC": roc_auc_score(y_test, y_proba),
    }


def _build_models() -> dict[str, Any]:
    """Build candidate estimators with configured hyperparameters."""
    return {
        "LogisticRegression": LogisticRegression(**LOGISTIC_REGRESSION_PARAMS),
        "RandomForestClassifier": RandomForestClassifier(**RANDOM_FOREST_PARAMS),
        "GradientBoostingClassifier": GradientBoostingClassifier(**GRADIENT_BOOSTING_PARAMS),
    }


def _evaluate_models_with_cv(
    models: dict[str, Any], x: pd.DataFrame, y: pd.Series
) -> dict[str, list[dict[str, float]]]:
    """Evaluate all models across stratified folds with SMOTE on train folds."""
    evaluation_results: dict[str, list[dict[str, float]]] = {name: [] for name in models}
    skf = StratifiedKFold(n_splits=CV_SPLITS, shuffle=True, random_state=RANDOM_STATE)

    for train_idx, test_idx in skf.split(x, y):
        x_train, x_test = x.iloc[train_idx], x.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        smote = SMOTE(random_state=RANDOM_STATE)
        x_train_resampled, y_train_resampled = smote.fit_resample(x_train, y_train)

        for model_name, model in models.items():
            model.fit(x_train_resampled, y_train_resampled)
            metrics = evaluate_model(model, x_test, y_test)
            evaluation_results[model_name].append(metrics)

    return evaluation_results


def _average_fold_metrics(evaluation_results: dict[str, list[dict[str, float]]]) -> pd.DataFrame:
    """Average per-fold metrics and return sorted comparison dataframe."""
    averaged_rows: list[dict[str, float | str]] = []
    for model_name, metrics_list in evaluation_results.items():
        averaged_row: dict[str, float | str] = {
            metric: float(np.mean([row[metric] for row in metrics_list])) for metric in METRIC_KEYS
        }
        averaged_row["Model"] = model_name
        averaged_rows.append(averaged_row)

    return pd.DataFrame(averaged_rows).sort_values(by="ROC-AUC", ascending=False).reset_index(drop=True)


def _fit_best_model(best_name: str, models: dict[str, Any], x: pd.DataFrame, y: pd.Series) -> Any:
    """Fit the chosen model on full SMOTE-resampled data."""
    smote_full = SMOTE(random_state=RANDOM_STATE)
    x_resampled_full, y_resampled_full = smote_full.fit_resample(x, y)
    best_model = models[best_name]
    best_model.fit(x_resampled_full, y_resampled_full)
    return best_model


def train_and_select_best_model(df: pd.DataFrame) -> tuple[str, Any, pd.DataFrame, LabelEncoder]:
    """Train candidate models, evaluate on stratified split, and select the best by ROC-AUC.

    Args:
        df: Raw loan dataset.

    Returns:
        Model name, fitted best estimator, comparison dataframe, and employment label encoder.
    """
    clean_df = df.dropna().copy()
    employment_encoder = LabelEncoder()
    employment_encoder.fit_transform(clean_df["employment_status"])

    processed_df = preprocess_loan_data(df)
    x = processed_df.drop(columns=["default"])
    y = processed_df["default"]

    models = _build_models()
    evaluation_results = _evaluate_models_with_cv(models, x, y)
    comparison_df = _average_fold_metrics(evaluation_results)
    best_name = str(comparison_df.iloc[0]["Model"])
    best_model = _fit_best_model(best_name, models, x, y)

    return best_name, best_model, comparison_df, employment_encoder


def main() -> None:
    """Run model training, print comparison, and persist best model artifact."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at '{DATA_PATH}'. Run src/preprocess.py first.")

    df = pd.read_csv(DATA_PATH)
    best_name, best_model, comparison_df, employment_encoder = train_and_select_best_model(df)

    LOGGER.info("Model Comparison (sorted by ROC-AUC):\n%s", comparison_df.to_string(index=False, float_format=lambda value: f"{value:.4f}"))

    best_roc_auc = float(comparison_df.iloc[0]["ROC-AUC"])
    LOGGER.info("Winner: %s", best_name)
    LOGGER.info(
        "Reason: It achieved the highest ROC-AUC score (%.4f) on the stratified test split.",
        best_roc_auc,
    )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "model_name": best_name,
        "model": best_model,
        "employment_label_encoder": employment_encoder,
        "feature_columns": [column for column in df.columns if column != "default"]
        + ["debt_to_income", "loan_to_income", "monthly_payment", "payment_to_income"],
    }
    joblib.dump(artifact, MODEL_PATH)
    LOGGER.info("Saved best model artifact to: %s", MODEL_PATH)


if __name__ == "__main__":
    main()


__all__ = [
    "evaluate_model",
    "main",
    "train_and_select_best_model",
]
