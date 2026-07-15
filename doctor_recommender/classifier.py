"""
AI specialist classifier.  (Ubaid Ullah Farooqui)  — Day 3 (Groq)

Uses Groq (OpenAI-compatible, free tier) to read free-text symptoms and pick
ONE specialist, constrained to the six that exist in Hoku's `doctors` table.
Returns None when the AI is unavailable, times out, or returns anything
off-list — the caller then falls back to the Day 2 keyword map. The AI never
widens the specialist set.

Design guarantees:
  - No API key set        -> returns None (keyword map handles it)
  - Call errors / timeout -> returns None (never raises, never a 500)
  - AI answers off-list   -> returns None (no invented specialties)
"""

from __future__ import annotations

import logging

from shared.config import settings
from shared.prompts import DOCTOR_RECOMMENDER_SYSTEM_PROMPT

logger = logging.getLogger("doctor_recommender")

# The only specialists the recommender may ever return (brief §1.2).
VALID_SPECIALISTS = {
    "General Physician",
    "Cardiologist",
    "Dermatologist",
    "Gynecologist",
    "Dental Specialist",
    "Child Specialist",
}


def validate_specialist(answer: str) -> str | None:
    """Return the canonical specialist name if `answer` is on-list, else None."""
    cleaned = (answer or "").strip().rstrip(".").strip()
    for specialist in VALID_SPECIALISTS:
        if specialist.lower() == cleaned.lower():
            return specialist  # canonical casing
    return None


def classify_with_ai(symptoms: list[str]) -> str | None:
    """
    Ask Groq for the best specialist. Returns a valid specialist name, or
    None if the AI is unavailable / errored / returned something off-list.
    """
    if not settings.GROQ_API_KEY:
        return None  # no key -> let the keyword map handle it

    try:
        # Groq is OpenAI-compatible: same SDK, different base_url + model.
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL,
            timeout=settings.AI_TIMEOUT_SECONDS,  # NFR-02: stay under 4s
        )
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            temperature=0,        # deterministic triage, no creativity
            max_tokens=10,        # we only need a short specialist name
            messages=[
                {"role": "system", "content": DOCTOR_RECOMMENDER_SYSTEM_PROMPT},
                {"role": "user", "content": "Symptoms: " + ", ".join(symptoms)},
            ],
        )
        answer = response.choices[0].message.content
        specialist = validate_specialist(answer)
        if specialist is None:
            logger.warning("AI returned off-list specialist: %r", answer)
        return specialist
    except Exception as exc:  # network, auth, timeout — never propagate
        logger.warning("AI classifier unavailable: %s", exc)
        return None
