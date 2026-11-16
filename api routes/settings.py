import os
from pathlib import Path
from dotenv import load_dotenv

# Neon CLI writes its service credentials in the project root.
# Existing process variables (e.g. Render secrets) always take precedence.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env.local")
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(Path(__file__).resolve().parent / ".env")
PRODUCTION = os.getenv("APP_ENV", "development") == "production"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true" if PRODUCTION else "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax").lower()
CORS_ORIGINS = [value.strip().rstrip("/") for value in os.getenv("CORS_ORIGINS", "" if PRODUCTION else "http://localhost:5173").split(",") if value.strip()]
if COOKIE_SAMESITE not in {"lax", "strict", "none"}:
    raise RuntimeError("COOKIE_SAMESITE must be lax, strict or none")
if (PRODUCTION or COOKIE_SAMESITE == "none") and not COOKIE_SECURE:
    raise RuntimeError("HTTPS cookies are required for production and SameSite=None")
if PRODUCTION and (len(os.getenv("SECRET_KEY", "")) < 32 or os.getenv("SECRET_KEY", "").startswith("replace-")):
    raise RuntimeError("Configure a strong SECRET_KEY for production")
if "*" in CORS_ORIGINS:
    raise RuntimeError("Use explicit origins with cookie authentication")
