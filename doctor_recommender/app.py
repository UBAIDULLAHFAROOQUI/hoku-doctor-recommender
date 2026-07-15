"""
AI Doctor Recommender — FastAPI service.  (Ubaid Ullah Farooqui)

Day 3: the specialist is chosen by an OpenAI classifier (constrained to the
six real specialties), falling back to the Day 2 keyword map when the AI is
unavailable. `matchedBy` reports which path was used. Doctors still come from
the database; an empty list is explained by `note`, never a fabricated doctor.

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
    version="0.6.0 (Day 6)",
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
    duration: str | None = Field(
        default=None,
        examples=["3 days"],
        description="Optional: how long symptoms have lasted, e.g. '5 days'.",
    )
    preferredDay: str | None = Field(
        default=None,
        examples=["Monday"],
        description="Optional: only return doctors available this weekday.",
    )


class DoctorCard(BaseModel):
    doctorId: int
    name: str
    specialty: str
    experience: str
    consultationFee: float | None = None
    hospital: str
    availability: str


class RecommendedService(BaseModel):
    serviceId: int | None = None
    name: str
    price: float | None = None
    matchedBy: str  # "ai" or "keyword"


class RecommendResponse(BaseModel):
    recommendedSpecialist: str
    matchedBy: str  # "ai" or "keyword"
    doctors: list[DoctorCard]
    note: str
    recommendedService: RecommendedService
    urgencyLevel: str  # "low" | "medium" | "high"
    urgency: str
    disclaimer: str


@app.get("/health", tags=["meta"])
def health() -> dict:
    """Liveness probe."""
    return {"status": "ok", "service": "doctor_recommender", "day": 6}


@app.post("/api/ai/recommend-doctor", response_model=RecommendResponse, tags=["ai"])
def recommend_doctor(payload: RecommendRequest) -> RecommendResponse:
    """
    Map symptoms -> specialist -> real doctors from the database.

    Returns an empty `doctors` list with an explanatory `note` when no matching
    doctor exists or the directory is unavailable — never a fabricated doctor.
    """
    result = recommend(
        payload.symptoms, payload.location, payload.duration, payload.preferredDay
    )
    return RecommendResponse(**result)