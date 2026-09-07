import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "starter-datasets"
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_STORAGE_DIR = BASE_DIR / "data_store"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATA_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

# Default LLM provider if keys are available: 'gemini', 'openai', or 'local'
DEFAULT_PROVIDER = "gemini" if GEMINI_API_KEY else ("openai" if OPENAI_API_KEY else "local")
