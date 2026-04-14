"""Predict loan default risk using the trained model artifact."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

try:
    from .config import ANNUAL_INTEREST_RATE, MODEL_PATH, REQUIRED_FIELDS, RISK_LABEL_THRESHOLD
except ImportError:
    from config import ANNUAL_INTEREST_RATE, MODEL_PATH, REQUIRED_FIELDS, RISK_LABEL_THRESHOLD  # type: ignore[no-redef]

LOGGER = logging.getLogger(__name__)


def _load_model_artifact(model_path: Path = MODEL_PATH) -> dict[str, Any]:
    """Load the serialized model artifact from disk.

    Args:
        model_path: Path to the trained artifact.

    Returns:
        Dictionary containing model, encoder, and metadata.

    Raises:
        FileNotFoundError: If the model file does not exist.
    """
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file '{model_path}' not found. Train the model first by running 'python src/train_model.py'."
        )

    return joblib.load(model_path)


def _encode_employment_status(employment_status: str, encoder: Any) -> int:
    """Encode employment status using the persisted label encoder."""
    if hasattr(encoder, "transform"):
        return int(encoder.transform([employment_status])[0])

    classes = list(getattr(encoder, "classes_", []))
    if employment_status not in classes:
        raise ValueError(f"Unknown employment_status '{employment_status}'. Known values: {classes}")
    return classes.index(employment_status)


def _build_features(input_data: dict[str, Any], encoder: Any) -> pd.DataFrame:
    """Create a one-row feature dataframe with training-consistent engineering."""
    missing = [field for field in REQUIRED_FIELDS if field not in input_data]
    if missing:
        raise ValueError(f"Missing required input fields: {missing}")

    income = float(input_data["income"])
    loan_amount = float(input_data["loan_amount"])
    existing_debts = float(input_data["existing_debts"])
    loan_term = int(input_data["loan_term"])
    employment_status = str(input_data["employment_status"])

    if income <= 0:
        raise ValueError("income must be greater than 0.")
    if loan_term <= 0:
        raise ValueError("loan_term must be greater than 0.")

    monthly_rate = ANNUAL_INTEREST_RATE / 12
    denominator = 1 - (1 + monthly_rate) ** (-loan_term)
    monthly_payment = (loan_amount * monthly_rate) / denominator

    feature_row: dict[str, float | int] = {
        "age": int(input_data["age"]),
        "income": income,
        "loan_amount": loan_amount,
        "credit_score": int(input_data["credit_score"]),
        "employment_status": _encode_employment_status(employment_status, encoder),
        "loan_term": loan_term,
        "existing_debts": existing_debts,
        "debt_to_income": existing_debts / income,
        "loan_to_income": loan_amount / income,
        "monthly_payment": monthly_payment,
        "payment_to_income": monthly_payment / (income / 12),
    }

    return pd.DataFrame([feature_row])


def _credit_score_reasons(credit_score: float) -> list[tuple[float, str]]:
    """Return risk reasons related to credit score."""
    if credit_score < 620:
        return [(3.0, "Low credit score")]
    if credit_score < 680:
        return [(2.0, "Below-average credit score")]
    return []


def _debt_burden_reasons(debt_to_income: float) -> list[tuple[float, str]]:
    """Return risk reasons related to debt burden."""
    if debt_to_income > 0.40:
        return [(2.8, "High existing debt relative to income")]
    if debt_to_income > 0.30:
        return [(1.8, "Moderately high debt burden")]
    return []


def _loan_burden_reasons(loan_to_income: float) -> list[tuple[float, str]]:
    """Return risk reasons related to loan burden."""
    if loan_to_income > 0.45:
        return [(2.6, "Large loan amount compared to income")]
    if loan_to_income > 0.30:
        return [(1.6, "Elevated loan-to-income ratio")]
    return []


def _employment_reasons(employment_status: str) -> list[tuple[float, str]]:
    """Return risk reasons related to employment status."""
    if employment_status == "Unemployed":
        return [(2.4, "Unemployed status increases repayment uncertainty")]
    if employment_status == "Part-Time":
        return [(1.4, "Part-time employment may reduce income stability")]
    return []


def _probability_reasons(probability: float) -> list[tuple[float, str]]:
    """Return risk reasons related to model output probability."""
    if probability > 0.70:
        return [(2.2, "Model predicts a high default probability")]
    if probability > 0.50:
        return [(1.2, "Model predicts moderate default probability")]
    return []


def _derive_risk_factors(input_data: dict[str, Any], probability: float) -> list[str]:
    """Return up to three top reasons that most contribute to risk."""
    scored_reasons: list[tuple[float, str]] = []

    credit_score = float(input_data["credit_score"])
    scored_reasons.extend(_credit_score_reasons(credit_score))

    income = float(input_data["income"])
    debt_to_income = float(input_data["existing_debts"]) / max(income, 1.0)
    loan_to_income = float(input_data["loan_amount"]) / max(income, 1.0)
    scored_reasons.extend(_debt_burden_reasons(debt_to_income))
    scored_reasons.extend(_loan_burden_reasons(loan_to_income))

    employment_status = str(input_data["employment_status"])
    scored_reasons.extend(_employment_reasons(employment_status))

    scored_reasons.extend(_probability_reasons(probability))

    if not scored_reasons:
        scored_reasons = [(1.0, "Strong credit and affordability profile"), (0.9, "Stable debt and payment ratios")]

    scored_reasons.sort(key=lambda item: item[0], reverse=True)
    return [reason for _, reason in scored_reasons[:3]]


def predict_loan_risk(input_data: dict[str, Any]) -> dict[str, Any]:
    """Predict loan default risk for one applicant profile.

    Args:
        input_data: Applicant and loan fields containing age, income, loan_amount,
            credit_score, employment_status, loan_term, and existing_debts.

    Returns:
        Prediction payload with risk label, probability, risk score, and top factors.
    """
    artifact = _load_model_artifact()
    model = artifact["model"]
    encoder = artifact["employment_label_encoder"]
    feature_columns = artifact["feature_columns"]

    features_df = _build_features(input_data, encoder)
    features_df = features_df[feature_columns]

    probability = float(model.predict_proba(features_df)[0][1])
    risk_label = "High Risk" if probability >= RISK_LABEL_THRESHOLD else "Low Risk"
    risk_score = int(np.clip(round(probability * 100), 0, 100))
    risk_factors = _derive_risk_factors(input_data, probability)

    return {
        "risk_label": risk_label,
        "probability": probability,
        "risk_score": risk_score,
        "risk_factors": risk_factors,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
    try:
        high_risk_input = {
            "age": 25,
            "income": 28000,
            "loan_amount": 22000,
            "credit_score": 560,
            "employment_status": "Unemployed",
            "loan_term": 60,
            "existing_debts": 18000,
        }
        low_risk_input = {
            "age": 41,
            "income": 120000,
            "loan_amount": 15000,
            "credit_score": 785,
            "employment_status": "Employed",
            "loan_term": 24,
            "existing_debts": 5000,
        }

        LOGGER.info("=== High-Risk Sample ===")
        LOGGER.info("%s", predict_loan_risk(high_risk_input))
        LOGGER.info("=== Low-Risk Sample ===")
        LOGGER.info("%s", predict_loan_risk(low_risk_input))
    except FileNotFoundError as exc:
        LOGGER.error("Error: %s", exc)


__all__ = [
    "predict_loan_risk",
]
