"""
AI Doctor Recommender — FastAPI service.  (Ubaid Ullah Farooqui)

Day 1: exposes POST /api/ai/recommend-doctor returning the full response
contract (brief §10.4) driven by the static map in recommender.py, so the
frontend (Sibgha) can wire the Symptom Checker UI against real shapes today.

Run locally:
    uvicorn doctor_recommender.app:app --reload --port 8010
Swagger:
    http://127.0.0.1:8010/docs
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from doctor_recommender.recommender import recommend

app = FastAPI(
    title="Hoku Health Care — AI Doctor Recommender",
    version="0.1.0 (Day 1)",
    description="Recommends a specialist and doctors from patient symptoms.",
)

# CORS open in dev so the React app on :5173 can call this. Tighten before deploy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    """Request body for the recommender (brief §10.4)."""

    symptoms: list[str] = Field(
        ...,
        min_length=1,
        examples=[["chest pain", "shortness of breath"]],
        description="One or more symptom phrases.",
    )
    location: str | None = Field(
        default=None,
        examples=["Lahore"],
        description="Optional patient city (used for filtering from Day 2).",
    )


class DoctorCard(BaseModel):
    name: str
    specialty: str
    experience: str
    hospital: str
    availability: str


class RecommendResponse(BaseModel):
    recommendedSpecialist: str
    doctors: list[DoctorCard]
    urgency: str
    disclaimer: str


@app.get("/health", tags=["meta"])
def health() -> dict:
    """Liveness probe."""
    return {"status": "ok", "service": "doctor_recommender", "day": 1}


@app.post("/api/ai/recommend-doctor", response_model=RecommendResponse, tags=["ai"])
def recommend_doctor(payload: RecommendRequest) -> RecommendResponse:
    """
    Map symptoms -> specialist -> doctors.

    Day 1 uses the static keyword map and sample doctors; the response shape
    is final so no frontend rewiring is needed when the DB and LLM land.
    """
    result = recommend(payload.symptoms, payload.location)
    return RecommendResponse(**result)
