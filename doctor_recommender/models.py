"""
ORM models the recommender READS.  (Ubaid Ullah Farooqui)

These mirror the `users` and `doctors` tables from the brief's schema (§5.1).
In production these tables are OWNED and migrated by Talha's backend (Alembic);
this module only reads them. Only the columns the recommender needs are mapped —
that is enough to SELECT even when the real table has extra columns.

The seed.py script uses these same models to create + populate a local DB for
testing before Talha's PostgreSQL is reachable.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String, Text, Time
from sqlalchemy.orm import relationship

from shared.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), default="patient")  # patient / doctor / admin


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    specialty = Column(String(255), nullable=False)
    experience_years = Column(Integer)
    qualification = Column(String(255))
    consultation_fee = Column(Numeric(10, 2))
    is_available = Column(Boolean, default=True)

    # Lets us reach the doctor's name via doctors.user.full_name
    user = relationship("User")


class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"

    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    day_of_week = Column(String(20))  # Monday, Tuesday, ...
    start_time = Column(Time)
    end_time = Column(Time)
    is_available = Column(Boolean, default=True)


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)