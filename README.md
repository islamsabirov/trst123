# 🎬 KinoBot — Python Telegram Bot

Har tomonlama ishlaydigan kino bot. Render.com, VPS, yoki lokal kompyuterda ishlaydi.

---

## 📁 Fayl tuzilmasi

```
KinoBot/
├── bot.py            ← Asosiy fayl (ishga tushirish)
├── config.py         ← Sozlamalar (env vars)
├── database.py       ← Ma'lumotlar bazasi (fayl asosida)
├── handlers.py       ← Barcha bot handlerlari
├── helpers.py        ← Yordamchi funksiyalar
├── keyboards.py      ← Barcha tugmalar
├── requirements.txt  ← Python kutubxonalar
├── Dockerfile        ← Docker (Render uchun)
├── .env.example      ← Namuna sozlamalar
└── data/             ← Ma'lumotlar (avtomatik yaratiladi)
    ├── users/
    ├── movies/
    ├── steps/
    └── tizim/
```

---

## 🚀 Ishga tushirish

### 1️⃣ Lokal (kompyuterda)

```bash
# 1. Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 2. .env fayl yaratish
cp .env.example .env
# .env ni oching va to'ldiring:
# BOT_TOKEN=sizning_token
# OWNER_ID=sizning_id

# 3. Botni ishga tushirish
python bot.py
```

### 2️⃣ Render.com da

1. GitHub ga yuklang:
```bash
git init && git add . && git commit -m "KinoBot"
git remote add origin https://github.com/SIZNING/repo.git
git push -u origin main
```

2. Render.com → **New** → **Background Worker**
3. GitHub repo ni ulang
4. **Environment**: Docker
5. **Environment Variables** ga qo'shing:
   ```
   BOT_TOKEN = sizning_bot_tokeni
   OWNER_ID  = sizning_telegram_id
   ```
6. **Deploy** bosing ✅

### 3️⃣ VPS (Ubuntu/Debian)

```bash
# Python o'rnatish
sudo apt update && sudo apt install python3 python3-pip -y

# Fayllarni yuklash
git clone https://github.com/SIZNING/kinobot.git
cd kinobot
pip3 install -r requirements.txt

# .env yaratish
cp .env.example .env
nano .env  # Token va ID ni kiriting

# Fon rejimida ishga tushirish
nohup python3 bot.py > bot.log 2>&1 &

# Yoki systemd service sifatida
sudo nano /etc/systemd/system/kinobot.service
```

**systemd service fayli:**
```ini
[Unit]
Description=KinoBot Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/kinobot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable kinobot
sudo systemctl start kinobot
sudo systemctl status kinobot
```

---

## ⚙️ Bot sozlamalari

### Birinchi marta ishga tushirgandan keyin:

1. Botga `/start` yuboring
2. **📥 Kino Yuklash** → Rasm + Video yuklang
3. **📢 Kanallar** → Majburiy obuna kanalini qo'shing
4. **📢 Kanallar** → Kino kanalini ulan

### Kino yuklash tartibi:
1. **📥 Kino Yuklash** ni bosing
2. Rasm yuboring (poster)
3. Video + caption (kino nomi) yuboring
4. Tayyor! Bot kanalga post qiladi va kod beradi

---

## 🔑 Muhim ma'lumotlar

- **BOT_TOKEN** — @BotFather dan oling
- **OWNER_ID** — @userinfobot botga `/start` yuboring
- Ma'lumotlar `data/` papkasida saqlanadi
- Webhook shart emas — Polling rejimida ishlaydi

---

## 📱 Funksiyalar

| Funksiya | Tavsif |
|---------|--------|
| 🎬 Kino yuborish | Kod bo'yicha video yuborish |
| 📥 Kino yuklash | Rasm + Video + Caption |
| 📢 Majburiy obuna | Kanal obunasini tekshirish |
| ✉️ Xabarnoma | Barcha userlarga yoki bitta usерга |
| 📊 Statistika | Kunlik, oylik, kinolar |
| 🤖 Bot on/off | Botni yoqish/o'chirish |
| 👥 Adminlar | Admin qo'shish/o'chirish |
| 🗂 Kino ro'yxati | Barcha kinolar va statistika |
