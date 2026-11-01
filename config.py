import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESUMES_DIR = DATA_DIR / "resumes"
COVER_LETTERS_DIR = DATA_DIR / "cover_letters"
MASTER_PROFILE_PATH = DATA_DIR / "master_profile.md"
ENV_PATH = BASE_DIR / ".env"

# Ensure essential directories exist
DATA_DIR.mkdir(exist_ok=True)
RESUMES_DIR.mkdir(exist_ok=True)
COVER_LETTERS_DIR.mkdir(exist_ok=True)

# Default LLM settings (can be overridden by environment or UI requests)
DEFAULT_PROVIDER = os.getenv("RESUME_AI_PROVIDER", "gemini")
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Load existing .env if present
if ENV_PATH.exists():
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

