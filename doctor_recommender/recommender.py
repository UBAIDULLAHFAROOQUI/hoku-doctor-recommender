"""
AI Doctor Recommender — core logic.  (Ubaid Ullah Farooqui)

Day 4: urgency is now scored from the symptoms (red flag -> high) instead of
a fixed placeholder. Specialist still comes from the AI classifier (Day 3)
with the keyword map as fallback; doctors still come from the DB (Day 2).

Roadmap:
  Day 5  -> real availability window from doctor_availability
"""

from __future__ import annotations

import logging

from doctor_recommender.classifier import classify_with_ai
from doctor_recommender.repository import get_doctors_by_specialty
from doctor_recommender.urgency import score_urgency

logger = logging.getLogger("doctor_recommender")

# The six specialties that exist in Hoku's `doctors` table (brief §1.2).
FALLBACK_SPECIALIST = "General Physician"

# Static symptom -> specialist map. Now the FALLBACK when the AI is unavailable.
# Keys are lowercase keywords matched inside each symptom string, so
# "bad chest pain" still matches "chest pain".
SYMPTOM_SPECIALTY_MAP: dict[str, str] = {
    # Cardiologist
    "chest pain": "Cardiologist",
    "shortness of breath": "Cardiologist",
    "palpitation": "Cardiologist",
    "heart": "Cardiologist",
    # Dermatologist
    "rash": "Dermatologist",
    "acne": "Dermatologist",
    "itching": "Dermatologist",
    "skin": "Dermatologist",
    "eczema": "Dermatologist",
    # Gynecologist
    "pregnancy": "Gynecologist",
    "menstrual": "Gynecologist",
    "period": "Gynecologist",
    # Dental Specialist
    "toothache": "Dental Specialist",
    "tooth": "Dental Specialist",
    "gum": "Dental Specialist",
    # Child Specialist
    "child fever": "Child Specialist",
    "infant": "Child Specialist",
    "newborn": "Child Specialist",
    # General Physician (common/systemic)
    "fever": "General Physician",
    "cough": "General Physician",
    "cold": "General Physician",
    "headache": "General Physician",
    "sore throat": "General Physician",
    "fatigue": "General Physician",
}


def keyword_match(symptoms: list[str]) -> str:
    """Fallback matcher: scan symptoms for a mapped keyword."""
    for symptom in symptoms:
        text = symptom.strip().lower()
        for keyword, specialist in SYMPTOM_SPECIALTY_MAP.items():
            if keyword in text:
                return specialist
    return FALLBACK_SPECIALIST


def match_specialist(symptoms: list[str]) -> tuple[str, str]:
    """
    Return (specialist, method). Tries the AI classifier first; if it is
    unavailable or returns something off-list, falls back to the keyword map.
    method is "ai" or "keyword" — handy for demos and debugging.
    """
    ai_specialist = classify_with_ai(symptoms)
    if ai_specialist:
        return ai_specialist, "ai"
    return keyword_match(symptoms), "keyword"


def find_doctors(specialist: str) -> tuple[list[dict], str]:
    """
    Fetch real doctors for a specialist from the database.

    Returns (doctors, note). `note` explains an empty list to the patient.
    We NEVER invent a doctor to fill an empty result.
    """
    try:
        doctors = get_doctors_by_specialty(specialist)
    except Exception as exc:  # DB down / not yet reachable
        logger.warning("Doctor DB unavailable (%s): %s", specialist, exc)
        return [], "Doctor directory is temporarily unavailable. Please try again shortly."

    if not doctors:
        return [], f"No {specialist} is currently available. Please check back soon."
    return doctors, ""


def recommend(
    symptoms: list[str],
    location: str | None = None,
    duration: str | None = None,
) -> dict:
    """Build the full recommendation response (brief §10.4)."""
    specialist, method = match_specialist(symptoms)
    doctors, note = find_doctors(specialist)
    urgency_level, urgency_message = score_urgency(symptoms, duration)
    return {
        "recommendedSpecialist": specialist,
        "matchedBy": method,  # "ai" or "keyword"
        "doctors": doctors,
        "note": note,  # empty string when doctors were found
        "urgencyLevel": urgency_level,       # "low" | "medium" | "high"
        "urgency": urgency_message,          # human-readable, e.g. "high - ..."
        "disclaimer": "Please consult a doctor for proper diagnosis.",
    }