"""
AI Doctor Recommender — core logic.  (Ubaid Ullah Farooqui)

Day 1 scope: a static symptom -> specialist map and a matcher that turns a
list of symptoms into a recommended specialist. No database, no OpenAI yet.

Roadmap this file follows:
  Day 2  -> query the real `doctors` table instead of SAMPLE_DOCTORS
  Day 3  -> replace map lookup with an OpenAI classifier (map = fallback)
  Day 4  -> urgency scoring from red-flag symptoms
  Day 5  -> availability matching against `doctor_availability`
"""

from __future__ import annotations

# The six specialties that exist in Hoku's `doctors` table (brief §1.2).
# Anything unmatched falls back to General Physician.
FALLBACK_SPECIALIST = "General Physician"

# Static symptom -> specialist map. Keys are lowercase single keywords that
# we look for inside each symptom string, so "bad chest pain" still matches
# "chest pain". Ordered roughly specific -> general.
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

# Day-1 stand-in for the `doctors` table. Replaced by a real query on Day 2.
SAMPLE_DOCTORS: dict[str, list[dict]] = {
    "Cardiologist": [
        {
            "name": "Dr. Ali Khan",
            "specialty": "Cardiologist",
            "experience": "10 years",
            "hospital": "Hoku Health Care",
            "availability": "Monday-Friday, 9AM-5PM",
        }
    ],
    "General Physician": [
        {
            "name": "Dr. Sara Ahmed",
            "specialty": "General Physician",
            "experience": "7 years",
            "hospital": "Hoku Health Care",
            "availability": "Monday-Saturday, 10AM-6PM",
        }
    ],
    "Dermatologist": [
        {
            "name": "Dr. Hina Raza",
            "specialty": "Dermatologist",
            "experience": "8 years",
            "hospital": "Hoku Health Care",
            "availability": "Tuesday-Saturday, 11AM-4PM",
        }
    ],
}


def match_specialist(symptoms: list[str]) -> str:
    """
    Return the best-matching specialist for a list of symptom strings.

    Scans each symptom for any keyword in SYMPTOM_SPECIALTY_MAP. The first
    keyword hit wins (map is ordered specific -> general). Falls back to
    General Physician when nothing matches, so we never return None.
    """
    for symptom in symptoms:
        text = symptom.strip().lower()
        for keyword, specialist in SYMPTOM_SPECIALTY_MAP.items():
            if keyword in text:
                return specialist
    return FALLBACK_SPECIALIST


def find_doctors(specialist: str) -> list[dict]:
    """
    Day 1: return sample doctors for the specialist from SAMPLE_DOCTORS.
    Day 2: this becomes a PostgreSQL query on the `doctors` table.
    """
    return SAMPLE_DOCTORS.get(specialist, SAMPLE_DOCTORS[FALLBACK_SPECIALIST])


def recommend(symptoms: list[str], location: str | None = None) -> dict:
    """
    Build the full recommendation response (brief §10.4).

    urgency is a Day-1 placeholder — real red-flag scoring lands on Day 4.
    """
    specialist = match_specialist(symptoms)
    doctors = find_doctors(specialist)
    return {
        "recommendedSpecialist": specialist,
        "doctors": doctors,
        # Placeholder until Day 4 urgency scoring:
        "urgency": "medium - Please book an appointment soon",
        "disclaimer": "Please consult a doctor for proper diagnosis.",
    }
