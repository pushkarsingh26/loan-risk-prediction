from __future__ import annotations

from typing import Any, Callable

from fastapi.testclient import TestClient

import app.api as api_module


def _run_with_summary(test_name: str, test_body: Callable[[], None]) -> None:
    """Run test body and print PASSED/FAILED summary."""
    try:
        test_body()
        print(f"PASSED: {test_name}")
    except Exception:
        print(f"FAILED: {test_name}")
        raise


def test_health_endpoint_returns_ok_status() -> None:
    def body() -> None:
        client = TestClient(api_module.app)
        response = client.get("/health")

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"

    _run_with_summary("GET /health returns status ok", body)


def test_predict_with_valid_input_returns_required_fields(monkeypatch) -> None:
    def body() -> None:
        client = TestClient(api_module.app)

        def mock_predict_loan_risk(_: dict[str, Any]) -> dict[str, Any]:
            return {
                "risk_label": "Low Risk",
                "probability": 0.23,
                "risk_score": 23,
                "risk_factors": ["Strong credit and affordability profile"],
            }

        monkeypatch.setattr(api_module, "predict_loan_risk", mock_predict_loan_risk)

        valid_payload = {
            "age": 35,
            "income": 60000,
            "loan_amount": 15000,
            "credit_score": 680,
            "employment_status": "Employed",
            "loan_term": 36,
            "existing_debts": 5000,
        }

        response = client.post("/predict", json=valid_payload)
        assert response.status_code == 200

        payload = response.json()
        assert "risk_label" in payload
        assert "probability" in payload
        assert "risk_score" in payload

    _run_with_summary("POST /predict valid input returns core fields", body)


def test_predict_with_credit_score_below_range_returns_422() -> None:
    def body() -> None:
        client = TestClient(api_module.app)

        invalid_payload = {
            "age": 35,
            "income": 60000,
            "loan_amount": 15000,
            "credit_score": 200,
            "employment_status": "Employed",
            "loan_term": 36,
            "existing_debts": 5000,
        }

        response = client.post("/predict", json=invalid_payload)
        assert response.status_code == 422

    _run_with_summary("POST /predict credit_score=200 returns 422", body)


def test_predict_with_zero_income_returns_422() -> None:
    def body() -> None:
        client = TestClient(api_module.app)

        invalid_payload = {
            "age": 35,
            "income": 0,
            "loan_amount": 15000,
            "credit_score": 680,
            "employment_status": "Employed",
            "loan_term": 36,
            "existing_debts": 5000,
        }

        response = client.post("/predict", json=invalid_payload)
        assert response.status_code == 422

    _run_with_summary("POST /predict income=0 returns 422", body)


def test_cors_headers_present_in_response() -> None:
    def body() -> None:
        client = TestClient(api_module.app)
        response = client.get("/health", headers={"Origin": "http://example.com"})

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    _run_with_summary("CORS headers present in response", body)
