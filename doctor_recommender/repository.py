"""
Repository layer — the ONLY place that talks to the database.  (Ubaid)

Keeps SQL out of the recommender logic. Returns plain dicts shaped like the
API's DoctorCard so the rest of the code never touches ORM objects.

Day 5 will extend get_doctors_by_specialty() to also read `doctor_availability`
and fill the real availability window instead of the "Not set" placeholder.
"""

from __future__ import annotations

from sqlalchemy import select

from doctor_recommender.models import Doctor, User
from shared.db import SessionLocal

HOSPITAL_NAME = "Hoku Health Care"


def _to_card(doctor: Doctor, user: User) -> dict:
    """Shape one (Doctor, User) row into the API's DoctorCard dict."""
    fee = float(doctor.consultation_fee) if doctor.consultation_fee is not None else None
    years = doctor.experience_years or 0
    return {
        "doctorId": doctor.id,
        "name": user.full_name,
        "specialty": doctor.specialty,
        "experience": f"{years} years",
        "consultationFee": fee,
        "hospital": HOSPITAL_NAME,
        # Day 5 replaces this with the real window from doctor_availability:
        "availability": "Not set",
    }


def get_doctors_by_specialty(specialty: str, only_available: bool = True) -> list[dict]:
    """
    Return real doctors for a specialty, newest-experience first.

    Joins doctors -> users so the name comes from the real users row. Returns
    an empty list when no doctor matches — the caller decides what to tell the
    patient. Never invents a doctor.
    """
    with SessionLocal() as session:
        stmt = (
            select(Doctor, User)
            .join(User, Doctor.user_id == User.id)
            .where(Doctor.specialty == specialty)
            .order_by(Doctor.experience_years.desc().nullslast())
        )
        if only_available:
            stmt = stmt.where(Doctor.is_available.is_(True))

        rows = session.execute(stmt).all()
        return [_to_card(doctor, user) for doctor, user in rows]
