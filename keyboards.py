"""
⌨️ KinoBot — Klaviaturalar
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from database import db


# ── REPLY KLAVIATURALAR ────────────────────────────────────────

def kb_main() -> ReplyKeyboardMarkup:
    """Oddiy foydalanuvchi — asosiy"""
    return ReplyKeyboardMarkup(
        [[" 🎬 Kino qidirish", "📋 Yordam"]],
        resize_keyboard=True,
    )


def kb_admin_panel() -> ReplyKeyboardMarkup:
    """Admin panel"""
    return ReplyKeyboardMarkup(
        [
            ["📥 Kino Yuklash",  "🗂 Kino Ro'yxati"],
            ["📢 Kanallar",      "✉️ Xabarnoma"],
            ["📊 Statistika",    "🤖 Bot Holati"],
            ["👥 Adminlar",      "👑 VIP Boshqaruv"],
            ["◀️ Orqaga"],
        ],
        resize_keyboard=True,
    )


def kb_back() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["◀️ Orqaga"]], resize_keyboard=True)


# ── INLINE KLAVIATURALAR ───────────────────────────────────────

def ikb_main_user(movie_channel: str = "", bot_username: str = "") -> InlineKeyboardMarkup:
    buttons = []
    if movie_channel:
        ch = movie_channel.lstrip("@")
        buttons.append([InlineKeyboardButton("🎬 Kino Kanali", url=f"https://t.me/{ch}")])
    buttons.append([InlineKeyboardButton("📋 Yordam", callback_data="help")])
    return InlineKeyboardMarkup(buttons)


def ikb_subscription(channels: list, bot_username: str = "") -> InlineKeyboardMarkup:
    buttons = []
    for ch in channels:
        if ch.startswith("@"):
            url  = f"https://t.me/{ch.lstrip('@')}"
            text = f"📢 I remember"
        else:
            url  = ch
            text = "🔒 I remember"
        buttons.append([InlineKeyboardButton(text, url=url)])
    buttons.append([InlineKeyboardButton("✅ Obuna bo'ldim", callback_data="check_sub")])
    return InlineKeyboardMarkup(buttons)


def ikb_movie(code: int, bot_username: str, movie_channel: str = "") -> InlineKeyboardMarkup:
    buttons = []
    if movie_channel:
        ch = movie_channel.lstrip("@")
        buttons.append([InlineKeyboardButton("🔎 Kino Kanali", url=f"https://t.me/{ch}")])
    share_url = f"https://t.me/{bot_username}?start={code}"
    buttons.append([InlineKeyboardButton("📤 Ulashish", url=f"https://t.me/share/url?url={share_url}")])
    return InlineKeyboardMarkup(buttons)


def ikb_admin_home() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖥️ Admin Panel", callback_data="admin_panel")],
    ])


def ikb_vip_menu() -> InlineKeyboardMarkup:
    """VIP boshqaruv menyusi"""
    vip_enabled = db.get_vip_status()
    status_btn = InlineKeyboardButton("❌ VIP O'chirish", callback_data="toggle_vip") if vip_enabled \
                else InlineKeyboardButton("✅ VIP Yoqish", callback_data="toggle_vip")
    
    return InlineKeyboardMarkup([
        [status_btn],
        [InlineKeyboardButton("👑 VIP Ro'yxat", callback_data="list_vip")],
        [InlineKeyboardButton("➕ VIP Qo'shish", callback_data="add_vip"),
         InlineKeyboardButton("🗑 VIP O'chirish", callback_data="del_vip")],
        [InlineKeyboardButton("◀️ Orqaga", callback_data="admin_panel")],
    ])


def ikb_channels_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Majburiy Obuna", callback_data="sub_channels")],
        [InlineKeyboardButton("🎬 Kino Kanali",    callback_data="movie_channel")],
        [InlineKeyboardButton("◀️ Orqaga",          callback_data="admin_panel")],
    ])


def ikb_sub_channels_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Qo'shish",  callback_data="add_sub_ch"),
         InlineKeyboardButton("🗑 O'chirish", callback_data="del_sub_ch")],
        [InlineKeyboardButton("📋 Ro'yxat",   callback_data="list_sub_ch")],
        [InlineKeyboardButton("◀️ Orqaga",    callback_data="channels_menu")],
    ])


def ikb_movie_channel_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 O'zgartirish", callback_data="set_movie_ch")],
        [InlineKeyboardButton("◀️ Orqaga",       callback_data="channels_menu")],
    ])


def ikb_broadcast_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📨 Hammaga Xabar",   callback_data="broadcast_all")],
        [InlineKeyboardButton("👤 Userga Xabar",    callback_data="broadcast_user")],
        [InlineKeyboardButton("◀️ Orqaga",           callback_data="admin_panel")],
    ])


def ikb_stats_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Kunlik",  callback_data="stat_daily"),
         InlineKeyboardButton("📆 Oylik",   callback_data="stat_monthly")],
        [InlineKeyboardButton("🎬 Kinolar", callback_data="stat_movies")],
        [InlineKeyboardButton("◀️ Orqaga",  callback_data="admin_panel")],
    ])


def ikb_bot_status(is_active: bool) -> InlineKeyboardMarkup:
    if is_active:
        btn = InlineKeyboardButton("❌ O'chirish", callback_data="toggle_bot")
    else:
        btn = InlineKeyboardButton("✅ Yoqish", callback_data="toggle_bot")
    return InlineKeyboardMarkup([
        [btn],
        [InlineKeyboardButton("◀️ Orqaga", callback_data="admin_panel")],
    ])


def ikb_admins_menu(is_owner: bool = False) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton("📋 Ro'yxat", callback_data="list_admins")]]
    if is_owner:
        buttons.append([
            InlineKeyboardButton("➕ Qo'shish",  callback_data="add_admin"),
            InlineKeyboardButton("🗑 O'chirish", callback_data="del_admin"),
        ])
    buttons.append([InlineKeyboardButton("◀️ Orqaga", callback_data="admin_panel")])
    return InlineKeyboardMarkup(buttons)


def ikb_movie_confirm(code: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_movie_{code}"),
         InlineKeyboardButton("❌ Bekor",      callback_data="cancel_movie")],
    ])


def ikb_movie_list_item(code: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🗑 #{code} ni o'chirish", callback_data=f"del_movie_{code}")],
        [InlineKeyboardButton("◀️ Orqaga", callback_data="admin_panel")],
    ])


def ikb_back_to_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Orqaga", callback_data="admin_panel")],
    ])


def ikb_cancel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_step")],
    ])
