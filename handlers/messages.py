"""
هندلر پیام‌های متنی
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from modules.user_manager import user_manager
from modules.ai_system import ai_system
from modules.keyboards import main_keyboard, settings_keyboard, difficulty_keyboard, language_keyboard

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت پیام‌های متنی"""
    user_id = update.effective_user.id
    text = update.message.text
    
    user_manager.update_activity(user_id)
    
    # نقشه دستورات
    command_map = {
        "📘 شروع درس امروز": "start_lesson",
        "📊 وضعیت من": "my_status",
        "🔄 ریست پیشرفت": "reset_progress",
        "🔍 بررسی کد": "review_code",
        "💻 تمرین اضافی": "extra_exercise",
        "❓ سوال دارم": "ask_question",
        "⚙️ تنظیمات": "show_settings",
        "🔙 بازگشت": "back_to_main",
        "🎯 سطح دشواری": "change_difficulty",
        "🌐 زبان": "change_language",
        "🐢 آسان": "set_difficulty_easy",
        "🚶 متوسط": "set_difficulty_normal",
        "🏃 سخت": "set_difficulty_hard",
        "🚀 متخصص": "set_difficulty_expert",
        "🇮🇷 فارسی": "set_language_persian",
        "🇺🇸 انگلیسی": "set_language_english"
    }
    
    if text in command_map:
        await execute_command(update, context, command_map[text])
        return
    
    # اگر پیام معمولی است، به عنوان سوال پردازش شود
    if len(text) > 3:
        await handle_question(update, text)

async def execute_command(update, context, command):
    """اجرای دستور"""
    if command == "start_lesson":
        from handlers.lessons import start_lesson
        await start_lesson(update, context)
    
    elif command == "my_status":
        from handlers.commands import my_status
        await my_status(update, context)
    
    elif command == "reset_progress":
        from handlers.commands import reset_progress
        await reset_progress(update, context)
    
    elif command == "review_code":
        await update.message.reply_text(
            "کد خود را ارسال کنید تا بررسی کنم:",
            reply_markup=main_keyboard()
        )
    
    elif command == "extra_exercise":
        await update.message.reply_text(
            "این قابلیت به زودی اضافه می‌شود!",
            reply_markup=main_keyboard()
        )
    
    elif command == "ask_question":
        await update.message.reply_text(
            "سوال پایتون خود را بنویسید:",
            reply_markup=main_keyboard()
        )
    
    elif command == "show_settings":
        await update.message.reply_text(
            "⚙️ **تنظیمات**\n\nبرای تغییر هر گزینه کلیک کنید:",
            reply_markup=settings_keyboard()
        )
    
    elif command == "change_difficulty":
        await update.message.reply_text(
            "🎯 **سطح دشواری**\n\nسطح مورد نظر را انتخاب کنید:",
            reply_markup=difficulty_keyboard()
        )
    
    elif command == "change_language":
        await update.message.reply_text(
            "🌐 **زبان**\n\nزبان مورد نظر را انتخاب کنید:",
            reply_markup=language_keyboard()
        )
    
    elif command == "back_to_main":
        await update.message.reply_text(
            "بازگشت به منوی اصلی",
            reply_markup=main_keyboard()
        )
    
    elif command.startswith("set_difficulty_"):
        difficulty = command.replace("set_difficulty_", "")
        await set_difficulty(update, difficulty)
    
    elif command.startswith("set_language_"):
        language = command.replace("set_language_", "")
        await set_language(update, language)

async def set_difficulty(update, difficulty):
    """تنظیم سطح دشواری"""
    user_id = update.effective_user.id
    user = user_manager.load_user(user_id)
    
    difficulty_map = {
        "easy": "آسان",
        "normal": "متوسط",
        "hard": "سخت",
        "expert": "متخصص"
    }
    
    user["settings"]["difficulty"] = difficulty
    user_manager.save_user(user_id, user)
    
    await update.message.reply_text(
        f"✅ سطح دشواری به '{difficulty_map.get(difficulty, difficulty)}' تغییر کرد.",
        reply_markup=main_keyboard()
    )

async def set_language(update, language):
    """تنظیم زبان"""
    user_id = update.effective_user.id
    user = user_manager.load_user(user_id)
    
    language_map = {
        "persian": "فارسی",
        "english": "انگلیسی"
    }
    
    user["settings"]["language"] = language
    user_manager.save_user(user_id, user)
    
    await update.message.reply_text(
        f"✅ زبان به '{language_map.get(language, language)}' تغییر کرد.",
        reply_markup=main_keyboard()
    )

async def handle_question(update, question):
    """پردازش سوال"""
    await update.message.reply_text(
        "⏳ در حال پردازش سوال...",
        reply_markup=main_keyboard()
    )
    
    user_id = update.effective_user.id
    user = user_manager.load_user(user_id)
    
    # اضافه کردن زمینه
    context = f"کاربر در روز {user['current_day']} است. سطح: {user['settings']['difficulty']}"
    
    answer = ai_system.answer_question(question, context)
    
    if answer and not any(error in answer for error in ["❌", "⚠️", "⏱️", "🔌"]):
        # محدود کردن طول پاسخ
        if len(answer) > 3000:
            answer = answer[:3000] + "\n\n... (ادامه پاسخ)"
        
        await update.message.reply_text(
            f"🤖 **پاسخ:**\n\n{answer}",
            reply_markup=main_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "⚠️ در پردازش سوال مشکلی پیش آمد. لطفاً دوباره تلاش کنید.",
            reply_markup=main_keyboard()
        )