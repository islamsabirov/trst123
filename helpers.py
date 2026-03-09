"""
🔧 KinoBot — Yordamchi funksiyalar
"""

import asyncio
import logging
from telegram import Bot, Update
from telegram.error import TelegramError

from database import db
from keyboards import ikb_subscription

logger = logging.getLogger(__name__)


async def check_subscription(bot: Bot, user_id: int, check_only: bool = False) -> bool:
    """
    Foydalanuvchining majburiy kanallarga obunasini tekshirish.
    True = obuna bor, False = obuna yo'q
    """
    # VIP tizimi yoqilgan bo'lsa va foydalanuvchi VIP bo'lmasa
    if db.get_vip_status() and not db.is_vip_user(user_id):
        if not check_only:
            await bot.send_message(
                chat_id=user_id,
                text="🔒 <b>Bu funksiya faqat VIP obunachilar uchun!</b>\n\n"
                     "💎 Botdan to'liq foydalanish uchun VIP obuna bo'ling.",
                parse_mode="HTML",
            )
        return False
    
    channels = db.get_sub_channels()
    if not channels:
        return True

    not_subscribed = []
    for ch in channels:
        try:
            if ch.startswith("@"):
                member = await bot.get_chat_member(chat_id=ch, user_id=user_id)
                if member.status not in ("creator", "administrator", "member"):
                    not_subscribed.append(ch)
            # Maxfiy kanallar uchun: faqat invite link bor
            # Ularni avtomatik tekshirib bo'lmaydi, shuning uchun skip
        except TelegramError as e:
            logger.warning(f"Sub tekshiruv xato ({ch}): {e}")

    if not_subscribed and not check_only:
        kb = ikb_subscription(not_subscribed)
        await bot.send_message(
            chat_id=user_id,
            text=(
                "⚠️ <b>Botdan foydalanish uchun quyidagi kanalga obuna bo'ling:</b>\n\n"
                "- Kanal tugmasi nomi: \"I remember\"\n"
                "- Tugma kanal ssilkasiga olib boradi"
            ),
            parse_mode="HTML",
            reply_markup=kb,
        )
        return False
    return len(not_subscribed) == 0


async def register_user(bot: Bot, user_id: int, first_name: str, username: str, owner_id: int) -> None:
    """Yangi foydalanuvchini ro'yxatga olish va ownerga xabar berish"""
    is_new = db.save_user(user_id, first_name, username or "")
    if is_new:
        uname_str = f"@{username}" if username else "yo'q"
        try:
            await bot.send_message(
                chat_id=owner_id,
                text=(
                    f"👤 <b>Yangi foydalanuvchi!</b>\n\n"
                    f"👤 Ism: {first_name}\n"
                    f"🆔 ID: <code>{user_id}</code>\n"
                    f"🔗 Username: {uname_str}"
                ),
                parse_mode="HTML",
            )
        except TelegramError:
            pass


async def broadcast_message(bot: Bot, user_ids: list[int], from_chat_id: int, message_id: int) -> tuple[int, int]:
    """Barcha userlarga xabar yuborish. (ok, err) qaytaradi"""
    ok = err = 0
    for uid in user_ids:
        try:
            await bot.copy_message(
                chat_id=uid,
                from_chat_id=from_chat_id,
                message_id=message_id,
            )
            ok += 1
        except TelegramError:
            err += 1
        await asyncio.sleep(0.05)  # Flood limiti uchun
    return ok, err


def user_mention(user_id: int, name: str) -> str:
    return f"<a href='tg://user?id={user_id}'>{name}</a>"
