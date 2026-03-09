# ============================================================
#  🎬 KinoBot — Dockerfile
#  Render.com → New Background Worker → Docker
# ============================================================

FROM python:3.11-slim

WORKDIR /app

# Kerakli kutubxonalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bot fayllari
COPY . .

# Data papkalarini yaratish
RUN mkdir -p data/users data/movies data/steps data/tizim data/admin

CMD ["python", "bot.py"]
