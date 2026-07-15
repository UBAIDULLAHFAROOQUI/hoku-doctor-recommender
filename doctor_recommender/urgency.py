"""
Urgency scoring for the Doctor Recommender.  (Ubaid Ullah Farooqui)  — Day 4

Turns a list of symptoms into an urgency level (low / medium / high) with an
actionable message. Errs toward caution: anything resembling a red flag is
escalated to "high — see a doctor immediately".

This is heuristic triage to route patients faster, NOT a medical diagnosis.
Every recommender response still carries the consult-a-doctor disclaimer.
"""

from __future__ import annotations

import re

# Red flags -> HIGH. Immediate, potentially life-threatening presentations.
# Kept broad on purpose; a false "high" is safe, a missed one is not.
RED_FLAG_KEYWORDS = {
    "chest pain",
    "shortness of breath",
    "difficulty breathing",
    "trouble breathing",
    "can't breathe",
    "cannot breathe",
    "severe bleeding",
    "heavy bleeding",
    "bleeding heavily",
    "unconscious",
    "loss of consciousness",
    "fainting",
    "fainted",
    "passed out",
    "seizure",
    "convulsion",
    "stroke",
    "slurred speech",
    "paralysis",
    "numb on one side",
    "blue lips",
    "choking",
    "severe allergic",
    "anaphylaxis",
    "heart attack",
    "coughing blood",
    "vomiting blood",
    "suicidal",
}

# Moderate concerns -> at least MEDIUM.
MODERATE_KEYWORDS = {
    "high fever",
    "persistent vomiting",
    "severe vomiting",
    "dehydration",
    "severe pain",
    "severe headache",
    "broken bone",
    "fracture",
    "deep cut",
    "infection",
    "swelling",
    "dizziness",
    "blood in",
    "unable to eat",
    "can't keep food",
}

# If a patient reports at least this many distinct symptoms, bump to MEDIUM.
MANY_SYMPTOMS_THRESHOLD = 3

MESSAGES = {
    "high": "high - Please see a doctor immediately",
    "medium": "medium - Please book an appointment soon",
    "low": "low - Monitor your symptoms and book if they persist",
}


def _contains_any(text: str, keywords: set[str]) -> bool:
    return any(kw in text for kw in keywords)


def _duration_days(duration: str | None) -> int:
    """Extract a leading number of days from strings like '5 days' / '2 weeks'."""
    if not duration:
        return 0
    text = duration.lower()
    match = re.search(r"(\d+)", text)
    if not match:
        return 0
    n = int(match.group(1))
    if "week" in text:
        return n * 7
    if "month" in text:
        return n * 30
    return n  # assume days


def score_urgency(symptoms: list[str], duration: str | None = None) -> tuple[str, str]:
    """
    Return (level, message) where level is 'low' | 'medium' | 'high'.

    Rules, highest priority first:
      1. any red-flag symptom            -> high
      2. any moderate symptom            -> medium
      3. 3+ distinct symptoms            -> medium
      4. symptom persisting 7+ days      -> medium
      5. otherwise                       -> low
    """
    joined = " ".join(s.strip().lower() for s in symptoms)

    if _contains_any(joined, RED_FLAG_KEYWORDS):
        return "high", MESSAGES["high"]

    if _contains_any(joined, MODERATE_KEYWORDS):
        return "medium", MESSAGES["medium"]

    if len([s for s in symptoms if s.strip()]) >= MANY_SYMPTOMS_THRESHOLD:
        return "medium", MESSAGES["medium"]

    if _duration_days(duration) >= 7:
        return "medium", MESSAGES["medium"]

    return "low", MESSAGES["low"]
