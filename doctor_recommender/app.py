"""
AI Doctor Recommender — FastAPI service.  (Ubaid Ullah Farooqui)

Day 2: POST /api/ai/recommend-doctor now returns REAL doctors from the
database (name, doctorId, specialty, experience, consultationFee). A `note`
field explains an empty doctor list instead of inventing a doctor.

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
    version="0.2.0 (Day 2)",
    description="Recommends a specialist and real doctors from patient symptoms.",
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
        description="Optional patient city (used for filtering from a later day).",
    )


class DoctorCard(BaseModel):
    doctorId: int
    name: str
    specialty: str
    experience: str
    consultationFee: float | None = None
    hospital: str
    availability: str


class RecommendResponse(BaseModel):
    recommendedSpecialist: str
    doctors: list[DoctorCard]
    note: str
    urgency: str
    disclaimer: str


@app.get("/health", tags=["meta"])
def health() -> dict:
    """Liveness probe."""
    return {"status": "ok", "service": "doctor_recommender", "day": 2}


@app.post("/api/ai/recommend-doctor", response_model=RecommendResponse, tags=["ai"])
def recommend_doctor(payload: RecommendRequest) -> RecommendResponse:
    """
    Map symptoms -> specialist -> real doctors from the database.

    Returns an empty `doctors` list with an explanatory `note` when no matching
    doctor exists or the directory is unavailable — never a fabricated doctor.
    """
    result = recommend(payload.symptoms, payload.location)
    return RecommendResponse(**result)