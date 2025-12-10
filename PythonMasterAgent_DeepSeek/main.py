import os
import json
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
PROGRESS_FILE = "progress.json"

if not os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump({"day": 0}, f)

def get_day():
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["day"]

def save_day(day):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump({"day": day}, f)

def call_deepseek(prompt):
    try:
        r = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            json={"model": "deepseek-coder", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7},
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            timeout=60
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"خطا در DeepSeek: {str(e)}"

def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("درس امروز", callback_data="today"),
         InlineKeyboardButton("درس بعدی", callback_data="next")],
        [InlineKeyboardButton("تمرین تموم شد", callback_data="done")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام قهرمان! آماده‌ای بریم؟", reply_markup=get_keyboard())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    day = get_day()

    if query.data == "today":
        lesson = call_deepseek(f"روز {day} از ۷۰ — درس کوتاه فارسی پایتون با کد داخل ```python و توضیحات کامل")
        await query.edit_message_text(
            text=f"روز {day} از ۷۰\n\n{lesson}",
            reply_markup=get_keyboard()
        )

    elif query.data == "next":
        day += 1
        lesson = call_deepseek(f"روز {day} از ۷۰ — درس کوتاه فارسی پایتون با کد داخل ```python و توضیحات کامل")
        await query.edit_message_text(
            text=f"روز {day} از ۷۰\n\n{lesson}",
            reply_markup=get_keyboard()
        )
        save_day(day)

    elif query.data == "done":
        await query.edit_message_text(
            text="عالیییی! ۳۰ امتیاز گرفتی! 💪",
            reply_markup=get_keyboard()
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("ربات نهایی — دکمه‌ها ۱۰۰٪ کار می‌کنن!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()