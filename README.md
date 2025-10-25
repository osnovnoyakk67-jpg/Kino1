# Kino1
from telegram import (
    Update, InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    InlineQueryHandler, CallbackQueryHandler, ContextTypes, filters
)
import json, re, uuid, os

# 🔑 O'z bot tokeningizni yozing
TOKEN = "7864342626:AAHd7Yp4BrZj7dojj93lKZtlRF4MKPocMTY"   # <-- Masalan: 123456789:ABCdefGhIjKlmNopQRstuVwxYZ

# 🗃️ Faylga saqlanadigan baza
DB_FILE = "kino_db.json"


# === Baza funksiyalari ===
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# === /start komandasi ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Salom! Men *Kino Qidiruvchi Bot*man.\n\n"
        "📥 Guruhga video tashlang (caption bilan) — men uni saqlab qo‘yaman.\n"
        "🔍 Keyin har qanday chatda yozing:\n"
        "`@Primekino_robot avatar`\n\n"
        "va filmni topib, yuklab oling! 🍿",
        parse_mode="Markdown"
    )


# === Guruhga video tashlansa saqlaydi ===
async def save_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.video and update.message.caption:
        db = load_db()
        title = update.message.caption.strip()
        file_id = update.message.video.file_id

        # Avval saqlangan bo‘lsa, qaytmasin
        for film in db:
            if film["file_id"] == file_id:
                await update.message.reply_text("⚠️ Bu video allaqachon bazada bor.")
                return

        # Har bir filmga unikal qisqa ID beramiz
        uid = str(uuid.uuid4())[:8]
        db.append({"uid": uid, "title": title, "file_id": file_id})
        save_db(db)

        await update.message.reply_text(f"✅ *{title}* bazaga saqlandi!", parse_mode="Markdown")


# === Inline qidiruv (yozilgan nom bo‘yicha) ===
async def inline_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip().lower()
    if not query:
        return

    db = load_db()
    results = []

    for film in db:
        if query in film["title"].lower():
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title=film["title"],
                    input_message_content=InputTextMessageContent(
                        f"🎬 *{film['title']}*\n\n📥 Yuklab olish uchun pastdagi tugmani bosing 👇",
                        parse_mode="Markdown"
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("📥 Yuklab olish", callback_data=f"get|{film['uid']}")]]
                    )
                )
            )

    await update.inline_query.answer(results[:20], cache_time=0)


# === Tugmani bosganda — foydalanuvchiga video yuborish ===
async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")

    if data[0] == "get":
        uid = data[1]
        db = load_db()

        for film in db:
            if film["uid"] == uid:
                await context.bot.send_video(chat_id=query.from_user.id, video=film["file_id"])
                await query.edit_message_text(
                    f"✅ *{film['title']}* yuborildi!", parse_mode="Markdown"
                )
                return

        await query.edit_message_text("❌ Fayl topilmadi.")


# === Asosiy ishga tushirish ===
async def error_handler(update, context):
    print(f"Xato: {context.error}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VIDEO & filters.ChatType.GROUPS, save_video))
app.add_handler(InlineQueryHandler(inline_search))
app.add_handler(CallbackQueryHandler(send_video))
app.add_error_handler(error_handler)

print("🎥 Kino bot ishga tushdi...")
app.run_polling()
