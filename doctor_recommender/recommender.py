"""
AI Doctor Recommender — core logic.  (Ubaid Ullah Farooqui)

Day 2: find_doctors() now queries the REAL `doctors` table via the repository.
The static symptom->specialist map still decides WHICH specialist; the DB
decides WHICH doctors of that specialist to return.

Roadmap:
  Day 3  -> replace the map with an OpenAI classifier (map = fallback)
  Day 4  -> urgency scoring from red-flag symptoms
  Day 5  -> real availability window from doctor_availability
"""

from __future__ import annotations

import logging

from doctor_recommender.repository import get_doctors_by_specialty

logger = logging.getLogger("doctor_recommender")

# The six specialties that exist in Hoku's `doctors` table (brief §1.2).
FALLBACK_SPECIALIST = "General Physician"

# Static symptom -> specialist map. Keys are lowercase keywords matched inside
# each symptom string, so "bad chest pain" still matches "chest pain".
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


def match_specialist(symptoms: list[str]) -> str:
    """Return the best-matching specialist, falling back to General Physician."""
    for symptom in symptoms:
        text = symptom.strip().lower()
        for keyword, specialist in SYMPTOM_SPECIALTY_MAP.items():
            if keyword in text:
                return specialist
    return FALLBACK_SPECIALIST


def find_doctors(specialist: str) -> tuple[list[dict], str]:
    """
    Fetch real doctors for a specialist from the database.

    Returns (doctors, note). `note` explains an empty list to the patient:
      - DB reachable but no match   -> "no doctor currently available"
      - DB unreachable (dev/outage) -> service-unavailable message
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


def recommend(symptoms: list[str], location: str | None = None) -> dict:
    """Build the full recommendation response (brief §10.4)."""
    specialist = match_specialist(symptoms)
    doctors, note = find_doctors(specialist)
    return {
        "recommendedSpecialist": specialist,
        "doctors": doctors,
        "note": note,  # empty string when doctors were found
        # Placeholder until Day 4 urgency scoring:
        "urgency": "medium - Please book an appointment soon",
        "disclaimer": "Please consult a doctor for proper diagnosis.",
    }