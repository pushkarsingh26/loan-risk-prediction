from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from preprocess import generate_synthetic_loan_data


@pytest.fixture
def sample_loan_dataframe() -> pd.DataFrame:
    """Synthetic dataset fixture used across preprocessing and training tests."""
    return generate_synthetic_loan_data(n_rows=300, random_state=123)


@pytest.fixture
def sample_predict_input() -> dict[str, Any]:
    """Valid one-row payload for prediction tests."""
    return {
        "age": 34,
        "income": 85000,
        "loan_amount": 18000,
        "credit_score": 710,
        "employment_status": "Employed",
        "loan_term": 36,
        "existing_debts": 9000,
    }


@pytest.fixture
def invalid_predict_input(sample_predict_input: dict[str, Any]) -> dict[str, Any]:
    """Invalid payload with negative income for input validation checks."""
    invalid = dict(sample_predict_input)
    invalid["income"] = -1000
    return invalid


@pytest.fixture
def trained_model_artifact(tmp_path: Path, sample_loan_dataframe: pd.DataFrame, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Train model in isolated temp dirs and return the artifact path."""
    import train_model

    data_dir = tmp_path / "data"
    model_dir = tmp_path / "models"
    data_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)

    data_path = data_dir / "loan_data.csv"
    model_path = model_dir / "loan_model.pkl"

    sample_loan_dataframe.to_csv(data_path, index=False)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(train_model, "DATA_PATH", Path("data/loan_data.csv"))
    monkeypatch.setattr(train_model, "MODEL_PATH", Path("models/loan_model.pkl"))

    train_model.main()

    return model_path
