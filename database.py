"""
🗄️ KinoBot — Ma'lumotlar bazasi (fayl asosida)
JSON + text fayllar — hamma serverda ishlaydi
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from config import (
    BASE_DIR, DATA_DIR, USERS_DIR, MOVIES_DIR,
    STEP_DIR, TIZIM_DIR, ADMIN_DIR, OWNER_ID
)

logger = logging.getLogger(__name__)


class Database:
    """Fayl asosidagi ma'lumotlar bazasi"""

    def init_dirs(self):
        """Kerakli papkalarni yaratish"""
        for d in [DATA_DIR, USERS_DIR, MOVIES_DIR, STEP_DIR, TIZIM_DIR, ADMIN_DIR]:
            d.mkdir(parents=True, exist_ok=True)
        logger.info("📁 Barcha papkalar tayyor")

    # ──────────────────────────────────────────────────
    #  👤 FOYDALANUVCHILAR
    # ──────────────────────────────────────────────────
    def user_exists(self, user_id: int) -> bool:
        return (USERS_DIR / f"{user_id}.json").exists()

    def save_user(self, user_id: int, first_name: str, username: str) -> bool:
        """Yangi foydalanuvchi saqlash. True = yangi, False = mavjud"""
        path = USERS_DIR / f"{user_id}.json"
        if path.exists():
            return False
        data = {
            "id":         user_id,
            "name":       first_name,
            "username":   username or "",
            "joined":     datetime.now().strftime("%d.%m.%Y"),
            "joined_dt":  datetime.now().isoformat(),
        }
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return True

    def get_all_users(self) -> list[int]:
        return [int(f.stem) for f in USERS_DIR.glob("*.json")]

    def get_user_count(self) -> int:
        return len(list(USERS_DIR.glob("*.json")))

    def get_users_by_date(self, date_str: str) -> int:
        """Berilgan sana (dd.mm.YYYY) ga qo'shilgan userlar soni"""
        count = 0
        for f in USERS_DIR.glob("*.json"):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                if d.get("joined") == date_str:
                    count += 1
            except Exception:
                pass
        return count

    def get_users_by_month(self, month_str: str) -> int:
        """Berilgan oy (mm.YYYY) ga qo'shilgan userlar soni"""
        count = 0
        for f in USERS_DIR.glob("*.json"):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                if d.get("joined", "")[-7:] == month_str:
                    count += 1
            except Exception:
                pass
        return count

    def is_blocked(self, user_id: int) -> bool:
        f = TIZIM_DIR / "blocked.txt"
        if not f.exists():
            return False
        return str(user_id) in f.read_text().split()

    def block_user(self, user_id: int):
        f = TIZIM_DIR / "blocked.txt"
        ids = set(f.read_text().split()) if f.exists() else set()
        ids.add(str(user_id))
        f.write_text("\n".join(ids))

    # ──────────────────────────────────────────────────
    #  🎬 KINOLAR
    # ──────────────────────────────────────────────────
    def get_next_movie_code(self) -> int:
        f = DATA_DIR / "movie_counter.txt"
        n = int(f.read_text()) + 1 if f.exists() else 1
        f.write_text(str(n))
        return n

    def save_movie(self, code: int, title: str, file_id: str, photo_id: str) -> None:
        path = MOVIES_DIR / f"{code}.json"
        data = {
            "code":      code,
            "title":     title,
            "file_id":   file_id,
            "photo_id":  photo_id,
            "downloads": 0,
            "added":     datetime.now().strftime("%d.%m.%Y %H:%M"),
        }
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def get_movie(self, code: int) -> Optional[dict]:
        path = MOVIES_DIR / f"{code}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def movie_downloaded(self, code: int) -> None:
        path = MOVIES_DIR / f"{code}.json"
        if path.exists():
            d = json.loads(path.read_text(encoding="utf-8"))
            d["downloads"] = d.get("downloads", 0) + 1
            path.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

    def get_movie_count(self) -> int:
        return len(list(MOVIES_DIR.glob("*.json")))

    def delete_movie(self, code: int) -> bool:
        path = MOVIES_DIR / f"{code}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def get_all_movies(self) -> list[dict]:
        movies = []
        for f in sorted(MOVIES_DIR.glob("*.json")):
            try:
                movies.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                pass
        return movies

    def search_movies(self, query: str) -> list[dict]:
        """Kinolarni nomi bo'yicha qidirish"""
        movies = []
        query = query.lower().strip()
        for f in MOVIES_DIR.glob("*.json"):
            try:
                movie = json.loads(f.read_text(encoding="utf-8"))
                if query in movie.get("title", "").lower():
                    movies.append(movie)
            except Exception:
                pass
        return movies

    def get_top_movies(self, limit: int = 10) -> list[dict]:
        """Eng ko'p yuklangan kinolar"""
        movies = []
        for f in MOVIES_DIR.glob("*.json"):
            try:
                movie = json.loads(f.read_text(encoding="utf-8"))
                movies.append(movie)
            except Exception:
                pass
        
        movies.sort(key=lambda x: x.get("downloads", 0), reverse=True)
        return movies[:limit]

    # ──────────────────────────────────────────────────
    #  🪜 STEPLAR (holat saqlash)
    # ──────────────────────────────────────────────────
    def set_step(self, user_id: int, step: str = "", data: dict = None) -> None:
        f = STEP_DIR / f"{user_id}.json"
        if step == "":
            f.unlink(missing_ok=True)
        else:
            payload = {"step": step, "data": data or {}}
            f.write_text(json.dumps(payload), encoding="utf-8")

    def get_step(self, user_id: int) -> tuple[str, dict]:
        f = STEP_DIR / f"{user_id}.json"
        if not f.exists():
            return "", {}
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            return d.get("step", ""), d.get("data", {})
        except Exception:
            return "", {}

    # ──────────────────────────────────────────────────
    #  🔧 TIZIM SOZLAMALARI
    # ──────────────────────────────────────────────────
    def _tizim(self, key: str, default="") -> str:
        f = TIZIM_DIR / f"{key}.txt"
        return f.read_text(encoding="utf-8").strip() if f.exists() else default

    def _tizim_set(self, key: str, value: str) -> None:
        (TIZIM_DIR / f"{key}.txt").write_text(value, encoding="utf-8")

    # Bot holati
    def is_bot_active(self) -> bool:
        return self._tizim("bot_active", "1") == "1"

    def toggle_bot(self) -> bool:
        """Botni yoqish/o'chirish. Yangi holatni qaytaradi"""
        new = not self.is_bot_active()
        self._tizim_set("bot_active", "1" if new else "0")
        return new

    # Kino kanali
    def get_movie_channel(self) -> str:
        return self._tizim("movie_channel", "")

    def set_movie_channel(self, channel: str) -> None:
        self._tizim_set("movie_channel", channel.strip())

    # Majburiy obuna kanallar
    def get_sub_channels(self) -> list[str]:
        raw = self._tizim("sub_channels", "")
        return [c.strip() for c in raw.split("\n") if c.strip()]

    def add_sub_channel(self, channel: str) -> bool:
        channels = self.get_sub_channels()
        if channel not in channels:
            channels.append(channel)
            self._tizim_set("sub_channels", "\n".join(channels))
            return True
        return False

    def remove_sub_channel(self, channel: str) -> bool:
        channels = self.get_sub_channels()
        if channel in channels:
            channels.remove(channel)
            self._tizim_set("sub_channels", "\n".join(channels))
            return True
        return False

    # Adminlar
    def get_admins(self) -> list[int]:
        raw = self._tizim("admins", "")
        ids = [int(x) for x in raw.split() if x.strip().isdigit()]
        if OWNER_ID not in ids:
            ids.insert(0, OWNER_ID)
        return ids

    def add_admin(self, user_id: int) -> bool:
        admins = self.get_admins()
        if user_id not in admins:
            admins.append(user_id)
            self._tizim_set("admins", "\n".join(str(a) for a in admins if a != OWNER_ID))
            return True
        return False

    def remove_admin(self, user_id: int) -> bool:
        admins = [a for a in self.get_admins() if a != OWNER_ID]
        if user_id in admins:
            admins.remove(user_id)
            self._tizim_set("admins", "\n".join(str(a) for a in admins))
            return True
        return False

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.get_admins()

    # Xabarnoma target
    def set_broadcast_target(self, user_id: int, target_uid: int) -> None:
        self.set_step(user_id, "send_to_user", {"target": target_uid})

    # VIP tizimi
    def get_vip_users(self) -> list[int]:
        """VIP foydalanuvchilar ro'yxati"""
        raw = self._tizim("vip_users", "")
        return [int(x) for x in raw.split() if x.strip().isdigit()]

    def add_vip_user(self, user_id: int) -> bool:
        """VIP foydalanuvchi qo'shish"""
        vip_users = self.get_vip_users()
        if user_id not in vip_users:
            vip_users.append(user_id)
            self._tizim_set("vip_users", " ".join(str(uid) for uid in vip_users))
            return True
        return False

    def remove_vip_user(self, user_id: int) -> bool:
        """VIP foydalanuvchini olib tashlash"""
        vip_users = self.get_vip_users()
        if user_id in vip_users:
            vip_users.remove(user_id)
            self._tizim_set("vip_users", " ".join(str(uid) for uid in vip_users))
            return True
        return False

    def is_vip_user(self, user_id: int) -> bool:
        """Foydalanuvchi VIPmi tekshirish"""
        return user_id in self.get_vip_users()

    def get_vip_status(self) -> bool:
        """VIP tizimi yoqilgan/o'chirilgan"""
        return self._tizim("vip_enabled", "0") == "1"

    def set_vip_status(self, enabled: bool) -> None:
        """VIP tizimini yoqish/o'chirish"""
        self._tizim_set("vip_enabled", "1" if enabled else "0")


db = Database()
