"""
⚙️ KinoBot — Sozlamalar
.env yoki environment variables orqali o'qiladi
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash (agar mavjud bo'lsa)
load_dotenv(Path(__file__).parent / ".env")

# ──────────────────────────────────────────────────────────────
#  🔑  ASOSIY ENV VARIABLES
#  Render/VPS da: Environment Variables bo'limiga qo'shing
#  Lokal da: .env faylini to'ldiring
# ──────────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
OWNER_ID:  int = int(os.getenv("OWNER_ID", "0"))

# ──────────────────────────────────────────────────────────────
#  📁  PAPKALAR
# ──────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "data"

USERS_DIR  = DATA_DIR / "users"
MOVIES_DIR = DATA_DIR / "movies"
STEP_DIR   = DATA_DIR / "steps"
TIZIM_DIR  = DATA_DIR / "tizim"
ADMIN_DIR  = DATA_DIR / "admin"
