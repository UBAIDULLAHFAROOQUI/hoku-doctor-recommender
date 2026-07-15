"""
Service (care-type) recommender.  (Ubaid Ullah Farooqui)  — Day 6

Classifies a patient's situation into one of Hoku's three services:
Home Health, Palliative Care, or Hospice Care. Uses Groq (with a keyword
fallback), constrained to those three — never invents a service.

Home Health is the default for routine cases; the others require clear
serious-illness or end-of-life signals.
"""

from __future__ import annotations

import logging

from shared.config import settings
from shared.prompts import SERVICE_RECOMMENDER_SYSTEM_PROMPT

logger = logging.getLogger("doctor_recommender")

DEFAULT_SERVICE = "Home Health"

VALID_SERVICES = {"Home Health", "Palliative Care", "Hospice Care"}

# Keyword fallback. Checked most-specific first: hospice > palliative > home.
HOSPICE_KEYWORDS = {
    "hospice", "end of life", "end-of-life", "terminal", "dying",
    "final stage", "no cure", "last days",
}
PALLIATIVE_KEYWORDS = {
    "palliative", "comfort care", "serious illness", "chronic pain",
    "cancer", "life-limiting", "advanced illness", "chemotherapy",
}


def validate_service(answer: str) -> str | None:
    """Return the canonical service name if `answer` is on-list, else None."""
    cleaned = (answer or "").strip().rstrip(".").strip()
    for service in VALID_SERVICES:
        if service.lower() == cleaned.lower():
            return service
    return None


def keyword_service(symptoms: list[str]) -> str:
    """Fallback: pick a service from keywords, defaulting to Home Health."""
    text = " ".join(s.strip().lower() for s in symptoms)
    if any(k in text for k in HOSPICE_KEYWORDS):
        return "Hospice Care"
    if any(k in text for k in PALLIATIVE_KEYWORDS):
        return "Palliative Care"
    return DEFAULT_SERVICE


def classify_service_with_ai(symptoms: list[str]) -> str | None:
    """Ask Groq for the care type, constrained to the three services."""
    if not settings.GROQ_API_KEY:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL,
            timeout=settings.AI_TIMEOUT_SECONDS,
        )
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            temperature=0,
            max_tokens=10,
            messages=[
                {"role": "system", "content": SERVICE_RECOMMENDER_SYSTEM_PROMPT},
                {"role": "user", "content": "Situation: " + ", ".join(symptoms)},
            ],
        )
        service = validate_service(response.choices[0].message.content)
        if service is None:
            logger.warning("AI returned off-list service: %r",
                           response.choices[0].message.content)
        return service
    except Exception as exc:
        logger.warning("AI service classifier unavailable: %s", exc)
        return None


def classify_service(symptoms: list[str]) -> tuple[str, str]:
    """Return (service_name, method). AI first, keyword fallback."""
    ai_service = classify_service_with_ai(symptoms)
    if ai_service:
        return ai_service, "ai"
    return keyword_service(symptoms), "keyword"
