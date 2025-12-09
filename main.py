#!/usr/bin/env python3
"""
ربات آموزش پایتون - فایل اصلی اجرا
"""

import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# ایمپورت ماژول‌های داخلی
from handlers.commands import start, my_status, reset_progress
from handlers.lessons import start_lesson, handle_callback
from handlers.messages import handle_message
from utils.helpers import setup_directories

# تنظیم logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# بارگذاری متغیرهای محیطی
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def main():
    """تابع اصلی اجرای ربات"""
    
    if not TOKEN:
        logger.error("❌ TOKEN تنظیم نشده است!")
        print("لطفاً در فایل .env قرار دهید:")
        print("TELEGRAM_BOT_TOKEN=your_token_here")
        return
    
    # ایجاد دایرکتوری‌های لازم
    setup_directories()
    
    # ساخت اپلیکیشن
    app = Application.builder().token(TOKEN).build()
    
    # اضافه کردن هندلرهای دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset_progress))
    app.add_handler(CommandHandler("status", my_status))
    
    # هندلرهای درس‌ها
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    # هندلر پیام‌ها
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # نمایش اطلاعات راه‌اندازی
    print("🚀 **ربات Python Coach (۶۰ روزه) راه‌اندازی شد!**")
    print(f"🔑 DeepSeek API: {'✅ فعال' if DEEPSEEK_API_KEY else '❌ غیرفعال'}")
    print("=" * 50)
    print("✅ ربات آماده دریافت کاربران...")
    
    try:
        app.run_polling(allowed_updates="all", drop_pending_updates=True)
    except Exception as e:
        logger.error(f"خطا در اجرای ربات: {e}")

if __name__ == "__main__":
    main()