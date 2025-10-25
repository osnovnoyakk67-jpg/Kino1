# Kino1
    import logging
import uuid
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    InlineQueryHandler,
    ContextTypes,
)

# 🔹 Tokeningni shu yerga yoz
TOKEN = "7864342626:AAHd7Yp4BrZj7dojj93lKZtlRF4MKPocMTY"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# /start buyrug‘i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Salom! Kino bot ishga tushdi!\n\n"
        "Inline orqali qidirish uchun shunchaki yoz:\n"
        "@BotUsername kino nomi"
    )

# inline qidiruv
async def inline_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()

    if not query:
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title=f"Kino topildi: {query.title()}",
            description=f"{query.title()} haqida ma'lumot",
            input_message_content=InputTextMessageContent(
                f"🎥 {query.title()}\n"
                f"Kino haqida: bu sinov natijasi.\n\n"
                f"@{update.inline_query.from_user.username}"
            ),
        )
    ]

    await update.inline_query.answer(results, cache_time=1)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(InlineQueryHandler(inline_search))

    print("🎬 Kino bot ishga tushdi (Python 3.13 + PTB 20.7)")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
