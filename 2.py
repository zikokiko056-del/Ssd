import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from pytube import YouTube


# --------- FUNCTIONS ---------

def download_youtube_mp4(url):
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    filename = "video.mp4"
    stream.download(filename=filename)
    return filename


def download_youtube_mp3(url):
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()

    filename = "audio.mp3"
    out_file = stream.download(filename="audio.mp3")

    return filename


# --------- TELEGRAM HANDLERS ---------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 مرحباً! أرسل رابط فيديو وسأعطيك خيارات MP3 / MP4")


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    # نحفظ الرابط داخل context حتى نستعمله لاحقاً
    context.user_data["url"] = url

    # نرسل أزرار الاختيار
    keyboard = [
        [
            InlineKeyboardButton("🎬 MP4", callback_data="mp4"),
            InlineKeyboardButton("🎵 MP3", callback_data="mp3")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر نوع التحميل:", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice = query.data
    url = context.user_data.get("url")

    await query.edit_message_text("⏳ جاري التحميل...")

    try:
        if choice == "mp4":
            file_path = download_youtube_mp4(url)
            await query.message.reply_video(video=open(file_path, "rb"))
        else:
            file_path = download_youtube_mp3(url)
            await query.message.reply_audio(audio=open(file_path, "rb"))

        # حذف الملف
        os.remove(file_path)

    except Exception as e:
        await query.message.reply_text(f"❌ خطأ: {str(e)}")


# --------- START BOT ---------

TOKEN = "8263136641:AAHVlEFKXQ8aAVuueVDeEJ7xrVdz3JiD0jY"

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(button))

print("🤖 البوت يعمل...")
app.run_polling()