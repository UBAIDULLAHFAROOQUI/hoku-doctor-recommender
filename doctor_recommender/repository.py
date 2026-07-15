"""
Repository layer — the ONLY place that talks to the database.  (Ubaid)

Day 5: also reads `doctor_availability` and renders each doctor's real
schedule window into the `availability` field (replacing "Not set"). An
optional preferred_day filters to doctors bookable on that weekday.

Keeps SQL out of the recommender logic. Returns plain dicts shaped like the
API's DoctorCard so the rest of the code never touches ORM objects.
"""

from __future__ import annotations

from sqlalchemy import select

from doctor_recommender.models import Doctor, DoctorAvailability, User
from shared.db import SessionLocal

HOSPITAL_NAME = "Hoku Health Care"

# For sorting availability windows Mon -> Sun.
_DAY_ORDER = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}


def _fmt_time(value) -> str:
    """Render a TIME value as HH:MM, tolerant of time objects or strings."""
    try:
        return value.strftime("%H:%M")
    except AttributeError:
        return str(value)[:5] if value is not None else "?"


def _format_availability(rows: list[DoctorAvailability]) -> str:
    """Turn availability rows into e.g. 'Mon 09:00-13:00, Wed 09:00-13:00'."""
    if not rows:
        return "Not set"
    ordered = sorted(rows, key=lambda r: _DAY_ORDER.get((r.day_of_week or "").lower(), 7))
    parts = [
        f"{(r.day_of_week or '')[:3]} {_fmt_time(r.start_time)}-{_fmt_time(r.end_time)}"
        for r in ordered
    ]
    return ", ".join(parts)


def _to_card(doctor: Doctor, user: User, availability: list[DoctorAvailability]) -> dict:
    """Shape one doctor into the API's DoctorCard dict."""
    fee = float(doctor.consultation_fee) if doctor.consultation_fee is not None else None
    years = doctor.experience_years or 0
    return {
        "doctorId": doctor.id,
        "name": user.full_name,
        "specialty": doctor.specialty,
        "experience": f"{years} years",
        "consultationFee": fee,
        "hospital": HOSPITAL_NAME,
        "availability": _format_availability(availability),
    }


def get_doctors_by_specialty(
    specialty: str,
    only_available: bool = True,
    preferred_day: str | None = None,
) -> list[dict]:
    """
    Return real doctors for a specialty, newest-experience first, each with
    their real availability window.

    If preferred_day is given (e.g. "Monday"), only doctors with an available
    slot that weekday are returned. Never invents a doctor.
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
        if not rows:
            return []

        # Fetch availability for all matched doctors in one query (no N+1).
        doctor_ids = [doctor.id for doctor, _ in rows]
        av_rows = (
            session.execute(
                select(DoctorAvailability).where(
                    DoctorAvailability.doctor_id.in_(doctor_ids),
                    DoctorAvailability.is_available.is_(True),
                )
            )
            .scalars()
            .all()
        )
        av_by_doctor: dict[int, list[DoctorAvailability]] = {}
        for a in av_rows:
            av_by_doctor.setdefault(a.doctor_id, []).append(a)

        cards: list[dict] = []
        for doctor, user in rows:
            slots = av_by_doctor.get(doctor.id, [])
            if preferred_day:
                slots = [
                    s for s in slots
                    if (s.day_of_week or "").lower() == preferred_day.lower()
                ]
                if not slots:
                    continue  # not bookable that day -> skip
            cards.append(_to_card(doctor, user, slots))
        return cards