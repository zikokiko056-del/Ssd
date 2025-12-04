import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from pytube import YouTube
import instaloader
from facebook_scraper import get_posts


# ---------------- FUNCTIONS ----------------

def download_youtube(url):
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    filename = "youtube_video.mp4"
    stream.download(filename=filename)
    return filename


def download_instagram(url):
    L = instaloader.Instaloader(download_videos=True, save_metadata=False)
    shortcode = url.split("/")[-2]
    post = instaloader.Post.from_shortcode(L.context, shortcode)

    folder = "insta_dl"
    if not os.path.exists(folder):
        os.makedirs(folder)

    L.download_post(post, target=folder)

    files = os.listdir(folder)
    files = [f for f in files if f.endswith((".mp4", ".jpg", ".jpeg"))]
    files.sort(key=lambda x: os.path.getctime(os.path.join(folder, x)))

    return os.path.join(folder, files[-1])


def download_facebook(url):
    for post in get_posts(urls=[url], pages=1):
        if "video" in post and post["video"]:
            video_url = post["video"]
            filename = "facebook_video.mp4"
            r = requests.get(video_url)
            with open(filename, "wb") as f:
                f.write(r.content)
            return filename
    return None


# ---------------- TELEGRAM BOT ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحباً! أرسل رابط فيديو من:\n"
        "• YouTube\n• Instagram\n• Facebook\n"
        "وسأقوم بتحميله لك مباشرة 📥"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("⏳ جاري التحميل...")

    try:
        if "youtube.com" in url or "youtu.be" in url:
            file_path = download_youtube(url)

        elif "instagram.com" in url:
            file_path = download_instagram(url)

        elif "facebook.com" in url:
            file_path = download_facebook(url)
            if file_path is None:
                await update.message.reply_text("❌ لم يتم العثور على الفيديو.")
                return

        else:
            await update.message.reply_text("❌ الرابط غير مدعوم.")
            return

        # إرسال الفيديو
        await update.message.reply_video(video=open(file_path, "rb"))

        # حذف الملف بعد الإرسال
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")


# ---------------- START BOT ----------------

TOKEN = "YOUR_TOKEN_HERE"  # ضع التوكن هنا فقط

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 البوت يعمل الآن...")
app.run_polling()