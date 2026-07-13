"""
Local dev seed — creates the users + doctors tables and inserts sample doctors
so you can test the recommender BEFORE Talha's PostgreSQL is reachable.

Run once:
    python -m doctor_recommender.seed

Uses whatever DATABASE_URL points to in your .env. For local testing set:
    DATABASE_URL=sqlite:///./hoku_local.db

DO NOT run this against Talha's production PostgreSQL — he owns those tables
and seeds them via his own migrations. This is a dev convenience only.
"""

from __future__ import annotations

from doctor_recommender.models import Doctor, User
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


def run() -> None:
    Base.metadata.create_all(engine)  # create tables if they don't exist

    with SessionLocal() as session:
        if session.query(Doctor).count() > 0:
            print("Doctors already seeded — skipping.")
            return

        for full_name, email, specialty, years, qual, fee in SAMPLE:
            user = User(full_name=full_name, email=email, role="doctor")
            session.add(user)
            session.flush()  # assigns user.id
            session.add(
                Doctor(
                    user_id=user.id,
                    specialty=specialty,
                    experience_years=years,
                    qualification=qual,
                    consultation_fee=fee,
                    is_available=True,
                )
            )
        session.commit()
        print(f"Seeded {len(SAMPLE)} doctors across "
              f"{len({s[2] for s in SAMPLE})} specialties.")


if __name__ == "__main__":
    run()
