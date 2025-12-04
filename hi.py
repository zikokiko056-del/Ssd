تمام — أعطيك مثال بسيط وعملي ببايثون يربط بوت تليجرام بالتوكن والـ chat_id (بدون الاعتماد على مكتبات خارجية إذا رغبت). ملاحظة مهمة قبل الكود: لا تَضع التوكن في أماكن عامة أو تشاركه — إذا كان التوكن الذي أرفقته حقيقيًا فأنصحك بإلغائه (revoke) وإنشاء توكن جديد لأنَّه الآن مكشوف. في الكود أدناه سأستخدم قراءة التوكن والآي دي من متغيّئات بيئة لتقليل خطر التسريب.

سكربت بسيط (باستخدام requests) — إرسال رسالة واستقبال آخر التحديثات

احفظه مثلاً كـ tg_bot_simple.py:

#!/usr/bin/env python3
"""
تشغيل: 
export TG_BOT_TOKEN="8263136641:AAHVlEFKXQ8aAVuueVDeEJ7xrVdz3JiD0jY"
export TG_CHAT_ID="8431804711"
python3 tg_bot_simple.py
"""

import os
import requests
import time

TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise SystemExit("ضع المتغيرات البيئية TG_BOT_TOKEN و TG_CHAT_ID قبل التشغيل.")

API_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(text):
    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, data=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def get_updates(offset=None, timeout=10):
    url = f"{API_URL}/getUpdates"
    params = {"timeout": timeout}
    if offset:
        params["offset"] = offset
    r = requests.get(url, params=params, timeout=timeout+5)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    # مثال: إرسال رسالة ترحيب
    resp = send_message("بوت بايثون متصل ✅")
    print("sendMessage response:", resp)

    # مثال بسيط على Polling لقراءة الرسائل الواردة
    print("بدء polling لقراءة التحديثات (اضغط Ctrl+C للإيقاف)...")
    last_update_id = None
    try:
        while True:
            updates = get_updates(offset=(last_update_id + 1) if last_update_id else None, timeout=15)
            if updates.get("ok"):
                for u in updates.get("result", []):
                    last_update_id = u["update_id"]
                    # مثال: استخرج نص الرسالة ومرسِلها
                    if "message" in u:
                        chat = u["message"]["chat"]["id"]
                        text = u["message"].get("text", "")
                        user = u["message"]["from"].get("username") or u["message"]["from"].get("first_name")
                        print(f"رسالة من {user} ({chat}): {text}")

                        # رد تلقائي بسيط
                        send_message(f"استلمت رسالتك، شكرًا {user}!")
            time.sleep(1)
    except KeyboardInterrupt:
        print("تم الإيقاف من قبل المستخدم.")
    except Exception as e:
        print("خطأ:", e)

تعليمات تشغيل سريعة

1. ثبّت requests لو لم تكن مثبتة:

pip install requests


2. قبل التشغيل، ضَع التوكن والآي دي كمتغيرات بيئة (مثال لينكس / macOS):

export TG_BOT_TOKEN="هنا_توكن_البوت"
export TG_CHAT_ID="8431804711"   # أو الآي دي الذي ترغب بإرسال الرسائل إليه
python3 tg_bot_simple.py



نقاط مهمة وأمان

لا تشارك التوكن في دردشات عامة؛ أي شخص يملك التوكن يمكنه التحكم ببوتك.

إن كان التوكن الذي أرفقته حقيقيًا فاستَبْطِلْه (revoke) واصنع توكن جديد من BotFather.

إن أردت ميزات أكثر تقدّمًا (أوامر، تحكم بالـ inline keyboards، webhook بدلاً من polling) أقدّم لك مثالًا باستخدام مكتبة python-telegram-bot أو aiogram — أيّ واحدة تفضّل؟


هل تريد أن أعدل الكود ليستخدم الـtoken والـchat_id اللذان أرسلتَهُم مباشرةً داخل السكربت (مع تحذير آخر عن المخاطر)، أو تريد مثالًا بمكتبة أكبر مثل python-telegram-bot؟