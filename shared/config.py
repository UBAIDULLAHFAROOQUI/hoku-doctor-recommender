"""
Shared configuration for all Hoku Health Care AI modules.

Reads from a single .env at the hoku-health-ai/ root so the chatbot,
symptom checker, doctor recommender and sentiment modules all point at
the SAME PostgreSQL that Talha's backend uses. Do not hardcode secrets.
"""

import os
from functools import lru_cache

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional; env vars can also come from the shell / Render.
    pass


class Settings:
    """Central settings object. Import `settings` from this module."""

    # --- OpenAI (used from Day 3 onward, declared now so config is stable) ---
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # --- Database (used from Day 2 onward) ---
    # MUST match the DATABASE_URL in Talha's hoku-health-backend/.env,
    # otherwise recommender queries hit a different `doctors` table than prod.
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/hoku_health",
    )

    # --- Service behaviour ---
    # NFR-02: AI responses must return in under 4 seconds.
    AI_TIMEOUT_SECONDS: float = float(os.getenv("AI_TIMEOUT_SECONDS", "4"))

    # Mandatory disclaimer appended to every AI health response (brief §10.1).
    MEDICAL_DISCLAIMER: str = "Please consult a doctor for proper diagnosis."


@lru_cache
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()
