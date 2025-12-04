import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai
import requests
import os

# ------------------------------
# CONFIG
# ------------------------------
BOT_TOKEN = "8438096029:AAFLuBsLxIxKoI9umE2-4dGx6QJ67OOrmkM"   # توكن تيليغرام
OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

# ------------------------------
#  FUNCTION: Analyze Media (video / image)
# ------------------------------
async def analyze_media(file_path):
    with open(file_path, "rb") as f:
        content = f.read()

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that analyzes videos and images and extracts Instagram captions, hashtags and keywords."},
            {"role": "user", "content": [
                {"type": "input_media", "media_type": "image", "image_url": f"file://{file_path}"},
                {"type": "text", "text": "حلل هذا الفيديو/الصورة واستخرج Caption + Strong Hashtags + Viral Hashtags + Keywords."}
            ]}
        ]
    )

    return response.choices[0].message["content"]

# ------------------------------
#  START COMMAND
# ------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أرسل لي أي صورة أو فيديو، وأنا سنعطيك:\n\n- Caption جاهز للنشر\n- أفضل Hashtags قوية\n- Hashtags Viral\n- Keywords\n\n🔥 جاهز نخدم!")

# ------------------------------
#  HANDLE MEDIA
# ------------------------------
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = None

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
    elif update.message.video:
        file_id = update.message.video.file_id

    if not file_id:
        return await update.message.reply_text("أرسل صورة أو فيديو فقط 👍")

    file = await context.bot.get_file(file_id)
    file_path = f"media_{file_id}.mp4" if update.message.video else f"media_{file_id}.jpg"
    await file.download_to_drive(file_path)

    await update.message.reply_text("⏳ جاري التحليل…")

    result = await analyze_media(file_path)

    await update.message.reply_text(f"✨ النتيجة جاهزة:\n\n{result}")

    os.remove(file_path)

# ------------------------------
#  MAIN
# ------------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

    print("🔥 البوت خدام…")
    app.run_polling()

if __name__ == "__main__":
    main()