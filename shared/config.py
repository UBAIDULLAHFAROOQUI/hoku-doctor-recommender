"""
Shared configuration for all Hoku Health Care AI modules.

Reads from a single .env at the hoku-health-ai/ root. Secrets are NEVER
hardcoded — put them in .env (which is gitignored).
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

    # --- Groq (OpenAI-compatible, free tier) ---
    # Groq uses the OpenAI SDK pointed at Groq's servers. Key starts with "gsk_".
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    # --- Database ---
    # For local dev: sqlite:///./hoku_local.db
    # For production: Talha's PostgreSQL URL from hoku-health-backend/.env
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./hoku_local.db",
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