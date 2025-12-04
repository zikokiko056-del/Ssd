#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import uuid
import asyncio
import logging
from functools import partial
from yt_dlp import YoutubeDL
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ---------------- إعدادات البوت ----------------

# ❗❗ ضع التوكن ديالك هنا ❗❗
TOKEN = "8394415105:AAHnyX8L_i3d1Ug-0C1suv6ucEQAQoXLBYA"

TMP_DIR = "downloads"
os.makedirs(TMP_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------

def detect_platform(url: str) -> str:
    url = url.lower()
    if "youtu" in url: return "YouTube"
    if "insta" in url: return "Instagram"
    if "facebook" in url or "fb.watch" in url: return "Facebook"
    if "tiktok" in url: return "TikTok"
    if "twitter" in url or "x.com" in url: return "Twitter"
    if "reddit" in url: return "Reddit"
    return "Unknown"

# ---------------- yt-dlp Downloader ----------------

def ytdlp_block(url, kind, cookiesfile=None):
    base = uuid.uuid4().hex
    outtmpl = os.path.join(TMP_DIR, base + ".%(ext)s")

    if kind == "mp4":
        opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": outtmpl,
            "quiet": True,
            "noplaylist": True,
        }
    else:
        opts = {
            "format": "bestaudio",
            "outtmpl": outtmpl,
            "quiet": True,
            "noplaylist": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }],
        }

    if cookiesfile:
        opts["cookiefile"] = cookiesfile

    with YoutubeDL(opts) as ydl:
        ydl.extract_info(url, download=True)

    # get produced file
    files = [f for f in os.listdir(TMP_DIR) if f.startswith(base)]
    files.sort(key=lambda f: os.path.getctime(os.path.join(TMP_DIR, f)))
    return os.path.join(TMP_DIR, files[-1])

async def download_async(url, kind, cookiesfile=None):
    loop = asyncio.get_event_loop()
    func = partial(ytdlp_block, url, kind, cookiesfile)
    return await loop.run_in_executor(None, func)

# ---------------- Handlers ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("YouTube"), KeyboardButton("Instagram")],
        [KeyboardButton("Facebook"), KeyboardButton("TikTok")],
        [KeyboardButton("Twitter/X"), KeyboardButton("Reddit")],
    ]
    await update.message.reply_text(
        "👋 مرحبا! أرسل رابط أي فيديو وسأعطيك خيارات MP3 / MP4.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # إذا كتب اسم منصة فقط
    if text.lower() in ["youtube", "instagram", "facebook", "tiktok", "twitter/x", "reddit"]:
        context.user_data["expected_platform"] = text
        await update.message.reply_text(f"✔️ جيد! الآن أرسل رابط {text}.")
        return

    # نعتبره رابط
    url = text
    platform = detect_platform(url)

    context.user_data["url"] = url

    buttons = [
        [
            InlineKeyboardButton("🎬 تحميل MP4", callback_data="mp4"),
            InlineKeyboardButton("🎵 تحميل MP3", callback_data="mp3"),
        ],
        [InlineKeyboardButton("📄 إضافة Cookies (اختياري)", callback_data="cookies")]
    ]

    await update.message.reply_text(
        f"🔗 الرابط: {platform}\nاختر نوع التحميل:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    url = context.user_data.get("url")

    if not url:
        return await query.message.reply_text("❌ المرجو إرسال الرابط أولا.")

    # cookies
    if data == "cookies":
        context.user_data["awaiting_cookies"] = True
        return await query.message.reply_text("📄 أرسل ملف cookies.txt الآن.")

    # mp3 / mp4
    kind = "mp4" if data == "mp4" else "mp3"
    await query.edit_message_text("⏳ جاري التحميل...")

    try:
        cookiesfile = context.user_data.get("cookiesfile")
        file_path = await download_async(url, kind, cookiesfile)
    except Exception as e:
        return await query.message.reply_text(f"❌ خطأ أثناء التحميل:\n{e}")

    # إرسال الملف
    try:
        if file_path.endswith(".mp3"):
            await query.message.reply_audio(audio=open(file_path, "rb"))
        else:
            try:
                await query.message.reply_video(video=open(file_path, "rb"))
            except:
                await query.message.reply_document(document=open(file_path, "rb"))
    except Exception as e:
        await query.message.reply_text(f"⚠️ خطأ أثناء إرسال الملف: {e}")

    try:
        os.remove(file_path)
    except:
        pass

async def file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_cookies"):
        doc = update.message.document
        if not doc:
            return await update.message.reply_text("❌ هذا ليس ملفاً.")

        newpath = os.path.join(TMP_DIR, "cookies_" + uuid.uuid4().hex + ".txt")
        await doc.get_file().download_to_drive(newpath)

        context.user_data["cookiesfile"] = newpath
        context.user_data["awaiting_cookies"] = False

        await update.message.reply_text("✔️ تم حفظ الكوكيز.\nالآن اختر MP3 أو MP4.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, file_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 البوت شغال...")
    app.run_polling()

if __name__ == "__main__":
    main()