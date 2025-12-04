import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import yt_dlp
import os

logging.basicConfig(level=logging.INFO)

TOKEN = "8315679351:AAFLUUZqlhF4zFlTEPfFrhP0qoEJ70egfFE"  # ⚠️ دخل التوكن الجديد هنا

#----- /start -----
async def start(update, context):
    await update.message.reply_text(
        "👋 مرحبا! صيفط رابط ديال اليوتيوب.\n\n"
        "🎵 لأي رابط كيظهر ليك اختيار:\n"
        "- تحميل MP4\n"
        "- تحميل MP3"
    )

#----- استقبال الرسالة -----
async def handle_link(update, context):
    url = update.message.text.strip()

    await update.message.reply_text(
        "🔽 اختر صيغة التحميل:",
        reply_markup=telegram.InlineKeyboardMarkup([
            [telegram.InlineKeyboardButton("🎬 MP4", callback_data=f"mp4|{url}")],
            [telegram.InlineKeyboardButton("🎵 MP3", callback_data=f"mp3|{url}")]
        ])
    )

#----- معالجة الاختيار -----
async def button(update, context):
    query = update.callback_query
    await query.answer()

    format_type, url = query.data.split("|")

    await query.edit_message_text("⏳ جاري التحميل… كن معي!")

    try:
        if format_type == "mp3":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "%(title)s.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }]
            }
        else:  # MP4
            ydl_opts = {
                "format": "mp4",
                "outtmpl": "%(title)s.%(ext)s"
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # إرسال الملف
        file = open(filename, "rb")
        if format_type == "mp3":
            await query.message.reply_audio(audio=file)
        else:
            await query.message.reply_video(video=file)
        file.close()

        # حذف الملف من الهاتف
        os.remove(filename)

        await query.message.reply_text("✅ تم التحميل!")

    except Exception as e:
        await query.edit_message_text(f"❌ خطأ: {e}")

#----- MAIN -----
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(telegram.ext.CallbackQueryHandler(button))

    app.run_polling()  # تشغيل البوت بطريقة صحيحة بدون Conflict

if __name__ == "__main__":
    import telegram
    main()