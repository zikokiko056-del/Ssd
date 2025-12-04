import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# المكتبات المطلوبة لكل منصة
try:
    from pytube import YouTube
except ImportError:
    os.system("pip install pytube")
    from pytube import YouTube

try:
    import instaloader
except ImportError:
    os.system("pip install instaloader")
    import instaloader

try:
    from facebook_scraper import get_posts
except ImportError:
    os.system("pip install facebook-scraper")
    from facebook_scraper import get_posts

# دوال التحميل
def download_youtube(url):
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    filename = "youtube_video.mp4"
    stream.download(output_path=".", filename=filename)
    return filename

def download_instagram(url):
    L = instaloader.Instaloader()
    shortcode = url.split("/")[-2]
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    target_folder = "instagram_video"
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    L.download_post(post, target=target_folder)
    # يرجع اسم الملف الأخير المحمل
    files = os.listdir(target_folder)
    files.sort(key=lambda x: os.path.getctime(os.path.join(target_folder, x)))
    return os.path.join(target_folder, files[-1])

def download_facebook(url):
    for post in get_posts(urls=[url], pages=1):
        if 'video' in post and post['video'] is not None:
            video_url = post['video']
            filename = "facebook_video.mp4"
            r = requests.get(video_url)
            with open(filename, "wb") as f:
                f.write(r.content)
            return filename
    return None

# بوت تيليجرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 مرحبا! أرسل لي رابط فيديو من يوتيوب، إنستغرام أو فيسبوك وسأرسله لك مباشرة.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("⏳ جاري التحميل...")
    
    try:
        if "youtube.com" in url or "youtu.be" in url:
            filename = download_youtube(url)
        elif "instagram.com" in url:
            filename = download_instagram(url)
        elif "facebook.com" in url:
            filename = download_facebook(url)
            if filename is None:
                await update.message.reply_text("❌ لم يتم العثور على فيديو في الرابط أو الفيديو محمي.")
                return
        else:
            await update.message.reply_text("❌ الرابط غير مدعوم!")
            return

        # إرسال الفيديو للمستخدم
        await update.message.reply_video(video=open(filename, "rb"))
        os.remove(filename)  # مسح الملف بعد الإرسال

    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")

# إعداد التطبيق
app = ApplicationBuilder().token("8263136641:AAHVlEFKXQ8aAVuueVDeEJ7xrVdz3JiD0jY").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 البوت شغال...")
app.run_polling()