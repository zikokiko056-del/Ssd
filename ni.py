import telebot

TOKEN = "8263136641:AAHVlEFKXQ8aAVuueVDeEJ7xrVdz3JiD0jY"
ADMIN_ID = 8431804711

bot = telebot.TeleBot(TOKEN)

# --- وظيفة التحقق من الإدمن ---
def is_admin(message):
    return message.from_user.id == ADMIN_ID

# --- توليد BIO ---
def generate_bio(text):
    return f"""
━━━━━━━━━━━━━━━━
🔥 Bio Instagram
━━━━━━━━━━━━━━━━
{text}
━━━━━━━━━━━━━━━━
❤️ Made by Your Bot
━━━━━━━━━━━━━━━━
"""

# --- زخرفة الاسم ---
def decorate_name(name):
    styles = [
        f"★ {name} ★",
        f"✦ {name} ✦",
        f"❖ {name} ❖",
        f"꧁ {name} ꧂",
        f"『 {name} 』",
        f"⟨ {name} ⟩"
    ]
    return "\n".join(styles)

# --- أمر bio ---
@bot.message_handler(commands=['bio'])
def bio(message):
    if not is_admin(message):
        bot.reply_to(message, "❌ هاد الأمر غير مسموح بيه.")
        return

    text = message.text.replace("/bio", "").strip()
    if text == "":
        bot.reply_to(message, "اكتب هكذا:\n/bio النص ديال البايو")
        return

    bot.reply_to(message, generate_bio(text))

# --- أمر زخرفة ---
@bot.message_handler(commands=['zkhrafa'])
def zkhrafa(message):
    if not is_admin(message):
        bot.reply_to(message, "❌ هاد الأمر غير مسموح بيه.")
        return

    name = message.text.replace("/zkhrafa", "").strip()
    if name == "":
        bot.reply_to(message, "اكتب هكذا:\n/zkhrafa الاسم")
        return

    bot.reply_to(message, decorate_name(name))

# --- رسالة ترحيب ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "مرحبا! البوت خدام. الأوامر:\n/bio\n/zkhrafa")

# تشغيل البوت
bot.polling()