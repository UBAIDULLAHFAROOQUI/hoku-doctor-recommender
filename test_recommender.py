"""
Test suite for the AI Doctor Recommender.  (Ubaid Ullah Farooqui)  — Day 7

Run:
    pip install pytest
    pytest -v

Uses a temporary SQLite DB seeded with sample data, and forces keyword mode
(no GROQ key) so results are deterministic and no network is needed.
"""

import os
import tempfile

import pytest

# Force a temp DB + keyword mode BEFORE importing the app.
_TMP_DB = os.path.join(tempfile.gettempdir(), "hoku_test.db")
if os.path.exists(_TMP_DB):
    os.remove(_TMP_DB)
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB}"
os.environ.pop("GROQ_API_KEY", None)

from fastapi.testclient import TestClient  # noqa: E402

from doctor_recommender.app import app  # noqa: E402
from doctor_recommender.seed import run as seed_run  # noqa: E402
from doctor_recommender.urgency import score_urgency  # noqa: E402
from doctor_recommender.classifier import validate_specialist  # noqa: E402
from doctor_recommender.service_recommender import (  # noqa: E402
    keyword_service,
    validate_service,
)

seed_run()
client = TestClient(app)


def post(payload):
    return client.post("/api/ai/recommend-doctor", json=payload)


# --- health ---
def test_health():
    assert client.get("/health").json()["status"] == "ok"


# --- specialist matching (Day 1/3) ---
@pytest.mark.parametrize("symptom,expected", [
    ("chest pain", "Cardiologist"),
    ("skin rash", "Dermatologist"),
    ("tooth ache", "Dental Specialist"),
    ("something totally unmapped", "General Physician"),  # safe fallback
])
def test_specialist(symptom, expected):
    assert post({"symptoms": [symptom]}).json()["recommendedSpecialist"] == expected


# --- real doctors from DB (Day 2) ---
def test_doctors_from_db():
    doctors = post({"symptoms": ["chest pain"]}).json()["doctors"]
    assert len(doctors) == 2
    assert doctors[0]["experience"] == "10 years"  # sorted, most experienced first
    assert doctors[0]["doctorId"] is not None


# --- urgency scoring (Day 4) ---
@pytest.mark.parametrize("symptoms,level", [
    (["chest pain"], "high"),
    (["shortness of breath"], "high"),
    (["mild cold"], "low"),
    (["fever", "cough", "sore throat"], "medium"),
])
def test_urgency(symptoms, level):
    assert score_urgency(symptoms)[0] == level


def test_urgency_duration_bump():
    assert score_urgency(["sore throat"], "10 days")[0] == "medium"


# --- availability (Day 5) ---
def test_availability_shows_schedule():
    doctors = post({"symptoms": ["chest pain"]}).json()["doctors"]
    assert doctors[0]["availability"] != "Not set"
    assert ":" in doctors[0]["availability"]  # has a time window


def test_preferred_day_filter():
    r = post({"symptoms": ["chest pain"], "preferredDay": "Tuesday"}).json()
    names = [d["name"] for d in r["doctors"]]
    assert "Dr. Zara Sheikh" in names
    assert "Dr. Ali Khan" not in names  # works Mon/Wed/Fri only


def test_no_doctor_on_empty_day():
    r = post({"symptoms": ["chest pain"], "preferredDay": "Sunday"}).json()
    assert r["doctors"] == []
    assert "Sunday" in r["note"]


# --- service recommender (Day 6) ---
@pytest.mark.parametrize("symptoms,service", [
    (["chest pain"], "Home Health"),
    (["cancer, needs comfort care"], "Palliative Care"),
    (["terminal, end of life care"], "Hospice Care"),
])
def test_service(symptoms, service):
    assert post({"symptoms": symptoms}).json()["recommendedService"]["name"] == service


def test_service_has_real_id():
    svc = post({"symptoms": ["chest pain"]}).json()["recommendedService"]
    assert svc["serviceId"] is not None


# --- edge cases (Day 7) ---
def test_empty_symptoms_rejected():
    assert post({"symptoms": []}).status_code == 422


def test_blank_symptoms_rejected():
    assert post({"symptoms": ["", "   "]}).status_code == 422


def test_whitespace_is_stripped():
    r = post({"symptoms": ["  chest pain  "]})
    assert r.status_code == 200
    assert r.json()["recommendedSpecialist"] == "Cardiologist"


def test_disclaimer_always_present():
    assert "consult a doctor" in post({"symptoms": ["headache"]}).json()["disclaimer"].lower()


# --- pure validators ---
def test_validate_specialist():
    assert validate_specialist("cardiologist.") == "Cardiologist"
    assert validate_specialist("Neurologist") is None


def test_validate_service():
    assert validate_service("home health") == "Home Health"
    assert validate_service("Spa Day") is None


def test_keyword_service_default():
    assert keyword_service(["random symptom"]) == "Home Health"
