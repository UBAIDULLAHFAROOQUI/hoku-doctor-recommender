# AI Doctor Recommender — Ubaid Ullah Farooqui

Recommends a specialist and matching doctors from a patient's symptoms.
Part of the Hoku Health Care platform (TechNexus VU 14-day sprint).

## Day 1 status
Static symptom → specialist map + stubbed doctors. Endpoint contract is
final so the frontend can wire the UI now; DB and LLM swap in later without
changing response shapes.

## Run (Windows / PowerShell)
```powershell
cd hoku-health-ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn doctor_recommender.app:app --reload --port 8010
```
Swagger docs: http://127.0.0.1:8010/docs

## Endpoint
`POST /api/ai/recommend-doctor`

Request:
```json
{ "symptoms": ["chest pain", "shortness of breath"], "location": "Lahore" }
```
Response:
```json
{
  "recommendedSpecialist": "Cardiologist",
  "doctors": [{ "name": "Dr. Ali Khan", "specialty": "Cardiologist",
               "experience": "10 years", "hospital": "Hoku Health Care",
               "availability": "Monday-Friday, 9AM-5PM" }],
  "urgency": "medium - Please book an appointment soon",
  "disclaimer": "Please consult a doctor for proper diagnosis."
}
```

## Roadmap
- **Day 2** — query real `doctors` table (replaces SAMPLE_DOCTORS)
- **Day 3** — OpenAI classifier (map becomes fallback)
- **Day 4** — red-flag urgency scoring
- **Day 5** — availability matching via `doctor_availability`
- **Day 6** — Service Recommender (Home Health / Palliative / Hospice)
- **Day 7** — edge cases + Postman suite + handover

## Note for Talha
`shared/config.py DATABASE_URL` must match `hoku-health-backend/.env` before
Day 2, or my queries hit a different `doctors` table than production.
