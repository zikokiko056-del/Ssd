import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai
import os

BOT_TOKEN = "8438096029:AAFLuBsLxIxKoI9umE2-4dGx6QJ67OOrmkM"
OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🍀 صيفط ليا فيديو ولا صورة، ونحللها ونخرج ليك الهاشتاغ والشرح جاهز.")

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = None

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_path = "image.jpg"
    elif update.message.video:
        file_id = update.message.video.file_id
        file_path = "video.mp4"
    else:
        return await update.message.reply_text("🔹 صيفط صورة أو فيديو فقط.")

    file = await context.bot.get_file(file_id)
    await file.download_to_drive(file_path)

    await update.message.reply_text("⏳ كندير التحليل...")

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You analyze media and generate captions and hashtags."},
            {"role": "user", "content": "حلل هذه الصورة/الفيديو واستخرج Caption + hashtags + keywords."}
        ]
    )

    await update.message.reply_text(response.choices[0].message["content"])

    os.remove(file_path)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    print("🔥 البوت خدام...")
    app.run_polling()

if __name__ == "__main__":
    main()