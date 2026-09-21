import os
import secrets
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API Config
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "nex-agi/nex-n2.5-mini:free")

# App settings — SECRET_KEY MUST be set in .env for production
_default_secret = os.environ.get("SECRET_KEY", "")
if not _default_secret:
    import warnings
    warnings.warn(
        "SECRET_KEY is not set in .env — using a random ephemeral key. "
        "Sessions will not survive restarts. Set SECRET_KEY in your .env file.",
        RuntimeWarning,
        stacklevel=1,
    )
    _default_secret = secrets.token_hex(32)

SECRET_KEY = _default_secret
MIN_RECORDS = 5
MAX_FILE_SIZE_MB = 5
