"""FastAPI service exposing loan risk predictions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.predict import predict_loan_risk

MODEL_PATH = Path("models/loan_model.pkl")

app = FastAPI(title="Loan Risk API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoanPredictionRequest(BaseModel):
    """Input payload for loan risk prediction."""

    age: int = Field(..., ge=18, le=100)
    income: float = Field(..., gt=0)
    loan_amount: float = Field(..., gt=0)
    credit_score: int = Field(..., ge=300, le=850)
    employment_status: str = Field(..., min_length=1)
    loan_term: int = Field(..., gt=0)
    existing_debts: float = Field(..., ge=0)


class LoanPredictionResponse(BaseModel):
    """Prediction response payload."""

    risk_label: str
    probability: float
    risk_score: int
    risk_factors: list[str]


def _is_model_loaded() -> bool:
    """Return True when the model artifact exists and can be loaded."""
    if not MODEL_PATH.exists():
        return False
    try:
        joblib.load(MODEL_PATH)
        return True
    except Exception:
        return False


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    model_status = "loaded" if _is_model_loaded() else "not_loaded"
    return {"status": "ok", "model": model_status}


@app.post("/predict", response_model=LoanPredictionResponse)
def predict(request: LoanPredictionRequest) -> dict[str, Any]:
    """Run loan risk prediction from validated request data."""
    try:
        return predict_loan_risk(request.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc


if __name__ == "__main__":
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
