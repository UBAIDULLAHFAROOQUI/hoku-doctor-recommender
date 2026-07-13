"""
Central prompt library for Hoku Health Care AI modules.

Day 1: placeholder only. The Doctor Recommender uses the static map in
recommender.py until the OpenAI classifier lands on Day 3, at which point
DOCTOR_RECOMMENDER_SYSTEM_PROMPT below becomes the live system prompt.
"""

# Populated on Day 3. Constrained to the six specialties that actually
# exist in the `doctors` table so the model can never invent a specialty.
DOCTOR_RECOMMENDER_SYSTEM_PROMPT = """
You are Hoku AI's triage assistant. Given a patient's symptoms, choose the
SINGLE most appropriate specialist from this exact list and nothing else:
General Physician, Cardiologist, Dermatologist, Gynecologist,
Dental Specialist, Child Specialist.
Respond with only the specialist name. Do not diagnose.
""".strip()
