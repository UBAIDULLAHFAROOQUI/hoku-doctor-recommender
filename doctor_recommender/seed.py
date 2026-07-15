"""
Local dev seed — creates users, doctors, and doctor_availability, and inserts
sample data so you can test the recommender BEFORE Talha's PostgreSQL is ready.

Run once (safe to re-run — it only fills tables that are empty):
    python -m doctor_recommender.seed

Uses whatever DATABASE_URL points to in .env. For local testing:
    DATABASE_URL=sqlite:///./hoku_local.db

DO NOT run against Talha's production PostgreSQL — he owns those tables.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import select

from doctor_recommender.models import Doctor, DoctorAvailability, User
from shared.db import Base, SessionLocal, engine

# (full_name, email, specialty, experience_years, qualification, fee)
SAMPLE = [
    ("Dr. Ali Khan", "ali.khan@hoku.pk", "Cardiologist", 10, "MBBS, FCPS (Cardiology)", 3000),
    ("Dr. Zara Sheikh", "zara.sheikh@hoku.pk", "Cardiologist", 6, "MBBS, MD", 2500),
    ("Dr. Sara Ahmed", "sara.ahmed@hoku.pk", "General Physician", 7, "MBBS", 1500),
    ("Dr. Bilal Iqbal", "bilal.iqbal@hoku.pk", "General Physician", 3, "MBBS", 1000),
    ("Dr. Hina Raza", "hina.raza@hoku.pk", "Dermatologist", 8, "MBBS, Diploma (Dermatology)", 2000),
    ("Dr. Ayesha Noor", "ayesha.noor@hoku.pk", "Gynecologist", 12, "MBBS, FCPS (Gynae)", 3500),
    ("Dr. Usman Tariq", "usman.tariq@hoku.pk", "Dental Specialist", 5, "BDS", 1800),
    ("Dr. Sana Malik", "sana.malik@hoku.pk", "Child Specialist", 9, "MBBS, FCPS (Paeds)", 2200),
]

# email -> list of (day_of_week, start (h, m), end (h, m))
SCHEDULES = {
    "ali.khan@hoku.pk":    [("Monday", (9, 0), (13, 0)), ("Wednesday", (9, 0), (13, 0)), ("Friday", (9, 0), (13, 0))],
    "zara.sheikh@hoku.pk": [("Tuesday", (14, 0), (18, 0)), ("Thursday", (14, 0), (18, 0))],
    "sara.ahmed@hoku.pk":  [("Monday", (10, 0), (18, 0)), ("Tuesday", (10, 0), (18, 0)), ("Wednesday", (10, 0), (18, 0)), ("Thursday", (10, 0), (18, 0)), ("Friday", (10, 0), (18, 0))],
    "bilal.iqbal@hoku.pk": [("Saturday", (9, 0), (14, 0)), ("Sunday", (9, 0), (14, 0))],
    "hina.raza@hoku.pk":   [("Tuesday", (11, 0), (16, 0)), ("Saturday", (11, 0), (16, 0))],
    "ayesha.noor@hoku.pk": [("Monday", (9, 0), (12, 0)), ("Wednesday", (9, 0), (12, 0))],
    "usman.tariq@hoku.pk": [("Monday", (9, 0), (17, 0)), ("Thursday", (9, 0), (17, 0))],
    "sana.malik@hoku.pk":  [("Monday", (9, 0), (13, 0)), ("Tuesday", (9, 0), (13, 0)), ("Wednesday", (9, 0), (13, 0)), ("Thursday", (9, 0), (13, 0)), ("Friday", (9, 0), (13, 0))],
}


def run() -> None:
    Base.metadata.create_all(engine)  # creates any missing tables

    with SessionLocal() as session:
        # --- doctors + users ---
        if session.query(Doctor).count() == 0:
            for full_name, email, specialty, years, qual, fee in SAMPLE:
                user = User(full_name=full_name, email=email, role="doctor")
                session.add(user)
                session.flush()  # assigns user.id
                session.add(Doctor(
                    user_id=user.id, specialty=specialty, experience_years=years,
                    qualification=qual, consultation_fee=fee, is_available=True,
                ))
            session.commit()
            print(f"Seeded {len(SAMPLE)} doctors.")
        else:
            print("Doctors already seeded — skipping.")

        # --- availability (added even if doctors already existed) ---
        if session.query(DoctorAvailability).count() == 0:
            # map email -> doctor.id
            email_to_doctor = {
                user.email: doctor.id
                for doctor, user in session.execute(
                    select(Doctor, User).join(User, Doctor.user_id == User.id)
                ).all()
            }
            count = 0
            for email, slots in SCHEDULES.items():
                doctor_id = email_to_doctor.get(email)
                if not doctor_id:
                    continue
                for day, (sh, sm), (eh, em) in slots:
                    session.add(DoctorAvailability(
                        doctor_id=doctor_id, day_of_week=day,
                        start_time=dt.time(sh, sm), end_time=dt.time(eh, em),
                        is_available=True,
                    ))
                    count += 1
            session.commit()
            print(f"Seeded {count} availability slots.")
        else:
            print("Availability already seeded — skipping.")


if __name__ == "__main__":
    run()