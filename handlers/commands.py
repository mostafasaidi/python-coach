"""
هندلرهای دستورات (commands)
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from modules.user_manager import user_manager
from modules.keyboards import main_keyboard

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start"""
    user_id = update.effective_user.id
    username = update.effective_user.first_name or f"کاربر_{user_id}"
    
    user = user_manager.update_activity(user_id, username)
    
    progress_percent = (len(user["completed_lessons"]) / 60) * 100
    
    welcome = f"""
👋 **سلام {username}!**

🤖 **به مربی پایتون (۶۰ روزه) خوش آمدید!**

📚 **پیشرفت شما:**
• 📅 روز فعلی: {user['current_day']}/60
• ✅ درس‌های کامل: {len(user['completed_lessons'])} ({progress_percent:.1f}%)

🎯 **ویژگی‌ها:**
• 📄 PDF خودکار هر درس
• 🔐 پاسخ‌نامه جداگانه
• 💾 کدهای قابل کپی
• ⏰ سیستم زمان‌بندی

برای شروع روی '📘 شروع درس امروز' کلیک کنید!
    """
    
    await update.message.reply_text(welcome, reply_markup=main_keyboard(), parse_mode="Markdown")

async def my_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /status"""
    user_id = update.effective_user.id
    user = user_manager.update_activity(user_id)
    
    progress_percent = (len(user["completed_lessons"]) / 60) * 100
    
    status = f"""
📊 **وضعیت یادگیری**

👤 کاربر: {user.get('username', 'کاربر')}
📅 روز فعلی: {user['current_day']}/60
✅ درس‌های کامل: {len(user['completed_lessons'])} ({progress_percent:.1f}%)

📈 پیشرفت:
{'▓' * int(progress_percent / 3)}{'░' * (20 - int(progress_percent / 3))} {progress_percent:.1f}%
    """
    
    await update.message.reply_text(status, reply_markup=main_keyboard(), parse_mode="Markdown")

async def reset_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /reset"""
    user_id = update.effective_user.id
    user_manager.reset_user(user_id)
    
    await update.message.reply_text(
        "🔄 **همه چیز ریست شد!**\n\n"
        "دوباره از روز اول شروع کن.",
        reply_markup=main_keyboard()
    )