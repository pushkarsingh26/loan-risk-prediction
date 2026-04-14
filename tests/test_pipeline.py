from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

import predict
from preprocess import preprocess_loan_data


def test_preprocess_output_has_no_null_values(sample_loan_dataframe: pd.DataFrame) -> None:
    processed = preprocess_loan_data(sample_loan_dataframe)

    assert not processed.isnull().any().any()


def test_preprocess_debt_to_income_exists_and_no_division_errors(sample_loan_dataframe: pd.DataFrame) -> None:
    processed = preprocess_loan_data(sample_loan_dataframe)

    assert "debt_to_income" in processed.columns
    assert np.isfinite(processed["debt_to_income"]).all()


def test_preprocess_employment_status_encoded_0_to_3(sample_loan_dataframe: pd.DataFrame) -> None:
    processed = preprocess_loan_data(sample_loan_dataframe)

    assert pd.api.types.is_integer_dtype(processed["employment_status"])
    assert processed["employment_status"].between(0, 3).all()
    assert set(processed["employment_status"].unique()).issubset({0, 1, 2, 3})


def test_train_model_creates_artifact(trained_model_artifact: Path) -> None:
    assert trained_model_artifact.exists()


def test_saved_model_has_predict_proba(trained_model_artifact: Path) -> None:
    artifact = joblib.load(trained_model_artifact)

    assert "model" in artifact
    assert hasattr(artifact["model"], "predict_proba")


def test_predict_loan_risk_output_shape_and_types(
    trained_model_artifact: Path,
    sample_predict_input: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = joblib.load(trained_model_artifact)
    monkeypatch.setattr(predict, "_load_model_artifact", lambda model_path=predict.MODEL_PATH: artifact)

    result = predict.predict_loan_risk(sample_predict_input)

    assert set(result.keys()) == {"risk_label", "probability", "risk_score", "risk_factors"}
    assert result["risk_label"] in {"High Risk", "Low Risk"}
    assert isinstance(result["probability"], float)
    assert 0.0 <= result["probability"] <= 1.0


def test_predict_loan_risk_negative_income_raises_value_error(
    trained_model_artifact: Path,
    invalid_predict_input: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = joblib.load(trained_model_artifact)
    monkeypatch.setattr(predict, "_load_model_artifact", lambda model_path=predict.MODEL_PATH: artifact)

    with pytest.raises(ValueError):
        predict.predict_loan_risk(invalid_predict_input)
