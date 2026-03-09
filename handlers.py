"""
🎮 KinoBot — Barcha handlerlar
"""

import logging
from datetime import datetime, timedelta

from telegram import Update, Message, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from config import OWNER_ID
from database import db
from keyboards import (
    kb_main, kb_admin_panel, kb_back, ikb_back_to_panel,
    ikb_cancel, ikb_channels_menu, ikb_sub_channels_menu,
    ikb_movie_channel_menu, ikb_broadcast_menu, ikb_stats_menu,
    ikb_bot_status, ikb_admins_menu, ikb_movie, ikb_subscription,
    ikb_movie_confirm, ikb_movie_list_item, ikb_main_user,
)
from helpers import check_subscription, register_user, broadcast_message, user_mention

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
#  🔵 /start
# ═══════════════════════════════════════════════════════════════
async def start_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user    = update.effective_user
    chat_id = update.effective_chat.id
    text    = update.message.text if update.message else "/start"
    bot     = ctx.bot

    await register_user(bot, user.id, user.first_name, user.username, OWNER_ID)
    db.set_step(user.id)  # Stepni tozalash

    # 👑 Ega uchun alohida javob
    if user.id == OWNER_ID:
        me = await bot.get_me()
        await update.message.reply_text(
            f"👑 <b>Xush kelibsiz, bot egasi!</b>\n\n"
            f"🤖 Bot: @{me.username}\n"
            f"👥 Foydalanuvchilar: {db.get_user_count()} ta\n"
            f"🎬 Kinolar: {db.get_movie_count()} ta\n"
            f"🟢 Holat: {'Yoqilgan' if db.is_bot_active() else 'O`chirilgan'}\n\n"
            f"🎛 Admin paneldan foydalaning:",
            parse_mode="HTML",
            reply_markup=kb_admin_panel(),
        )
        return

    # Admin uchun
    if db.is_admin(user.id):
        await update.message.reply_text(
            f"🖥 <b>Admin paneliga xush kelibsiz, {user.first_name}!</b>",
            parse_mode="HTML",
            reply_markup=kb_admin_panel(),
        )
        return

    # Bot o'chirilgan
    if not db.is_bot_active():
        await update.message.reply_text(
            "⛔️ <b>Bot vaqtinchalik o'chirilgan.</b>",
            parse_mode="HTML",
        )
        return

    # Kino kodi bilan keldi?  /start 42
    parts = text.split()
    code  = parts[1] if len(parts) > 1 else ""

    if code.isdigit():
        if not await check_subscription(bot, user.id):
            return
        await send_movie(update, ctx, int(code))
        return

    # Obuna tekshirish
    if not await check_subscription(bot, user.id):
        return

    me          = await bot.get_me()
    movie_ch    = db.get_movie_channel()
    nlink       = user_mention(user.id, user.first_name)

    await update.message.reply_text(
        f"🖐 <b>Assalomu alaykum, {nlink}!</b>\n\n"
        f"🎬 Kino kodini yuboring yoki kaналдан kodini toping.",
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=ikb_main_user(movie_ch, me.username),
    )


# ═══════════════════════════════════════════════════════════════
#  🔵 /help
# ═══════════════════════════════════════════════════════════════
async def help_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "ℹ️ <b>Yordam</b>\n\n"
        "🔢 Kino kodini yuboring → kino olasiz\n"
        "/start — Botni qayta ishga tushirish\n\n"
        "❓ Savol uchun admin bilan bog'laning.",
        parse_mode="HTML",
    )


# ═══════════════════════════════════════════════════════════════
#  🔵 MESSAGE HANDLER
# ═══════════════════════════════════════════════════════════════
async def message_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    user    = update.effective_user
    msg     = update.message
    text    = msg.text or msg.caption or ""
    is_adm  = db.is_admin(user.id)
    step, step_data = db.get_step(user.id)

    # ── Orqaga ───────────────────────────────────────────────
    if text == "◀️ Orqaga":
        db.set_step(user.id)
        if is_adm:
            await msg.reply_text("🏠 Bosh menyu:", reply_markup=kb_admin_panel())
        else:
            await msg.reply_text("🏠 Bosh menyu:", reply_markup=kb_main())
        return

    # ── Admin tugmalari ──────────────────────────────────────
    if text == "📥 Kino Yuklash" and is_adm:
        await start_movie_upload(update, ctx)
        return

    if text == "🗂 Kino Ro'yxati" and is_adm:
        await show_movie_list(update, ctx)
        return

    if text == "📢 Kanallar" and is_adm:
        await msg.reply_text(
            "📢 <b>Kanallar sozlamalari:</b>",
            parse_mode="HTML",
            reply_markup=ikb_channels_menu(),
        )
        return

    if text == "✉️ Xabarnoma" and is_adm:
        await msg.reply_text(
            "✉️ <b>Xabarnoma turini tanlang:</b>",
            parse_mode="HTML",
            reply_markup=ikb_broadcast_menu(),
        )
        return

    if text == "📊 Statistika" and is_adm:
        await show_stats(update, ctx)
        return

    if text == "🤖 Bot Holati" and is_adm:
        active = db.is_bot_active()
        status = "✅ Yoqilgan" if active else "❌ O'chirilgan"
        await msg.reply_text(
            f"🤖 <b>Bot holati:</b> {status}",
            parse_mode="HTML",
            reply_markup=ikb_bot_status(active),
        )
        return

    if text == "👥 Adminlar" and is_adm:
        await msg.reply_text(
            "👮 <b>Adminlar boshqaruvi:</b>",
            parse_mode="HTML",
            reply_markup=ikb_admins_menu(user.id == OWNER_ID),
        )
        return

    if text == "👑 VIP Boshqaruv" and is_adm:
        vip_status = "✅ Yoqilgan" if db.get_vip_status() else "❌ O'chirilgan"
        vip_count = len(db.get_vip_users())
        await msg.reply_text(
            f"👑 <b>VIP Boshqaruv</b>\n\n"
            f"🔧 Holat: {vip_status}\n"
            f"👥 VIPlar: {vip_count} ta",
            parse_mode="HTML",
            reply_markup=ikb_vip_menu(),
        )
        return

    # ── STEP: Kino yuklash — rasm ────────────────────────────
    if step == "upload_photo" and is_adm:
        if msg.photo:
            photo_id = msg.photo[-1].file_id
            db.set_step(user.id, "upload_video", {"photo_id": photo_id})
            await msg.reply_text(
                "✅ Rasm saqlandi!\n\n🎬 Endi <b>video</b> + <b>caption</b> (kino nomi) yuboring:",
                parse_mode="HTML",
                reply_markup=ikb_cancel(),
            )
        else:
            await msg.reply_text("📸 Iltimos, <b>rasm</b> yuboring!", parse_mode="HTML")
        return

    # ── STEP: Kino yuklash — video ───────────────────────────
    if step == "upload_video" and is_adm:
        if msg.video or msg.document:
            file_id = (msg.video or msg.document).file_id
            title   = msg.caption or "Nomsiz kino"
            photo_id = step_data.get("photo_id", "")

            code = db.get_next_movie_code()
            db.save_movie(code, title, file_id, photo_id)
            db.set_step(user.id)

            movie_ch = db.get_movie_channel()
            me = await ctx.bot.get_me()

            # Kaналга post
            if movie_ch:
                try:
                    sent = await ctx.bot.send_photo(
                        chat_id=movie_ch,
                        photo=photo_id,
                        caption=(
                            f"🍿 <b>{title}</b>\n\n"
                            f"🔢 Kod: <code>{code}</code>\n"
                            f"🤖 Bot: @{me.username}"
                        ),
                        parse_mode="HTML",
                        reply_markup=ikb_movie(code, me.username, movie_ch),
                    )
                    ch_clean = movie_ch.lstrip("@")
                    ch_link = f"https://t.me/{ch_clean}/{sent.message_id}"
                    await msg.reply_text(
                        f"✅ <b>Kino joylandi!</b>\n\n"
                        f"🔢 Kod: <code>{code}</code>\n"
                        f"🎬 Nomi: {title}\n\n"
                        f"<a href='{ch_link}'>📢 Kanalda ko'rish</a>",
                        parse_mode="HTML",
                        reply_markup=kb_admin_panel(),
                        disable_web_page_preview=True,
                    )
                except TelegramError as e:
                    await msg.reply_text(
                        f"⚠️ Kaналга yuborishda xato: {e}\n\n"
                        f"✅ Lekin kino saqlandi! Kod: <code>{code}</code>",
                        parse_mode="HTML",
                        reply_markup=kb_admin_panel(),
                    )
            else:
                await msg.reply_text(
                    f"✅ <b>Kino saqlandi!</b>\n\n"
                    f"🔢 Kod: <code>{code}</code>\n"
                    f"🎬 Nomi: {title}\n\n"
                    f"⚠️ Kino kanali ulanmagan.",
                    parse_mode="HTML",
                    reply_markup=kb_admin_panel(),
                )
        else:
            await msg.reply_text("🎬 Iltimos, <b>video</b> yuboring!", parse_mode="HTML")
        return

    # ── STEP: Kanal qo'shish ─────────────────────────────────
    if step == "add_sub_channel" and is_adm:
        channel = text.strip()
        if not channel.startswith("@") and not channel.startswith("http"):
            await msg.reply_text("❗ Format: <code>@KanalNomi</code>", parse_mode="HTML")
            return
        if db.add_sub_channel(channel):
            await msg.reply_text(
                f"✅ <b>{channel}</b> majburiy obunaga qo'shildi!",
                parse_mode="HTML",
                reply_markup=kb_admin_panel(),
            )
        else:
            await msg.reply_text(f"⚠️ <b>{channel}</b> allaqachon mavjud.", parse_mode="HTML")
        db.set_step(user.id)
        return

    if step == "del_sub_channel" and is_adm:
        channel = text.strip()
        if db.remove_sub_channel(channel):
            await msg.reply_text(
                f"✅ <b>{channel}</b> o'chirildi!",
                parse_mode="HTML",
                reply_markup=kb_admin_panel(),
            )
        else:
            await msg.reply_text(f"❌ <b>{channel}</b> topilmadi.", parse_mode="HTML")
        db.set_step(user.id)
        return

    if step == "set_movie_channel" and is_adm:
        channel = text.strip()
        if not channel.startswith("@"):
            await msg.reply_text("❗ Format: <code>@KanalNomi</code>", parse_mode="HTML")
            return
        db.set_movie_channel(channel)
        db.set_step(user.id)
        await msg.reply_text(
            f"✅ Kino kanali: <b>{channel}</b>",
            parse_mode="HTML",
            reply_markup=kb_admin_panel(),
        )
        return

    # ── STEP: Admin qo'shish/o'chirish ───────────────────────
    if step == "add_admin" and user.id == OWNER_ID:
        if text.strip().isdigit():
            uid = int(text.strip())
            if db.add_admin(uid):
                await msg.reply_text(
                    f"✅ Admin qo'shildi: <code>{uid}</code>",
                    parse_mode="HTML",
                    reply_markup=kb_admin_panel(),
                )
            else:
                await msg.reply_text(f"⚠️ <code>{uid}</code> allaqachon admin.", parse_mode="HTML")
            db.set_step(user.id)
        else:
            await msg.reply_text("❗ Faqat ID raqam yuboring!", parse_mode="HTML")
        return

    if step == "del_admin" and user.id == OWNER_ID:
        if text.strip().isdigit():
            uid = int(text.strip())
            if db.remove_admin(uid):
                await msg.reply_text(
                    f"✅ Admin o'chirildi: <code>{uid}</code>",
                    parse_mode="HTML",
                    reply_markup=kb_admin_panel(),
                )
            else:
                await msg.reply_text(f"❌ <code>{uid}</code> admin emas.", parse_mode="HTML")
            db.set_step(user.id)
        else:
            await msg.reply_text("❗ Faqat ID raqam yuboring!", parse_mode="HTML")
        return

    # ── STEP: Userga xabar ───────────────────────────────────
    if step == "get_target_user" and is_adm:
        if text.strip().isdigit():
            db.set_step(user.id, "send_to_user", {"target": int(text.strip())})
            await msg.reply_text(
                "📝 Endi yubormoqchi bo'lgan xabaringizni yuboring:",
                reply_markup=ikb_cancel(),
            )
        else:
            await msg.reply_text("❗ Faqat ID raqam!", parse_mode="HTML")
        return

    if step == "send_to_user" and is_adm:
        target = step_data.get("target")
        if target:
            try:
                await ctx.bot.copy_message(
                    chat_id=target,
                    from_chat_id=msg.chat_id,
                    message_id=msg.message_id,
                )
                await msg.reply_text(
                    f"✅ Xabar <code>{target}</code> ga yuborildi!",
                    parse_mode="HTML",
                    reply_markup=kb_admin_panel(),
                )
            except TelegramError as e:
                await msg.reply_text(f"❌ Xabar yuborishda xato: {e}")
        db.set_step(user.id)
        return

    # ── STEP: Broadcast ──────────────────────────────────────
    if step == "broadcast" and is_adm:
        db.set_step(user.id)
        users = db.get_all_users()
        prog  = await msg.reply_text(f"🔄 <b>Yuborilmoqda... 0/{len(users)}</b>", parse_mode="HTML")
        ok, err = await broadcast_message(ctx.bot, users, msg.chat_id, msg.message_id)
        await prog.edit_text(
            f"✅ <b>Xabarnoma tugadi!</b>\n\n"
            f"✅ Muvaffaqiyatli: {ok}\n"
            f"❌ Xato: {err}\n"
            f"👥 Jami: {len(users)}",
            parse_mode="HTML",
        )
        return

    # ── Kino kodi (oddiy user) ───────────────────────────────
    if text.isdigit():
        if not db.is_bot_active() and not is_adm:
            await msg.reply_text("⛔️ <b>Bot vaqtinchalik o'chirilgan.</b>", parse_mode="HTML")
            return
        if not is_adm and not await check_subscription(ctx.bot, user.id):
            return
        await send_movie(update, ctx, int(text))
        return

    # ── Noma'lum xabar ───────────────────────────────────────
    if not is_adm and not db.is_bot_active():
        await msg.reply_text("⛔️ <b>Bot vaqtinchalik o'chirilgan.</b>", parse_mode="HTML")
        return

    if not is_adm:
        await msg.reply_text(
            "🔢 Kino kodini yuboring yoki /start ni bosing.",
            parse_mode="HTML",
        )


# ═══════════════════════════════════════════════════════════════
#  🔵 CALLBACK QUERY HANDLER
# ═══════════════════════════════════════════════════════════════
async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    q      = update.callback_query
    user   = q.from_user
    data   = q.data
    is_adm = db.is_admin(user.id)

    await q.answer()

    # ── Obuna tekshirish ─────────────────────────────────────
    if data == "check_sub":
        is_subscribed = await check_subscription(ctx.bot, user.id, check_only=True)
        if is_subscribed:
            await q.message.delete()
            me       = await ctx.bot.get_me()
            movie_ch = db.get_movie_channel()
            await ctx.bot.send_message(
                chat_id=user.id,
                text="✅ <b>Obuna tasdiqlandi! Kino kodini yuboring.</b>",
                parse_mode="HTML",
                reply_markup=ikb_main_user(movie_ch, me.username),
            )
        else:
            await q.answer("❌ Hali barcha kanallarga obuna bo'lmagansiz!", show_alert=True)
        return

    # ── Yordam ───────────────────────────────────────────────
    if data == "help":
        await q.message.reply_text(
            "ℹ️ <b>Yordam</b>\n\n"
            "🔢 Kino kodini yuboring → kino olasiz\n"
            "/start — Botni qayta ishga tushirish",
            parse_mode="HTML",
        )
        return

    # ── ADMIN: Panel ─────────────────────────────────────────
    if data == "admin_panel" and is_adm:
        await q.message.edit_text(
            f"🖥 <b>Admin Panel</b>\n\n"
            f"👥 Foydalanuvchilar: {db.get_user_count()} ta\n"
            f"🎬 Kinolar: {db.get_movie_count()} ta",
            parse_mode="HTML",
        )
        return

    # ── ADMIN: Kanallar menyusi ───────────────────────────────
    if data == "channels_menu" and is_adm:
        await q.message.edit_text(
            "📢 <b>Kanallar sozlamalari:</b>",
            parse_mode="HTML",
            reply_markup=ikb_channels_menu(),
        )
        return

    if data == "sub_channels" and is_adm:
        channels = db.get_sub_channels()
        ch_list  = "\n".join(f"• {c}" for c in channels) if channels else "Hali kanal qo'shilmagan"
        await q.message.edit_text(
            f"📢 <b>Majburiy obuna kanallar:</b>\n{ch_list}",
            parse_mode="HTML",
            reply_markup=ikb_sub_channels_menu(),
        )
        return

    if data == "add_sub_ch" and is_adm:
        db.set_step(user.id, "add_sub_channel")
        await q.message.edit_text(
            "📢 Kanal username yuboring:\n\n📄 Namuna: <code>@KanalNomi</code>",
            parse_mode="HTML",
            reply_markup=ikb_cancel(),
        )
        return

    if data == "del_sub_ch" and is_adm:
        channels = db.get_sub_channels()
        if not channels:
            await q.answer("Hali kanal qo'shilmagan!", show_alert=True)
            return
        db.set_step(user.id, "del_sub_channel")
        ch_list = "\n".join(channels)
        await q.message.edit_text(
            f"🗑 O'chiriladigan kanal username yuboring:\n\n<code>{ch_list}</code>",
            parse_mode="HTML",
            reply_markup=ikb_cancel(),
        )
        return

    if data == "list_sub_ch" and is_adm:
        channels = db.get_sub_channels()
        ch_list  = "\n".join(f"• {c}" for c in channels) if channels else "Hali kanal qo'shilmagan"
        await q.answer(ch_list, show_alert=True)
        return

    if data == "movie_channel" and is_adm:
        current = db.get_movie_channel() or "Qo'shilmagan"
        await q.message.edit_text(
            f"🎬 <b>Hozirgi kino kanali:</b> {current}",
            parse_mode="HTML",
            reply_markup=ikb_movie_channel_menu(),
        )
        return

    if data == "set_movie_ch" and is_adm:
        db.set_step(user.id, "set_movie_channel")
        await q.message.edit_text(
            "🎬 Kino kanali username yuboring:\n\n📄 Namuna: <code>@KinalNomi</code>",
            parse_mode="HTML",
            reply_markup=ikb_cancel(),
        )
        return

    # ── ADMIN: Xabarnoma ─────────────────────────────────────
    if data == "broadcast_all" and is_adm:
        users = db.get_all_users()
        db.set_step(user.id, "broadcast")
        await q.message.edit_text(
            f"📨 <b>{len(users)} ta</b> foydalanuvchiga yubormoqchi bo'lgan xabaringizni yuboring:",
            parse_mode="HTML",
            reply_markup=ikb_cancel(),
        )
        return

    if data == "broadcast_user" and is_adm:
        db.set_step(user.id, "get_target_user")
        await q.message.edit_text(
            "👤 Foydalanuvchi ID sini yuboring:",
            reply_markup=ikb_cancel(),
        )
        return

    # ── ADMIN: Statistika ─────────────────────────────────────
    if data == "stat_daily" and is_adm:
        today     = datetime.now().strftime("%d.%m.%Y")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")
        t_count   = db.get_users_by_date(today)
        y_count   = db.get_users_by_date(yesterday)
        await q.answer(
            f"📅 Bugun: {t_count} ta\n📅 Kecha: {y_count} ta",
            show_alert=True,
        )
        return

    if data == "stat_monthly" and is_adm:
        this_month = datetime.now().strftime("%m.%Y")
        last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%m.%Y")
        t_count    = db.get_users_by_month(this_month)
        l_count    = db.get_users_by_month(last_month)
        await q.answer(
            f"📆 Shu oy: {t_count} ta\n📆 O'tgan oy: {l_count} ta",
            show_alert=True,
        )
        return

    if data == "stat_movies" and is_adm:
        movies = db.get_all_movies()
        total  = len(movies)
        top    = sorted(movies, key=lambda x: x.get("downloads", 0), reverse=True)[:3]
        top_str = "\n".join(
            f"#{m['code']} — {m['title'][:20]} ({m.get('downloads',0)} ta)"
            for m in top
        )
        no_movies = "Hali yo'q"
        await q.answer(
            f"🎬 Jami kinolar: {total} ta\n\n🔥 Top 3:\n{top_str or no_movies}",
            show_alert=True,
        )
        return

    # ── ADMIN: Bot holati ─────────────────────────────────────
    if data == "toggle_bot" and is_adm:
        new_state = db.toggle_bot()
        status    = "✅ Yoqilgan" if new_state else "❌ O'chirilgan"
        await q.message.edit_text(
            f"🤖 <b>Bot holati o'zgartirildi!</b>\n\nHozirgi holat: {status}",
            parse_mode="HTML",
            reply_markup=ikb_bot_status(new_state),
        )
        return

    # ── ADMIN: Adminlar ───────────────────────────────────────
    if data == "list_admins" and is_adm:
        admins  = db.get_admins()
        a_str   = "\n".join(f"• <code>{a}</code>" for a in admins)
        await q.answer(f"👮 Adminlar:\n" + "\n".join(str(a) for a in admins), show_alert=True)
        return

    if data == "add_admin" and user.id == OWNER_ID:
        db.set_step(user.id, "add_admin")
        await q.message.edit_text(
            "👮 Yangi admin Telegram ID sini yuboring:",
            reply_markup=ikb_cancel(),
        )
        return

    if data == "del_admin" and user.id == OWNER_ID:
        db.set_step(user.id, "del_admin")
        await q.message.edit_text(
            "🗑 O'chiriladigan admin ID sini yuboring:",
            reply_markup=ikb_cancel(),
        )
        return

    # ── Kino o'chirish ───────────────────────────────────────
    if data.startswith("del_movie_") and is_adm:
        code = int(data.split("_")[-1])
        if db.delete_movie(code):
            await q.message.edit_text(
                f"✅ #{code} kino o'chirildi.",
                reply_markup=ikb_back_to_panel(),
            )
        else:
            await q.answer("❌ Kino topilmadi!", show_alert=True)
        return

    # ── Bekor qilish ─────────────────────────────────────────
    if data == "cancel_step":
        db.set_step(user.id)
        await q.message.delete()
        if is_adm:
            await ctx.bot.send_message(
                chat_id=user.id,
                text="❌ Bekor qilindi.",
                reply_markup=kb_admin_panel(),
            )
        return


# ═══════════════════════════════════════════════════════════════
#  🎬 KINO YUBORISH
# ═══════════════════════════════════════════════════════════════
async def send_movie(update: Update, ctx: ContextTypes.DEFAULT_TYPE, code: int) -> None:
    user     = update.effective_user
    movie    = db.get_movie(code)
    movie_ch = db.get_movie_channel()
    me       = await ctx.bot.get_me()

    if not movie:
        await update.message.reply_text(
            "❌ <b>Bunday kod mavjud emas.</b>",
            parse_mode="HTML",
        )
        return

    db.movie_downloaded(code)
    downloads = movie.get("downloads", 0) + 1
    title     = movie["title"]
    file_id   = movie["file_id"]

    caption = (
        f"🍿 <b>{title}</b>\n\n"
        f"🔢 Kod: <code>{code}</code>\n"
        f"🗂 Yuklashlar: {downloads}\n"
    )
    if movie_ch:
        caption += f"📢 Kanal: {movie_ch}\n"
    caption += f"🤖 Bot: @{me.username}"

    try:
        await update.message.reply_video(
            video=file_id,
            caption=caption,
            parse_mode="HTML",
            reply_markup=ikb_movie(code, me.username, movie_ch),
        )
    except TelegramError:
        # Video yuborishda xato bo'lsa, document sifatida yuboramiz
        try:
            await update.message.reply_document(
                document=file_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=ikb_movie(code, me.username, movie_ch),
            )
        except TelegramError as e:
            await update.message.reply_text(f"❌ Kino yuborishda xato: {e}")


# ═══════════════════════════════════════════════════════════════
#  📋 KINO RO'YXATI
# ═══════════════════════════════════════════════════════════════
async def show_movie_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    movies = db.get_all_movies()
    if not movies:
        await update.message.reply_text("🎬 Hali kino yuklanmagan.", reply_markup=kb_admin_panel())
        return

    text = f"🎬 <b>Jami kinolar: {len(movies)} ta</b>\n\n"
    for m in movies[-20:]:  # Oxirgi 20 ta
        text += (
            f"🔢 #{m['code']} — {m['title'][:30]}\n"
            f"   📥 {m.get('downloads', 0)} yuklash | {m.get('added', '')}\n\n"
        )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb_admin_panel())


# ═══════════════════════════════════════════════════════════════
#  📊 STATISTIKA
# ═══════════════════════════════════════════════════════════════
async def show_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    today      = datetime.now().strftime("%d.%m.%Y")
    this_month = datetime.now().strftime("%m.%Y")
    yesterday  = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")

    total      = db.get_user_count()
    today_cnt  = db.get_users_by_date(today)
    yest_cnt   = db.get_users_by_date(yesterday)
    month_cnt  = db.get_users_by_month(this_month)
    movies_cnt = db.get_movie_count()

    await update.message.reply_text(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total}</b>\n"
        f"📅 Bugun qo'shildi: <b>{today_cnt}</b>\n"
        f"📅 Kecha qo'shildi: <b>{yest_cnt}</b>\n"
        f"📆 Shu oy: <b>{month_cnt}</b>\n\n"
        f"🎬 Jami kinolar: <b>{movies_cnt}</b>",
        parse_mode="HTML",
        reply_markup=ikb_stats_menu(),
    )


# ═══════════════════════════════════════════════════════════════
#  📥 KINO YUKLASH BOSHLASH
# ═══════════════════════════════════════════════════════════════
async def start_movie_upload(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    db.set_step(user.id, "upload_photo")
    await update.message.reply_text(
        "📸 <b>1-qadam:</b> Kino uchun <b>rasm</b> yuboring:",
        parse_mode="HTML",
        reply_markup=ikb_cancel(),
    )


# ═══════════════════════════════════════════════════════════════
#  🔍 INLINE QIDIRUV HANDLER
# ═══════════════════════════════════════════════════════════════
async def inline_query_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Inline qidiruv - kinolarni nomi bo'yicha qidirish"""
    query = update.inline_query.query
    if not query or len(query) < 2:
        return
    
    # Kinolarni qidirish
    movies = db.search_movies(query)
    
    results = []
    for movie in movies[:50]:  # Telegram limit: 50 ta result
        title = movie.get("title", "Nomsiz kino")
        code = movie.get("code", 0)
        
        result = InlineQueryResultArticle(
            id=str(code),
            title=title,
            description=f"Kino kodi: #{code}",
            input_message_content=InputTextMessageContent(
                f"🔍 <b>{title}</b>\n\n"
                f"🔢 Kod: <code>#{code}</code>\n"
                f"🤖 Bot: @{ctx.bot.username}",
                parse_mode="HTML"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Kino ko'rish", callback_data=f"view_movie_{code}")]
            ])
        )
        results.append(result)
    
    await update.inline_query.answer(results, cache_time=300)
