"""Generate and preprocess a synthetic loan dataset."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

try:
    from .config import (
        ANNUAL_INTEREST_RATE,
        DATA_PATH,
        DEFAULT_RATE_QUANTILE,
        EMPLOYMENT_STATUSES,
        EMPLOYMENT_STATUS_PROBABILITIES,
        LOAN_TERM_OPTIONS,
        LOAN_TERM_PROBABILITIES,
        LOWER_CLIP_QUANTILE,
        RANDOM_STATE,
        ROW_COUNT,
        UPPER_CLIP_QUANTILE,
    )
except ImportError:
    from config import (  # type: ignore[no-redef]
        ANNUAL_INTEREST_RATE,
        DATA_PATH,
        DEFAULT_RATE_QUANTILE,
        EMPLOYMENT_STATUSES,
        EMPLOYMENT_STATUS_PROBABILITIES,
        LOAN_TERM_OPTIONS,
        LOAN_TERM_PROBABILITIES,
        LOWER_CLIP_QUANTILE,
        RANDOM_STATE,
        ROW_COUNT,
        UPPER_CLIP_QUANTILE,
    )

try:
    from sklearn.preprocessing import LabelEncoder
except ImportError:
    class LabelEncoder:  # type: ignore[no-redef]
        """Fallback label encoder when scikit-learn is unavailable."""

        def __init__(self) -> None:
            self.classes_: np.ndarray = np.array([])

        def fit_transform(self, values: pd.Series) -> np.ndarray:
            """Encode labels as integers and store learned classes."""
            categories = pd.Categorical(values)
            self.classes_ = np.asarray(categories.categories)
            return categories.codes

LOGGER = logging.getLogger(__name__)


def _compute_raw_risk(
    employment_status: np.ndarray,
    credit_score: np.ndarray,
    existing_debts: np.ndarray,
    income: np.ndarray,
    loan_amount: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Compute synthetic default risk score used for target generation."""
    employment_risk = np.select(
        [
            employment_status == "Unemployed",
            employment_status == "Part-Time",
            employment_status == "Self-Employed",
        ],
        [0.22, 0.1, 0.06],
        default=0.0,
    )
    credit_risk = ((700 - credit_score).clip(min=0) / 650) * 0.35
    debt_burden = (existing_debts / income) * 0.2
    loan_burden = (loan_amount / income) * 0.25
    random_noise = rng.normal(0, 0.02, size=income.shape[0])
    return employment_risk + credit_risk + debt_burden + loan_burden + random_noise


def _build_synthetic_dataframe(
    age: np.ndarray,
    income: np.ndarray,
    loan_amount: np.ndarray,
    credit_score: np.ndarray,
    employment_status: np.ndarray,
    loan_term: np.ndarray,
    existing_debts: np.ndarray,
    default: np.ndarray,
) -> pd.DataFrame:
    """Construct the final synthetic dataframe."""
    return pd.DataFrame(
        {
            "age": age,
            "income": np.round(income, 2),
            "loan_amount": np.round(loan_amount, 2),
            "credit_score": np.round(credit_score).astype(int),
            "employment_status": employment_status,
            "loan_term": loan_term,
            "existing_debts": np.round(existing_debts, 2),
            "default": default,
        }
    )


def _clip_numeric_outliers(processed_df: pd.DataFrame) -> pd.DataFrame:
    """Clip numeric feature outliers to configured quantile bounds."""
    numeric_columns = processed_df.select_dtypes(include=[np.number]).columns.tolist()
    columns_to_clip = [column for column in numeric_columns if column != "default"]
    for column in columns_to_clip:
        lower, upper = processed_df[column].quantile([LOWER_CLIP_QUANTILE, UPPER_CLIP_QUANTILE])
        processed_df[column] = processed_df[column].clip(lower=lower, upper=upper)
    return processed_df


def generate_synthetic_loan_data(n_rows: int = ROW_COUNT, random_state: int = RANDOM_STATE) -> pd.DataFrame:
    """Generate a synthetic loan dataset with an approximately 10-15% default rate.

    Args:
        n_rows: Number of rows to generate.
        random_state: Random seed for reproducibility.

    Returns:
        A dataframe containing synthetic borrower and loan details.
    """
    rng = np.random.default_rng(random_state)

    age = rng.integers(21, 66, size=n_rows)
    income = rng.normal(70000, 25000, size=n_rows).clip(18000, 250000)
    loan_amount = rng.normal(18000, 9000, size=n_rows).clip(2000, 70000)
    credit_score = rng.normal(680, 90, size=n_rows).clip(300, 850)
    employment_status = rng.choice(
        EMPLOYMENT_STATUSES,
        size=n_rows,
        p=EMPLOYMENT_STATUS_PROBABILITIES,
    )
    loan_term = rng.choice(LOAN_TERM_OPTIONS, size=n_rows, p=LOAN_TERM_PROBABILITIES)
    existing_debts = rng.normal(12000, 7000, size=n_rows).clip(0, 60000)

    raw_risk = _compute_raw_risk(employment_status, credit_score, existing_debts, income, loan_amount, rng)
    threshold = np.quantile(raw_risk, DEFAULT_RATE_QUANTILE)
    default = (raw_risk > threshold).astype(int)

    return _build_synthetic_dataframe(
        age=age,
        income=income,
        loan_amount=loan_amount,
        credit_score=credit_score,
        employment_status=employment_status,
        loan_term=loan_term,
        existing_debts=existing_debts,
        default=default,
    )


def preprocess_loan_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform loan data for downstream modeling.

    This function removes null rows, label-encodes employment status, engineers
    ratio/payment features, and clips numeric outliers to the 1st-99th percentiles.

    Args:
        df: Input loan dataframe.

    Returns:
        A cleaned and feature-engineered dataframe.
    """
    processed_df = df.dropna().copy()

    encoder = LabelEncoder()
    processed_df["employment_status"] = encoder.fit_transform(processed_df["employment_status"])

    processed_df["debt_to_income"] = processed_df["existing_debts"] / processed_df["income"]
    processed_df["loan_to_income"] = processed_df["loan_amount"] / processed_df["income"]

    monthly_rate = ANNUAL_INTEREST_RATE / 12
    months = processed_df["loan_term"]
    principal = processed_df["loan_amount"]
    denominator = 1 - (1 + monthly_rate) ** (-months)
    processed_df["monthly_payment"] = (principal * monthly_rate) / denominator
    processed_df["payment_to_income"] = processed_df["monthly_payment"] / (processed_df["income"] / 12)

    return _clip_numeric_outliers(processed_df)


def main() -> None:
    """Generate loan data, save CSV, preprocess it, and report basic stats."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    loan_df = generate_synthetic_loan_data()
    loan_df.to_csv(DATA_PATH, index=False)

    processed_df = preprocess_loan_data(loan_df)
    default_rate = processed_df["default"].mean() * 100

    LOGGER.info("Processed shape: %s", processed_df.shape)
    LOGGER.info("Default rate: %.2f%%", default_rate)


if __name__ == "__main__":
    main()


__all__ = [
    "LabelEncoder",
    "generate_synthetic_loan_data",
    "main",
    "preprocess_loan_data",
]
