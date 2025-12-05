import os
import redis
import requests
from telegram import Update
from telegram.ext import ContextTypes

# مراحل یادگیری
stages = [
    "پایه‌های پایتون",
    "ساختار داده‌ها",
    "کنترل جریان",
    "توابع",
    "برنامه‌نویسی شی‌گرا",
    "ماژول‌ها و بسته‌ها",
    "ورودی/خروجی فایل",
    "استثناها",
    "تست‌نویسی",
    "توسعه وب",
    "آماده‌سازی برای AWS",
    "آماده‌سازی شغلی"
]

# سوالات آزمون برای هر مرحله
quizzes = {
    0: {"question": "چگونه یک متغیر در پایتون تعریف می‌کنیم؟", "answer": "نام_متغیر = مقدار"},
    1: {"question": "لیست در پایتون چیست؟", "answer": "یک ساختار داده قابل تغییر"},
    2: {"question": "چگونه یک حلقه for در پایتون می‌نویسیم؟", "answer": "for item in iterable:"},
    3: {"question": "تابع در پایتون چگونه تعریف می‌شود؟", "answer": "def نام_تابع():"},
    4: {"question": "کلاس در پایتون چگونه تعریف می‌شود؟", "answer": "class نام_کلاس:"},
    5: {"question": "چگونه یک ماژول را import می‌کنیم؟", "answer": "import نام_ماژول"},
    6: {"question": "چگونه یک فایل را باز می‌کنیم؟", "answer": "open('نام_فایل')"},
    7: {"question": "چگونه یک استثنا را مدیریت می‌کنیم؟", "answer": "try: except:"},
    8: {"question": "unittest چیست؟", "answer": "یک فریمورک تست در پایتون"},
    9: {"question": "Flask چیست؟", "answer": "یک فریمورک وب در پایتون"},
    10: {"question": "AWS چیست؟", "answer": "Amazon Web Services"},
    11: {"question": "CV چیست؟", "answer": "Curriculum Vitae"}
}

# اتصال به Vercel KV
r = redis.from_url(os.getenv('KV_URL'))

# پرامپت سیستم برای DeepSeek
system_prompt = """شما یک منتور پایتون با ۲۰ سال تجربه هستید که فقط به زبان پارسی صحبت می‌کنید. شما برای بازار کار آلمان طراحی شده‌اید و بسیار سختگیر هستید. پاسخ‌های شما باید آموزنده، دقیق و حرفه‌ای باشند. هرگز از زبان انگلیسی استفاده نکنید."""

def call_deepseek(prompt):
    api_key = os.getenv('DEEPSEEK_API_KEY')
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return "خطا در ارتباط با API"

def get_progress(user_id):
    progress_str = r.get(f"user:{user_id}")
    if progress_str:
        return eval(progress_str.decode())
    return {"stage": 0, "non_tech": 0, "github_links": [], "quiz_passed": False, "waiting_github": False}

def save_progress(user_id, data):
    r.set(f"user:{user_id}", str(data))
    r.sadd("users", user_id)

def is_non_tech(text):
    tech_words = ["python", "code", "function", "class", "aws", "job", "cv", "def", "import", "for", "if", "try", "test", "web", "flask", "django"]
    return not any(word in text.lower() for word in tech_words)

def is_github_link(text):
    return "github.com" in text.lower()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    progress = get_progress(user_id)
    stage = progress["stage"]

    if stage >= 12:
        response = "شما همه مراحل را گذرانده‌اید! تبریک می‌گویم."
    else:
        if is_non_tech(text):
            progress["non_tech"] += 1
            if progress["non_tech"] >= 3:
                response = "هشدار نهایی: لطفا پیام‌های فنی ارسال کنید. در غیر این صورت، دسترسی شما محدود خواهد شد."
            else:
                response = call_deepseek(text)
        else:
            progress["non_tech"] = 0
            if progress.get("waiting_github", False):
                if is_github_link(text):
                    progress["github_links"].append(text)
                    progress["stage"] += 1
                    progress["waiting_github"] = False
                    progress["quiz_passed"] = False
                    if stage + 1 < 12:
                        response = f"مرحله {stage + 2} باز شد: {stages[stage + 1]}"
                    else:
                        response = "شما همه مراحل را گذرانده‌اید!"
                else:
                    response = "لینک گیت‌هاب معتبر نیست. لطفا لینک پروژه خود را ارسال کنید."
            elif not progress.get("quiz_passed", False):
                if text.lower().strip() == quizzes[stage]["answer"].lower().strip():
                    progress["quiz_passed"] = True
                    progress["waiting_github"] = True
                    response = "جواب درست! حالا لینک گیت‌هاب پروژه مربوط به این مرحله را ارسال کنید."
                else:
                    response = "جواب اشتباه. دوباره تلاش کنید یا سوال را مرور کنید."
            else:
                # شروع آزمون
                response = f"برای باز کردن مرحله بعدی ({stages[stage + 1] if stage + 1 < 12 else 'پایان'}), به این سوال جواب دهید: {quizzes[stage]['question']}"

    save_progress(user_id, progress)
    await update.message.reply_text(response)