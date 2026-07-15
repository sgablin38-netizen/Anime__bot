import json
import os
import random
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, ChatPermissions
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

# ===================================================
#  تنظیمات — اینا رو عوض کن
# ===================================================
BOT_TOKEN = "8001776384:AAGGKYTDH9sRTPBog7XuVA5cJgbaDLwbTzY"

# همه ادمین‌ها — آیدی عددی هر کدوم رو اضافه کن
ADMIN_IDS = [
    7030523670,   # ادمین اول
    5287603496,   # ادمین دوم
]

ADMIN_CONTACTS = [
    {"name": "ادمین اول", "username": "@Kamal0514_H"},
    {"name": "ادمین دوم", "username": "@RoronoaZoro_1999"},
]

REQUIRED_CHANNELS = [
    {"name": "کانال اول", "username": "@channel1", "link": "https://t.me/Purgatory_anime_Chanel"},
    {"name": "کانال دوم", "username": "@channel2", "link": "@Hentai_of_Purgatory"},
]
# ===================================================

DB_FILE      = "anime.json"
SUGGEST_FILE = "suggest.json"


# ──────────────────────────────────────────────────
#  توابع کمکی
# ──────────────────────────────────────────────────

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def load_db() -> dict:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_db(db: dict):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def load_suggest() -> list:
    if os.path.exists(SUGGEST_FILE):
        with open(SUGGEST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_suggest(data: list):
    with open(SUGGEST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────────
#  Reply Keyboard
# ──────────────────────────────────────────────────

def main_reply_keyboard():
    keyboard = [
        [KeyboardButton("🎌  انیمه‌ها")],
        [KeyboardButton("👤 ارتباط با ادمین‌ها"), KeyboardButton("📢 کانال‌های ما")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


# ──────────────────────────────────────────────────
#  چک عضویت اجباری
# ──────────────────────────────────────────────────

async def check_membership(user_id: int, bot) -> bool:
    for ch in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch["username"], user_id=user_id)
            if member.status in ("left", "kicked"):
                return False
        except Exception:
            return False
    return True

async def send_join_message(update: Update):
    keyboard = []
    for ch in REQUIRED_CHANNELS:
        keyboard.append([InlineKeyboardButton(f"📢 {ch['name']}", url=ch["link"])])
    keyboard.append([InlineKeyboardButton("✅ عضو شدم، بررسی کن", callback_data="check_join")])
    text = "⚠️ *برای استفاده از ربات باید عضو کانال‌های زیر باشی:*\n\nبعد از عضویت دکمه «عضو شدم» رو بزن."
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


# ──────────────────────────────────────────────────
#  منوی اصلی
# ──────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        if not await check_membership(user_id, context.bot):
            await send_join_message(update)
            return

    await update.message.reply_text(
        "🎌 *به ربات انیمه خوش اومدی!*\n\n• گزینه‌ی مورد نظر خود را انتخاب کنید.",
        reply_markup=main_reply_keyboard(),
        parse_mode="Markdown"
    )


# ──────────────────────────────────────────────────
#  هندلر دکمه‌های Reply Keyboard
# ──────────────────────────────────────────────────

async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text    = update.message.text
    user_id = update.effective_user.id

    if not is_admin(user_id):
        if not await check_membership(user_id, context.bot):
            await send_join_message(update)
            return

    if text == "🎌  انیمه‌ها":
        db = load_db()
        if not db:
            await update.message.reply_text("  انیمه‌ای اضافه نشده.")
            return
        keyboard = []
        for key, val in db.items():
            display = val.get("display_name", key)
            keyboard.append([InlineKeyboardButton(f"🎌 {display}", callback_data=f"anime_{key}")])
        await update.message.reply_text(
            "🎌 *انیمه‌های موجود:*\nروی اسم انیمه بزن:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif text == "👤 ارتباط با ادمین‌ها":
        keyboard = []
        for admin in ADMIN_CONTACTS:
            keyboard.append([InlineKeyboardButton(f"👤 {admin['name']}", url=f"https://t.me/{admin['username'].lstrip('@')}")])
        await update.message.reply_text(
            "👤 *ارتباط با ادمین‌ها:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif text == "📢 کانال‌های ما":
        keyboard = []
        for ch in REQUIRED_CHANNELS:
            keyboard.append([InlineKeyboardButton(f"📢 {ch['name']}", url=ch["link"])])
        await update.message.reply_text(
            "📢 *کانال‌های ما:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


# ──────────────────────────────────────────────────
#  بررسی عضویت
# ──────────────────────────────────────────────────

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    user_id = update.effective_user.id
    if await check_membership(user_id, context.bot):
        await query.edit_message_text("✅ عضویت تأیید شد!")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="🎌 *به ربات انیمه خوش اومدی!*\n\n• گزینه‌ی مورد نظر خود را انتخاب کنید.",
            reply_markup=main_reply_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await query.answer("❌ هنوز عضو همه کانال‌ها نشدی!", show_alert=True)


# ──────────────────────────────────────────────────
#  بازی /gm در گروه
#  کاربر /gm میزنه، ربات میگه عدد 1 تا 6 انتخاب کن
#  اگه عدد کاربر == عدد رندم ربات → بن میشه
# ──────────────────────────────────────────────────

async def gm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """فقط تو گروه کار میکنه"""
    if update.effective_chat.type not in ("group", "supergroup"):
        await update.message.reply_text("این دستور فقط تو گروه کار میکنه!")
        return

    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=f"gm_{update.effective_user.id}_1"),
            InlineKeyboardButton("2", callback_data=f"gm_{update.effective_user.id}_2"),
            InlineKeyboardButton("3", callback_data=f"gm_{update.effective_user.id}_3"),
        ],
        [
            InlineKeyboardButton("4", callback_data=f"gm_{update.effective_user.id}_4"),
            InlineKeyboardButton("5", callback_data=f"gm_{update.effective_user.id}_5"),
            InlineKeyboardButton("6", callback_data=f"gm_{update.effective_user.id}_6"),
        ],
    ]

    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"🎲 *{user_name}* یه عدد بین ۱ تا ۶ انتخاب کن!\n\n"
        f"⚠️ اگه عددت با عدد ربات یکی بشه، بن میشی!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def gm_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وقتی کاربر عدد رو انتخاب کرد"""
    query   = update.callback_query
    data    = query.data  # فرمت: gm_userid_number

    parts      = data.split("_")
    target_uid = int(parts[1])
    user_choice = int(parts[2])

    # فقط همون کاربری که /gm زده میتونه انتخاب کنه
    if query.from_user.id != target_uid:
        await query.answer("این بازی مال تو نیست!", show_alert=True)
        return

    await query.answer()

    bot_number = random.randint(1, 6)
    user_name  = query.from_user.first_name

    if user_choice == bot_number:
        # بن!
        result_text = (
            f"🎲 عدد تو: *{user_choice}*\n"
            f"🤖 عدد ربات: *{bot_number}*\n\n"
            f"💀 یکی شدن! *{user_name}* بن شد!"
        )
        await query.edit_message_text(result_text, parse_mode="Markdown")

        try:
            await context.bot.ban_chat_member(
                chat_id=query.message.chat_id,
                user_id=target_uid
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"⚠️ نتونستم بن کنم. مطمئن شو ربات ادمین گروهه.\nخطا: {e}"
            )
    else:
        # نجات پیدا کرد
        result_text = (
            f"🎲 عدد تو: *{user_choice}*\n"
            f"🤖 عدد ربات: *{bot_number}*\n\n"
            f"✅ متفاوتن! *{user_name}* جون سالم به در برد! 😅"
        )
        await query.edit_message_text(result_text, parse_mode="Markdown")


# ──────────────────────────────────────────────────
#  صفحه یک انیمه
# ──────────────────────────────────────────────────

async def show_anime_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query     = update.callback_query
    await query.answer()
    anime_key = query.data[len("anime_"):]
    db        = load_db()

    if anime_key not in db:
        await query.edit_message_text("❌ انیمه پیدا نشد.")
        return

    display  = db[anime_key].get("display_name", anime_key)
    keyboard = [
        [InlineKeyboardButton("📖 خلاصه داستان",   callback_data=f"summary_{anime_key}")],
        [InlineKeyboardButton("📺 فصل‌ها",          callback_data=f"seasons_{anime_key}")],
        [InlineKeyboardButton("🔙 بازگشت به لیست", callback_data="back_animelist")],
    ]
    await query.edit_message_text(
        f"🎌 *{display}*\n\nیه گزینه انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ──────────────────────────────────────────────────
#  خلاصه داستان
# ──────────────────────────────────────────────────

async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query     = update.callback_query
    await query.answer()
    anime_key = query.data[len("summary_"):]
    db        = load_db()

    if anime_key not in db:
        await query.edit_message_text("❌ انیمه پیدا نشد.")
        return

    display  = db[anime_key].get("display_name", anime_key)
    summary  = db[anime_key].get("summary") or "📭 خلاصه‌ای ثبت نشده."
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data=f"anime_{anime_key}")]]
    await query.edit_message_text(
        f"📖 *{display}*\n\n{summary}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ──────────────────────────────────────────────────
#  لیست فصل‌ها
# ──────────────────────────────────────────────────

async def show_seasons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query     = update.callback_query
    await query.answer()
    anime_key = query.data[len("seasons_"):]
    db        = load_db()

    if anime_key not in db:
        await query.edit_message_text("❌ انیمه پیدا نشد.")
        return

    seasons = db[anime_key].get("seasons", {})
    display = db[anime_key].get("display_name", anime_key)

    if not seasons:
        await query.edit_message_text(
            f"😔 هنوز قسمتی برای *{display}* آپلود نشده.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data=f"anime_{anime_key}")]]),
            parse_mode="Markdown"
        )
        return

    keyboard = []
    for season_num in sorted(seasons.keys(), key=lambda x: int(x)):
        ep_count     = len(seasons[season_num].get("episodes", []))
        season_label = seasons[season_num].get("display", f"فصل {season_num}")
        keyboard.append([InlineKeyboardButton(f"📺 {season_label} ({ep_count} قسمت)", callback_data=f"season_{anime_key}|{season_num}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"anime_{anime_key}")])

    await query.edit_message_text(
        f"📺 *{display}* — فصل‌ها:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ──────────────────────────────────────────────────
#  ارسال قسمت‌های یک فصل
# ──────────────────────────────────────────────────

async def send_season(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query      = update.callback_query
    await query.answer()
    parts      = query.data[len("season_"):].split("|", 1)
    anime_key  = parts[0]
    season_num = parts[1]
    db         = load_db()

    if anime_key not in db:
        await query.edit_message_text("❌ انیمه پیدا نشد.")
        return

    seasons      = db[anime_key].get("seasons", {})
    display      = db[anime_key].get("display_name", anime_key)

    if season_num not in seasons:
        await query.edit_message_text("❌ فصل پیدا نشد.")
        return

    episodes     = seasons[season_num].get("episodes", [])
    season_label = seasons[season_num].get("display", f"فصل {season_num}")

    if not episodes:
        await query.edit_message_text(
            f"😔 قسمتی برای {season_label} آپلود نشده.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data=f"seasons_{anime_key}")]])
        )
        return

    await query.edit_message_text(f"📥 در حال ارسال {len(episodes)} قسمت از *{display} — {season_label}*...", parse_mode="Markdown")

    chat_id = query.message.chat_id
    for i, file_id in enumerate(episodes, start=1):
        try:
            await context.bot.send_document(chat_id=chat_id, document=file_id, caption=f"📺 {display} | {season_label} | قسمت {i}")
        except Exception:
            try:
                await context.bot.send_video(chat_id=chat_id, video=file_id, caption=f"📺 {display} | {season_label} | قسمت {i}")
            except Exception as e:
                await context.bot.send_message(chat_id=chat_id, text=f"⚠️ خطا در ارسال قسمت {i}: {e}")

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ همه قسمت‌های {season_label} ارسال شدن!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت به فصل‌ها", callback_data=f"seasons_{anime_key}")]])
    )


# ──────────────────────────────────────────────────
#  پنل ادمین — آپلود
#  فرمت: اسم انیمه | شماره فصل
# ──────────────────────────────────────────────────

async def admin_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        return

    file = update.message.video or update.message.document
    if not file:
        return

    caption = (update.message.caption or "").strip()
    if "|" not in caption:
        await update.message.reply_text("❗ فرمت:\nاسم انیمه | شماره فصل\n\nمثال:\nAttack on Titan | 1")
        return

    parts        = caption.split("|", 1)
    display_name = parts[0].strip()
    season_num   = parts[1].strip()
    anime_key    = display_name.lower()
    db           = load_db()

    if anime_key not in db:
        db[anime_key] = {"display_name": display_name, "summary": "", "seasons": {}}
    if season_num not in db[anime_key]["seasons"]:
        db[anime_key]["seasons"][season_num] = {"display": f"فصل {season_num}", "episodes": []}

    db[anime_key]["seasons"][season_num]["episodes"].append(file.file_id)
    save_db(db)

    ep_count = len(db[anime_key]["seasons"][season_num]["episodes"])
    await update.message.reply_text(f"✅ قسمت اضافه شد!\n🎌 {display_name}\n📺 فصل {season_num} — قسمت {ep_count}")


async def admin_set_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/summary اسم انیمه | متن خلاصه"""
    if not is_admin(update.message.from_user.id):
        return
    text = " ".join(context.args)
    if "|" not in text:
        await update.message.reply_text("فرمت:\n/summary اسم انیمه | متن خلاصه")
        return
    parts        = text.split("|", 1)
    key          = parts[0].strip().lower()
    summary_text = parts[1].strip()
    db = load_db()
    if key not in db:
        await update.message.reply_text(f"❌ انیمه «{key}» پیدا نشد.")
        return
    db[key]["summary"] = summary_text
    save_db(db)
    await update.message.reply_text(f"✅ خلاصه برای «{db[key]['display_name']}» ثبت شد.")


async def admin_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/delete اسم | /delete اسم | فصل"""
    if not is_admin(update.message.from_user.id):
        return
    if not context.args:
        await update.message.reply_text("مثال:\n/delete Attack on Titan\n/delete Attack on Titan | 1")
        return
    text = " ".join(context.args)
    db   = load_db()
    if "|" in text:
        parts      = text.split("|", 1)
        key        = parts[0].strip().lower()
        season_num = parts[1].strip()
        if key not in db or season_num not in db[key]["seasons"]:
            await update.message.reply_text("❌ پیدا نشد.")
            return
        del db[key]["seasons"][season_num]
        save_db(db)
        await update.message.reply_text(f"✅ فصل {season_num} حذف شد.")
    else:
        key = text.strip().lower()
        if key not in db:
            await update.message.reply_text("❌ پیدا نشد.")
            return
        name = db[key]["display_name"]
        del db[key]
        save_db(db)
        await update.message.reply_text(f"✅ انیمه «{name}» حذف شد.")


async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/adminlist"""
    if not is_admin(update.message.from_user.id):
        return
    db = load_db()
    if not db:
        await update.message.reply_text("هیچ انیمه‌ای نیست.")
        return
    msg = "📋 *لیست انیمه‌ها:*\n\n"
    for val in db.values():
        seasons     = val.get("seasons", {})
        has_summary = "✅" if val.get("summary") else "❌"
        msg += f"🎌 *{val['display_name']}* | خلاصه: {has_summary}\n"
        for snum in sorted(seasons.keys(), key=lambda x: int(x)):
            msg += f"   📺 فصل {snum}: {len(seasons[snum].get('episodes', []))} قسمت\n"
        msg += "\n"
    await update.message.reply_text(msg, parse_mode="Markdown")


# ──────────────────────────────────────────────────
#  روتر callback
# ──────────────────────────────────────────────────

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data  = query.data

    if data == "check_join":
        await check_join(update, context)
        return

    await query.answer()

    if data == "back_animelist":
        db       = load_db()
        keyboard = [[InlineKeyboardButton(f"🎌 {v.get('display_name', k)}", callback_data=f"anime_{k}")] for k, v in db.items()]
        await query.edit_message_text("🎌 *انیمه‌های موجود:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data.startswith("gm_"):
        await gm_choice(update, context)
    elif data.startswith("anime_"):
        await show_anime_menu(update, context)
    elif data.startswith("summary_"):
        await show_summary(update, context)
    elif data.startswith("seasons_"):
        await show_seasons(update, context)
    elif data.startswith("season_"):
        await send_season(update, context)


# ──────────────────────────────────────────────────
#  اجرا
# ──────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("gm",        gm_command))
    app.add_handler(CommandHandler("summary",   admin_set_summary))
    app.add_handler(CommandHandler("delete",    admin_delete))
    app.add_handler(CommandHandler("adminlist", admin_list))

    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL, admin_upload))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Regex(
            "^(🎌  انیمه‌ها|👤 ارتباط با ادمین‌ها|📢 کانال‌های ما)$"
        ),
        handle_menu_buttons
    ))
    app.add_handler(CallbackQueryHandler(callback_router))

    print("✅ ربات شروع به کار کرد...")
    app.run_polling()


if __name__ == "__main__":
    main()