# AI Doctor Recommender — Ubaid Ullah Farooqui

Recommends a specialist and matching doctors from a patient's symptoms.
Part of the Hoku Health Care platform (TechNexus VU 14-day sprint).

## Status
- **Day 1** — static symptom → specialist map + stubbed endpoint ✓
- **Day 2** — real doctors from the database (join `doctors` + `users`) ✓
- **Day 3** — Groq AI classifier picks the specialist; keyword map is the fallback ✓

## How it works
1. **Specialist** is chosen by a Groq LLM reading the free-text symptoms,
   constrained to the six specialties in Hoku's `doctors` table. If the AI is
   unavailable or answers off-list, a keyword map is used instead.
2. **Doctors** for that specialist are pulled from the database (`doctors`
   joined to `users`), sorted by experience.
3. The response's `matchedBy` field reports which path chose the specialist:
   `"ai"` or `"keyword"`.

## Run (Windows / PowerShell)
```powershell
cd hoku-health-ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env        # first time only, then add your Groq key

# create + populate a local test DB (uses DATABASE_URL from .env)
python -m doctor_recommender.seed

uvicorn doctor_recommender.app:app --reload --port 8010
```
Swagger docs: http://127.0.0.1:8010/docs

## Configuration (.env)
```
GROQ_API_KEY=gsk_...                         # from console.groq.com
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
DATABASE_URL=sqlite:///./hoku_local.db       # local dev; Postgres in production
AI_TIMEOUT_SECONDS=4
```
`.env` is gitignored — never commit your key. Without a key the service still
works; it just uses the keyword map (`matchedBy: "keyword"`).

## AI classifier (Day 3)
Groq is OpenAI-compatible, so the standard `openai` SDK is pointed at Groq's
servers. The AI handles phrasing the keyword map would miss, e.g.
`"my newborn keeps crying and feels very warm"` → Child Specialist.

Falls back to the keyword map automatically when:
- no `GROQ_API_KEY` is set
- the API errors or times out (stays under the 4s NFR-02)
- the AI answers with anything off the six-specialty list

> **Dependency note:** `httpx` is pinned to `0.28.1`. Older/newer combinations
> can raise `Client.__init__() got an unexpected keyword argument 'proxies'`
> with the `openai` SDK. Do not un-pin it without testing the Groq call.

## Endpoint
`POST /api/ai/recommend-doctor`

Request:
```json
{ "symptoms": ["chest pain"], "location": "Lahore" }
```
Response:
```json
{
  "recommendedSpecialist": "Cardiologist",
  "matchedBy": "ai",
  "doctors": [
    { "doctorId": 1, "name": "Dr. Ali Khan", "specialty": "Cardiologist",
      "experience": "10 years", "consultationFee": 3000.0,
      "hospital": "Hoku Health Care", "availability": "Not set" }
  ],
  "note": "",
  "urgency": "medium - Please book an appointment soon",
  "disclaimer": "Please consult a doctor for proper diagnosis."
}
```

## Database
Same code runs against two databases — only `DATABASE_URL` changes:
- **Local dev:** `sqlite:///./hoku_local.db` (run `seed.py` to populate)
- **Production:** Talha's PostgreSQL URL from `hoku-health-backend/.env`

`seed.py` is a dev convenience only — never run it against production; Talha
owns and migrates those tables.

## Design guarantees
- **No hallucinated doctors.** No match → empty `doctors` list + explanatory
  `note`. The AI is also constrained to six real specialties.
- **No hallucinated specialties.** Off-list AI answers are rejected and the
  keyword map takes over.
- **Never a 500.** DB down or AI down → the endpoint still returns 200 with a
  safe fallback.

## Known placeholders (built on later days)
- `urgency` is currently a fixed `"medium ..."` string — real red-flag scoring
  lands on **Day 4**.
- `availability` is `"Not set"` — the real schedule window lands on **Day 5**
  via the `doctor_availability` table.

## Roadmap
- **Day 4** — red-flag urgency scoring (low / medium / high)
- **Day 5** — availability matching via `doctor_availability`
- **Day 6** — Service Recommender (Home Health / Palliative / Hospice)
- **Day 7** — edge cases + Postman suite + handover

## Note for Talha
`.env DATABASE_URL` must match `hoku-health-backend/.env` before this reads
production data, or my queries hit a different `doctors` table.