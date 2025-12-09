"""
کیبوردهای ربات
"""

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def main_keyboard():
    """کیبورد اصلی"""
    buttons = [
        ["📘 شروع درس امروز"],
        ["💻 تمرین اضافی", "🔍 بررسی کد"],
        ["⚙️ تنظیمات", "❓ سوال دارم"],
        ["🔄 ریست پیشرفت", "📊 وضعیت من"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def lesson_options_keyboard(day):
    """کیبورد گزینه‌های درس"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔐 دریافت پاسخ‌نامه", callback_data=f"get_answers_{day}"),
            InlineKeyboardButton("💻 بررسی کد من", callback_data=f"review_code_{day}")
        ],
        [
            InlineKeyboardButton("✅ تمرین را کامل کردم", callback_data=f"complete_{day}"),
            InlineKeyboardButton("💡 راهنمایی بیشتر", callback_data=f"help_{day}")
        ]
    ])

def settings_keyboard():
    """کیبورد تنظیمات"""
    return ReplyKeyboardMarkup([
        ["🎯 سطح دشواری", "🌐 زبان"],
        ["🔙 بازگشت"]
    ], resize_keyboard=True)

def difficulty_keyboard():
    """کیبورد سطح دشواری"""
    return ReplyKeyboardMarkup([
        ["🐢 آسان", "🚶 متوسط"],
        ["🏃 سخت", "🚀 متخصص"],
        ["🔙 بازگشت"]
    ], resize_keyboard=True)

def language_keyboard():
    """کیبورد زبان"""
    return ReplyKeyboardMarkup([
        ["🇮🇷 فارسی", "🇺🇸 انگلیسی"],
        ["🔙 بازگشت"]
    ], resize_keyboard=True)