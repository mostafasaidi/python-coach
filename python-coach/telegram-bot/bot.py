import os
import logging
from dotenv import load_dotenv
from telegram import Update, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# بارگذاری تنظیمات
load_dotenv()

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توکن ربات
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://آدرس_شما/mini-app")

if not BOT_TOKEN:
    logger.error("❌ توکن ربات پیدا نشد! لطفاً در فایل .env قرار دهید.")
    exit(1)

async def start_command(update: Update, context: CallbackContext):
    """دستور /start"""
    user = update.effective_user
    
    # ایجاد دکمه Mini App
    keyboard = [
        [InlineKeyboardButton(
            "🚀 باز کردن آموزش تعاملی",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = f"""
🎯 سلام {user.first_name}!

به **پایتون کوچ** خوش آمدی 🤖

آموزش تعاملی پایتون از مبتدی تا حرفه‌ای:
✅ ۱۶ فصل کامل
✅ پروژه‌های عملی
✅ محیط کدنویسی آنلاین
✅ پشتیبانی هوش مصنوعی

برای شروع، روی دکمه زیر کلیک کن:
"""
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: CallbackContext):
    """دستور /help"""
    help_text = """
🆘 راهنمای ربات:

🎮 **نحوه استفاده:**
1. روی دکمه «باز کردن آموزش تعاملی» کلیک کن
2. در Mini App، فصل مورد نظرت را انتخاب کن
3. درس‌ها را بخوان و تمرین کن
4. اگر نیاز به توضیح بیشتر داشتی، از دکمه «محتوای بیشتر» استفاده کن

📚 **۱۶ فصل آموزشی:**
1. شروع با پایتون
2. کنترل جریان
3. توابع و ماژول‌ها
4. کار با فایل
5. شیءگرایی
6. کتابخانه‌های استاندارد
7. NumPy
8. Pandas
9. مصورسازی داده
10. یادگیری ماشین مقدماتی
11. Scikit-learn
12. یادگیری عمیق مقدماتی
13. PyTorch
14. شبکه‌های عصبی
15. مدل‌های پیشرفته
16. استقرار مدل‌ها

🛠️ **دستورات:**
/start - شروع ربات
/help - این راهنما
/app - باز کردن Mini App

📞 **پشتیبانی:**
اگر مشکلی داری، به @mostafasaidi پیام بده.
"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def app_command(update: Update, context: CallbackContext):
    """دستور /app - باز کردن Mini App"""
    await start_command(update, context)

def main():
    """تابع اصلی اجرای ربات"""
    logger.info("🚀 در حال راه‌اندازی ربات آموزش پایتون...")
    
    # ایجاد اپلیکیشن
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ثبت دستورات
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("app", app_command))
    application.add_handler(CommandHandler("mini", app_command))
    
    # شروع ربات
    logger.info("✅ ربات آماده است!")
    logger.info("🤖 در حال گوش دادن به پیام‌ها...")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()