# -*- coding: utf-8 -*-
"""
ربات مربی پایتون - نسخه حرفه‌ای
نوشته شده توسط مهندس ارشد نرم‌افزار با ۲۰ سال تجربه
"""

import os
import json
import logging
import asyncio
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import httpx
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

# بارگذاری متغیرهای محیطی
from dotenv import load_dotenv
load_dotenv()

# بررسی وجود فایل .env و متغیرها
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not TELEGRAM_BOT_TOKEN or not DEEPSEEK_API_KEY:
    print("خطا: متغیرهای محیطی یافت نشدند!")
    print("TELEGRAM_BOT_TOKEN:", TELEGRAM_BOT_TOKEN)
    print("DEEPSEEK_API_KEY:", DEEPSEEK_API_KEY)
    exit(1)

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تنظیمات کلیدهای API
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# مسیر فایل دیتابیس
DB_PATH = "bot_database.db"

@dataclass
class LessonContent:
    """ساختار محتوای درس"""
    title: str
    sections: List[str]

class DatabaseManager:
    """مدیریت دیتابیس SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """ایجاد جداول دیتابیس"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # جدول کش دروس
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS lessons_cache (
                        chapter INTEGER,
                        lesson INTEGER,
                        content TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (chapter, lesson)
                    )
                ''')
                
                # جدول پیشرفت کاربران
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_progress (
                        user_id INTEGER PRIMARY KEY,
                        chapter INTEGER DEFAULT 0,
                        lesson INTEGER DEFAULT 0,
                        section_index INTEGER DEFAULT 0,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            logger.error(f"خطا در ایجاد دیتابیس: {e}")
    
    def get_lesson_content(self, chapter: int, lesson: int) -> Optional[str]:
        """دریافت محتوای کش شده درس"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT content FROM lessons_cache WHERE chapter=? AND lesson=?",
                    (chapter, lesson)
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"خطا در خواندن کش درس: {e}")
            return None
    
    def save_lesson_content(self, chapter: int, lesson: int, content: str):
        """ذخیره محتوای درس در کش"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO lessons_cache (chapter, lesson, content) VALUES (?, ?, ?)",
                    (chapter, lesson, content)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"خطا در ذخیره کش درس: {e}")
    
    def get_user_progress(self, user_id: int) -> Tuple[int, int, int]:
        """دریافت پیشرفت کاربر"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT chapter, lesson, section_index FROM user_progress WHERE user_id=?",
                    (user_id,)
                )
                result = cursor.fetchone()
                return result if result else (0, 0, 0)
        except Exception as e:
            logger.error(f"خطا در خواندن پیشرفت کاربر: {e}")
            return (0, 0, 0)
    
    def update_user_progress(self, user_id: int, chapter: int, lesson: int, section_index: int):
        """به‌روزرسانی پیشرفت کاربر"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_progress 
                    (user_id, chapter, lesson, section_index, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, chapter, lesson, section_index, datetime.now()))
                conn.commit()
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی پیشرفت کاربر: {e}")

class CurriculumManager:
    """مدیریت منوها و دروس آموزشی"""
    
    def __init__(self, curriculum_file: str):
        try:
            with open(curriculum_file, 'r', encoding='utf-8') as f:
                self.curriculum = json.load(f)
        except Exception as e:
            logger.error(f"خطا در خواندن فایل chapters.json: {e}")
            self.curriculum = {"chapters": []}
    
    def get_chapters_list(self) -> str:
        """دریافت لیست فصل‌ها"""
        if not self.curriculum.get("chapters"):
            return "❌ فایل فصل‌ها یافت نشد."
        
        result = "📚 فصل‌های آموزشی:\n\n"
        for i, chapter in enumerate(self.curriculum["chapters"], 1):
            result += f"{i}. {chapter['title']}\n"
        return result
    
    def get_chapters_buttons(self) -> List[List[InlineKeyboardButton]]:
        """دریافت دکمه‌های فصل‌ها"""
        if not self.curriculum.get("chapters"):
            return []
        
        buttons = []
        for i, chapter in enumerate(self.curriculum["chapters"], 1):
            button = InlineKeyboardButton(
                text=f"فصل {i}: {chapter['title']}", 
                callback_data=f"chapter_{i}"
            )
            buttons.append([button])
        return buttons
    
    def get_lessons_buttons(self, chapter_num: int) -> List[List[InlineKeyboardButton]]:
        """دریافت دکمه‌های دروس فصل"""
        chapter = self.get_chapter_info(chapter_num)
        if not chapter:
            return []
        
        buttons = []
        row = []
        for i, lesson in enumerate(chapter["lessons"], 1):
            button = InlineKeyboardButton(
                text=f"درس {i}", 
                callback_data=f"lesson_{chapter_num}_{i}"
            )
            row.append(button)
            if len(row) == 3:  # 3 دکمه در هر ردیف
                buttons.append(row)
                row = []
        
        if row:
            buttons.append(row)
        
        # دکمه بازگشت
        buttons.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="back_to_chapters")])
        return buttons
    
    def get_chapter_info(self, chapter_num: int) -> Optional[Dict]:
        """دریافت اطلاعات فصل"""
        if 1 <= chapter_num <= len(self.curriculum.get("chapters", [])):
            return self.curriculum["chapters"][chapter_num - 1]
        return None
    
    def get_lesson_title(self, chapter_num: int, lesson_num: int) -> Optional[str]:
        """دریافت عنوان درس"""
        chapter = self.get_chapter_info(chapter_num)
        if chapter and 1 <= lesson_num <= len(chapter.get("lessons", [])):
            return chapter["lessons"][lesson_num - 1]["title"]
        return None
    
    def validate_lesson_request(self, chapter_num: int, lesson_num: int) -> bool:
        """اعتبارسنجی درخواست درس"""
        chapter = self.get_chapter_info(chapter_num)
        if not chapter:
            return False
        return 1 <= lesson_num <= len(chapter.get("lessons", []))
    
    def get_adjacent_chapters(self, current_chapter: int) -> Tuple[Optional[int], Optional[int]]:
        """دریافت فصل قبلی و بعدی"""
        total_chapters = len(self.curriculum.get("chapters", []))
        prev_chapter = current_chapter - 1 if current_chapter > 1 else None
        next_chapter = current_chapter + 1 if current_chapter < total_chapters else None
        return prev_chapter, next_chapter
    
    def get_adjacent_lessons(self, chapter_num: int, lesson_num: int) -> Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
        """دریافت درس قبلی و بعدی"""
        chapter = self.get_chapter_info(chapter_num)
        if not chapter:
            return None, None
        
        total_lessons = len(chapter.get("lessons", []))
        
        # درس قبلی
        if lesson_num > 1:
            prev_lesson = (chapter_num, lesson_num - 1)
        elif chapter_num > 1:
            # درس آخر فصل قبلی
            prev_chapter = self.get_chapter_info(chapter_num - 1)
            if prev_chapter:
                prev_lesson = (chapter_num - 1, len(prev_chapter.get("lessons", [])))
            else:
                prev_lesson = None
        else:
            prev_lesson = None
        
        # درس بعدی
        if lesson_num < total_lessons:
            next_lesson = (chapter_num, lesson_num + 1)
        elif chapter_num < len(self.curriculum.get("chapters", [])):
            # درس اول فصل بعدی
            next_lesson = (chapter_num + 1, 1)
        else:
            next_lesson = None
        
        return prev_lesson, next_lesson

class DeepSeekClient:
    """کلاینت اتصال به API هوش مصنوعی DeepSeek"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0  # افزایش تایم‌اوت
        )
    
    async def generate_lesson(self, chapter_title: str, lesson_title: str) -> str:
        """تولید محتوای درس با استفاده از AI"""
        prompt = f"""
شما یک مربی بسیار سختگیر و با تجربه برای آموزش پایتون هستید. 
در زبان فارسی به صورت حرفه‌ای توضیح دهید:

فصل: {chapter_title}
درس: {lesson_title}

قوانین خروجی:
1. توضیح نظریه به‌صورت واضح و دقیق
2. مثال‌های دنیای واقعی
3. قطعه کد را با > شروع کن (فرمت تلگرام قابل کپی)
4. در پایان چند تمرین چالشی بده بدون ارائه راه حل
5. متن را به قسمت‌های کوتاه تقسیم کن تا قابل خواندن باشد
6. هرگز راه حل کامل تمرین‌ها را ارائه نده
7. به عنوان یک مربی بسیار سختگیر عمل کن و کاربر باید خودش فکر کند
8. تمام کدهای پایتون را داخل تگ <q> قرار بده تا در تلگرام قابل کپی باشند
9. مطمئن شو که تمام کدهای پایتون داخل تگ مناسب قرار گرفته‌اند
""".strip()
        
        try:
            logger.info(f"در حال ارسال درخواست به API برای: {chapter_title} - {lesson_title}")
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            
            logger.info(f"وضعیت پاسخ API: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()
                logger.info("تولید محتوای درس با موفقیت انجام شد")
                return content
            else:
                logger.error(f"خطا در API: {response.status_code} - {response.text}")
                return f"❌ خطای API: {response.status_code}. لطفاً بعداً تلاش کنید."
                
        except httpx.TimeoutException:
            logger.error("تایم‌اوت در اتصال به API")
            return "❌ زمان اتصال به API به پایان رسید. لطفاً بعداً تلاش کنید."
        except httpx.RequestError as e:
            logger.error(f"خطا در اتصال به API: {e}")
            return f"❌ خطای اتصال به API: {str(e)}. لطفاً بعداً تلاش کنید."
        except Exception as e:
            logger.error(f"خطای نامشخص در تولید درس: {e}")
            return f"❌ خطای نامشخص: {str(e)}. لطفاً بعداً تلاش کنید."

class MessageSplitter:
    """تقسیم پیام‌های طولانی به بخش‌های کوچک"""
    
    @staticmethod
    def split_message(text: str, max_length: int = 3500) -> List[str]:
        """تقسیم متن به بخش‌های کوچکتر"""
        lines = text.split('\n')
        chunks = []
        current_chunk = ""
        
        for line in lines:
            # اگر خط خیلی بلند باشد، تقسیمش می‌کنیم
            if len(line) > max_length:
                words = line.split(' ')
                line_chunk = ""
                for word in words:
                    if len(line_chunk + word) < max_length:
                        line_chunk += word + " "
                    else:
                        if line_chunk:
                            if len(current_chunk + line_chunk) < max_length:
                                current_chunk += line_chunk + "\n"
                            else:
                                chunks.append(current_chunk.strip())
                                current_chunk = line_chunk + "\n"
                        line_chunk = word + " "
                
                if line_chunk:
                    if len(current_chunk + line_chunk) < max_length:
                        current_chunk += line_chunk + "\n"
                    else:
                        chunks.append(current_chunk.strip())
                        current_chunk = line_chunk + "\n"
                continue
            
            # اضافه کردن خط به چانک فعلی یا ایجاد چانک جدید
            if len(current_chunk + line) < max_length:
                current_chunk += line + "\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line + "\n"
        
        # اضافه کردن آخرین چانک
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

class ContentProvider:
    """ارائه محتوای پیش‌فرض برای درس‌های خاص"""
    
    @staticmethod
    def get_default_content(chapter_num: int, lesson_num: int, chapter_title: str, lesson_title: str) -> str:
        """دریافت محتوای پیش‌فرض برای درس‌های خاص"""
        
        # محتوای پیش‌فرض برای درس 1-1 (مقدمه و مفاهیم پایه)
        if chapter_num == 1 and lesson_num == 1:
            return f"""📘 فصل {chapter_num}: {chapter_title}
📝 درس {lesson_num}: {lesson_title}

🔍 مقدمه
پایتون یک زبان برنامه‌نویسی سطح بالا و همه منظوره است که در سال 1991 توسط Guido van Rossum طراحی شده است. این زبان به دلیل سادگی و خوانایی بالا بسیار محبوب شده است.

✨ ویژگی‌های پایتون:
• سادگی و خوانایی کد
• پشتیبانی از برنامه‌نویسی شیءگرا
• پشتیبانی از برنامه‌نویسی تابعی
• کتابخانه‌های گسترده
• اکوسیستم قوی

<q>print("Hello, World!")</q>

🎯 موارد استفاده:
• توسعه وب (Django, Flask)
• علم داده و تحلیل (pandas, numpy)
• یادگیری ماشین (scikit-learn, TensorFlow)
• اتوماسیون و اسکریپت‌نویسی
• توسعه بازی و GUI

📝 تمرینات:
1. نصب پایتون در سیستم خود
2. اجرای اولین برنامه "Hello World"
3. بررسی نسخه پایتون نصب شده
"""
        
        # محتوای پیش‌فرض برای درس 1-2 (نصب و راه‌اندازی محیط توسعه)
        elif chapter_num == 1 and lesson_num == 2:
            return f"""📘 فصل {chapter_num}: {chapter_title}
📝 درس {lesson_num}: {lesson_title}

🔧 نصب مفسر پایتون
برای شروع کار با پایتون، ابتدا باید مفسر آن را نصب کنید:

📥 روش‌های نصب:
1. از وب‌سایت رسمی: https://python.org
2. در ویندوز: winget install python
3. در مک: brew install python
4. در لینوکس: sudo apt install python3

<q># بررسی نصب موفق
python --version
# یا در لینوکس و مک
python3 --version</q>

💻 نصب ویرایشگر کد:
• Visual Studio Code (پیشنهادی)
• PyCharm
• Sublime Text
• Atom

⚙️ پیکربندی محیط:
1. اضافه کردن پایتون به PATH
2. نصب افزونه‌های مرتبط
3. تست اجرای ساده

<q># اجرای مفسر به صورت تعاملی
python
>>> print("Interactive Python!")
>>> exit()</q>

📝 تمرینات:
1. نصب پایتون و ویرایشگر
2. اجرای اولین دستور در محیط تعاملی
3. ایجاد و اجرای فایل .py اولیه
"""
        
        # محتوای پیش‌فرض برای درس 1-3 (اولین برنامه «سلام دنیا»)
        elif chapter_num == 1 and lesson_num == 3:
            return f"""📘 فصل {chapter_num}: {chapter_title}
📝 درس {lesson_num}: {lesson_title}

👋 سلام دنیا - اولین قدم در دنیای برنامه‌نویسی

همه برنامه‌نویسان با نوشتن «سلام دنیا» شروع می‌کنند. این یک سنت قدیمی است که به اولین برنامه شما در هر زبان اطلاق می‌شود.

<q># ساده‌ترین برنامه «سلام دنیا»
print("سلام دنیا!")</q>

✨ توضیح کد:
• `print()`: تابعی که متن را در خروجی نمایش می‌دهد
• `"سلام دنیا!"`: یک رشته که داخل کوتیشن قرار گرفته است

🔍 مفاهیم پیشرفته‌تر:
۱. **ترکیب متن و متغیرها**:
<q>name = "علی"
age = 25
print(f"سلام {name}، شما {age} سال دارید")</q>

۲. **چاپ چند خطی**:
<q>print("خط اول")
print("خط دوم")</q>

📝 تمرینات:
۱. برنامه‌ای بنویسید که نام، نام خانوادگی و سن خود را چاپ کند
۲. برنامه‌ای بنویسید که یک نقل قول مورد علاقه شما را نمایش دهد
۳. برنامه‌ای بنویسید که چند خط اطلاعات درباره خودتان را چاپ کند
"""
        
        # محتوای پیش‌فرض برای درس 1-4 (ساختار داده‌ها)
        elif chapter_num == 1 and lesson_num == 4:
            return f"""📘 فصل {chapter_num}: {chapter_title}
📝 درس {lesson_num}: {lesson_title}

🔍 ساختار داده‌ها در پایتون

داده‌ها قلب هر برنامه هستند. باید بدانید چگونه آنها را ذخیره، پردازش و استفاده کنید.

🔢 اعداد (Integers & Floats):
اعداد صحیح (int): ۱, -۵, ۱۰۰
اعداد اعشاری (float): ۳.۱۴, -۰.۵, ۲.۰

<q># مثال‌های اعداد
age = 25  # int
pi = 3.14159  # float
temperature = -10.5  # float

# عملیات ریاضی
result = age + pi
print(result)</q>

🔤 رشته‌ها (Strings):
رشته‌ها دنباله‌ای از کاراکترها هستند و با ' یا " تعریف می‌شوند.

<q># مثال‌های رشته
name = "علی"
message = 'سلام دنیا!'
multiline = '''این یک
متن چندخطی
است'''

# کار با رشته‌ها
full_name = name + " رضایی"
print("نام کامل:", full_name)</q>

🔄 تبدیل انواع داده:
گاهی باید انواع داده را به هم تبدیل کنید.

<q># تبدیل رشته به عدد
age_str = "25"
age_int = int(age_str)

# تبدیل عدد به رشته
number = 123
number_str = str(number)

# تبدیل عدد صحیح به اعشاری
int_num = 42
float_num = float(int_num)</q>

📝 تمرینات:
۱. برنامه‌ای بنویسید که میانگین ۳ عدد را حساب کند
۲. برنامه‌ای بنویسید که یک رشته را از کاربر بگیرد و طول آن را چاپ کند
۳. برنامه‌ای بنویسید که یک عدد را از کاربر بگیرد و نوع آن را تغییر دهد
"""
        
        # برای سایر درس‌ها محتوای پیش‌فرض ساده
        else:
            return f"""📘 فصل {chapter_num}: {chapter_title}
📝 درس {lesson_num}: {lesson_title}

در حال حاضر محتوای این درس در دسترس نیست. لطفاً بعداً دوباره تلاش کنید.

می‌توانید به درس‌های قبلی بازگردید یا درس‌های دیگر را امتحان کنید.
"""

class PythonMentorBot:
    """کلاس اصلی ربات مربی پایتون"""
    
    def __init__(self):
        self.db_manager = DatabaseManager(DB_PATH)
        self.curriculum_manager = CurriculumManager("chapters.json")
        self.ai_client = DeepSeekClient(DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL)
        self.message_splitter = MessageSplitter()
        self.content_provider = ContentProvider()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت دستور /start"""
        welcome_text = """🎓 به ربات مربی پایتون خوش آمدید!

من یک مربی سختگیرم که به شما کمک می‌کنم به صورت گام به گام پایتون یاد بگیرید."""

        # کیبورد اصلی
        keyboard = [
            [KeyboardButton("فصل‌ها 📚")],
            [KeyboardButton("پیشرفت من 📊")],
            [KeyboardButton("راهنما ℹ️")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def show_chapters_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی فصل‌ها"""
        chapters_text = self.curriculum_manager.get_chapters_list()
        chapters_buttons = self.curriculum_manager.get_chapters_buttons()
        
        if not chapters_buttons:
            await update.message.reply_text("❌ فایل فصل‌ها یافت نشد. لطفاً فایل chapters.json را بررسی کنید.")
            return
            
        reply_markup = InlineKeyboardMarkup(chapters_buttons)
        await update.message.reply_text(chapters_text, reply_markup=reply_markup)
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت دکمه‌های کیبورد و دکمه‌های شیشه‌ای"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("chapter_"):
            chapter_num = int(data.split("_")[1])
            await self.show_chapter_lessons(query, context, chapter_num)
        
        elif data.startswith("lesson_"):
            parts = data.split("_")
            chapter_num = int(parts[1])
            lesson_num = int(parts[2])
            
            # اجرای درس
            await self.start_lesson_by_numbers(query, context, chapter_num, lesson_num)
        
        elif data == "back_to_chapters":
            await self.back_to_chapters_menu(query, context)
        
        elif data == "next_section":
            await self.next_section_callback(query, context)
        
        elif data == "prev_section":
            await self.prev_section_callback(query, context)
        
        elif data == "show_exercises":
            await self.show_exercises_callback(query, context)
        
        elif data.startswith("nav_lesson_"):
            # ناوبری بین درس‌ها
            parts = data.split("_")
            chapter_num = int(parts[2])
            lesson_num = int(parts[3])
            await self.start_lesson_by_numbers(query, context, chapter_num, lesson_num)
    
    async def show_chapter_lessons(self, query, context, chapter_num):
        """نمایش درس‌های یک فصل"""
        chapter_info = self.curriculum_manager.get_chapter_info(chapter_num)
        
        if chapter_info:
            lessons_text = f"فصل {chapter_num}: {chapter_info['title']}\n\n"
            lessons_text += "درس‌های این فصل:\n"
            for i, lesson in enumerate(chapter_info["lessons"], 1):
                lessons_text += f"{i}. {lesson['title']}\n"
            
            lessons_buttons = self.curriculum_manager.get_lessons_buttons(chapter_num)
            if lessons_buttons:
                reply_markup = InlineKeyboardMarkup(lessons_buttons)
                await query.edit_message_text(lessons_text, reply_markup=reply_markup)
            else:
                await query.edit_message_text("❌ خطایی در بارگذاری دروس رخ داده است.")
    
    async def back_to_chapters_menu(self, query, context):
        """بازگشت به منوی فصل‌ها"""
        chapters_text = self.curriculum_manager.get_chapters_list()
        chapters_buttons = self.curriculum_manager.get_chapters_buttons()
        if chapters_buttons:
            reply_markup = InlineKeyboardMarkup(chapters_buttons)
            await query.edit_message_text(chapters_text, reply_markup=reply_markup)
        else:
            await query.edit_message_text("❌ خطایی در بارگذاری فصل‌ها رخ داده است.")
    
    async def start_lesson_by_numbers(self, query, context, chapter_num, lesson_num):
        """شروع درس با شماره فصل و درس"""
        user_id = query.from_user.id
        
        # اعتبارسنجی درخواست
        if not self.curriculum_manager.validate_lesson_request(chapter_num, lesson_num):
            await query.message.reply_text("❌ فصل یا درس مورد نظر وجود ندارد.")
            return
        
        chapter_info = self.curriculum_manager.get_chapter_info(chapter_num)
        lesson_title = self.curriculum_manager.get_lesson_title(chapter_num, lesson_num)
        
        if not chapter_info or not lesson_title:
            await query.message.reply_text("❌ اطلاعات فصل یا درس یافت نشد.")
            return
        
        # چک کردن کش درس
        cached_content = self.db_manager.get_lesson_content(chapter_num, lesson_num)
        
        if cached_content:
            # استفاده از محتوای کش شده
            lesson_content = cached_content
            logger.info(f"استفاده از کش برای درس {chapter_num}-{lesson_num}")
        else:
            # تولید محتوای جدید از طریق AI
            await query.message.reply_text("🔄 در حال تولید محتوای درس...")
            
            # برای درس‌های اولیه از محتوای پیش‌فرض استفاده می‌کنیم
            if chapter_num == 1 and lesson_num in [1, 2, 3, 4]:
                lesson_content = self.content_provider.get_default_content(
                    chapter_num, lesson_num, chapter_info["title"], lesson_title
                )
                logger.info(f"استفاده از محتوای پیش‌فرض برای درس {chapter_num}-{lesson_num}")
            else:
                # برای سایر درس‌ها سعی می‌کنیم از AI استفاده کنیم
                lesson_content = await self.ai_client.generate_lesson(
                    chapter_info["title"],
                    lesson_title
                )
                
                # اگر AI موفق نبود، از محتوای پیش‌فرض استفاده می‌کنیم
                if "❌" in lesson_content:
                    lesson_content = self.content_provider.get_default_content(
                        chapter_num, lesson_num, chapter_info["title"], lesson_title
                    )
                    logger.info(f"استفاده از محتوای پیش‌فرض به دلیل خطا در AI برای درس {chapter_num}-{lesson_num}")
            
            # ذخیره در کش
            self.db_manager.save_lesson_content(chapter_num, lesson_num, lesson_content)
            logger.info(f"ذخیره کش برای درس {chapter_num}-{lesson_num}")
        
        # تبدیل محتوای درس به بخش‌های کوچک
        sections = self.message_splitter.split_message(lesson_content)
        if not sections:
            await query.message.reply_text("❌ خطا در پردازش محتوای درس.")
            return
            
        lesson_obj = LessonContent(title=lesson_title, sections=sections)
        
        # ذخیره پیشرفت کاربر
        self.db_manager.update_user_progress(user_id, chapter_num, lesson_num, 0)
        
        # ارسال بخش اول درس
        first_section = lesson_obj.sections[0]
        header = f"📝 پیام ۱ از {len(lesson_obj.sections)} – فصل {chapter_num} درس {lesson_num} – {lesson_obj.title}\n\n"
        
        # دکمه‌های کنترل با توجه به تعداد بخش‌ها
        control_buttons = []
        
        # دکمه بعدی (فقط اگر بخش بعدی وجود داشته باشد)
        if len(lesson_obj.sections) > 1:
            control_buttons.append([
                InlineKeyboardButton("➡️ بعدی", callback_data="next_section")
            ])
        # دکمه تمرینات
        control_buttons.append([
            InlineKeyboardButton("🎯 تمرینات", callback_data="show_exercises")
        ])
        reply_markup = InlineKeyboardMarkup(control_buttons)
        
        await query.message.reply_text(header + first_section, reply_markup=reply_markup)
    
    async def next_section_callback(self, query, context):
        """بخش بعدی درس"""
        user_id = query.from_user.id
        
        # دریافت پیشرفت فعلی کاربر
        chapter, lesson, section_index = self.db_manager.get_user_progress(user_id)
        
        # چک کردن وجود درس فعال
        if chapter == 0 or lesson == 0:
            await query.answer("ابتدا یک درس را شروع کنید!", show_alert=True)
            return
        
        # دریافت محتوای درس از کش
        cached_content = self.db_manager.get_lesson_content(chapter, lesson)
        if not cached_content:
            await query.message.reply_text("❌ محتوای درس یافت نشد.")
            return
        
        # تقسیم محتوا به بخش‌ها
        sections = self.message_splitter.split_message(cached_content)
        lesson_title = self.curriculum_manager.get_lesson_title(chapter, lesson)
        if not lesson_title:
            await query.message.reply_text("❌ عنوان درس یافت نشد.")
            return
            
        lesson_obj = LessonContent(title=lesson_title, sections=sections)
        
        # چک کردن پایان درس
        if section_index >= len(lesson_obj.sections) - 1:
            # پایان درس - نمایش پیام و فقط دکمه تمرینات
            await query.answer("درس به پایان رسید! تمرینات را ببینید.", show_alert=True)
            return
        
        # به‌روزرسانی پیشرفت کاربر و ارسال بخش بعدی
        new_section_index = section_index + 1
        self.db_manager.update_user_progress(user_id, chapter, lesson, new_section_index)
        
        next_section = lesson_obj.sections[new_section_index]
        header = f"📝 پیام {new_section_index + 1} از {len(lesson_obj.sections)} – فصل {chapter} درس {lesson} – {lesson_obj.title}\n\n"
        
        # دکمه‌های ناوبری درس
        control_buttons = []
        
        # دکمه قبلی
        control_buttons.append([
            InlineKeyboardButton("⬅️ قبلی", callback_data="prev_section")
        ])
        
        # دکمه بعدی (فقط اگر بخش بعدی وجود داشته باشد)
        if new_section_index < len(lesson_obj.sections) - 1:
            control_buttons.append([
                InlineKeyboardButton("➡️ بعدی", callback_data="next_section")
            ])
        
        # دکمه تمرینات
        control_buttons.append([
            InlineKeyboardButton("🎯 تمرینات", callback_data="show_exercises")
        ])
        
        # دکمه‌های ناوبری درس (قبلی/بعدی درس)
        prev_lesson, next_lesson = self.curriculum_manager.get_adjacent_lessons(chapter, lesson)
        nav_lesson_buttons = []
        if prev_lesson:
            nav_lesson_buttons.append(InlineKeyboardButton("⏮ درس قبلی", callback_data=f"nav_lesson_{prev_lesson[0]}_{prev_lesson[1]}"))
        if next_lesson:
            nav_lesson_buttons.append(InlineKeyboardButton("درس بعدی ⏭", callback_data=f"nav_lesson_{next_lesson[0]}_{next_lesson[1]}"))
        
        if nav_lesson_buttons:
            control_buttons.append(nav_lesson_buttons)
        
        reply_markup = InlineKeyboardMarkup(control_buttons)
        
        await query.message.reply_text(header + next_section, reply_markup=reply_markup)
    
    async def prev_section_callback(self, query, context):
        """بخش قبلی درس"""
        user_id = query.from_user.id
        
        # دریافت پیشرفت فعلی کاربر
        chapter, lesson, section_index = self.db_manager.get_user_progress(user_id)
        
        # چک کردن وجود درس فعال
        if chapter == 0 or lesson == 0:
            await query.answer("ابتدا یک درس را شروع کنید!", show_alert=True)
            return
        
        # دریافت محتوای درس از کش
        cached_content = self.db_manager.get_lesson_content(chapter, lesson)
        if not cached_content:
            await query.message.reply_text("❌ محتوای درس یافت نشد.")
            return
        
        # تقسیم محتوا به بخش‌ها
        sections = self.message_splitter.split_message(cached_content)
        lesson_title = self.curriculum_manager.get_lesson_title(chapter, lesson)
        if not lesson_title:
            await query.message.reply_text("❌ عنوان درس یافت نشد.")
            return
            
        lesson_obj = LessonContent(title=lesson_title, sections=sections)
        
        # چک کردن ابتدای درس
        if section_index <= 0:
            await query.answer("شما در ابتدای درس هستید!", show_alert=True)
            return
        
        # به‌روزرسانی پیشرفت کاربر و ارسال بخش قبلی
        new_section_index = section_index - 1
        self.db_manager.update_user_progress(user_id, chapter, lesson, new_section_index)
        
        prev_section = lesson_obj.sections[new_section_index]
        header = f"📝 پیام {new_section_index + 1} از {len(lesson_obj.sections)} – فصل {chapter} درس {lesson} – {lesson_obj.title}\n\n"
        
        # دکمه‌های ناوبری درس
        control_buttons = []
        
        # دکمه قبلی (فقط اگر بخش قبلی وجود داشته باشد)
        if new_section_index > 0:
            control_buttons.append([
                InlineKeyboardButton("⬅️ قبلی", callback_data="prev_section")
            ])
        
        # دکمه بعدی
        control_buttons.append([
            InlineKeyboardButton("➡️ بعدی", callback_data="next_section")
        ])
        
        # دکمه تمرینات
        control_buttons.append([
            InlineKeyboardButton("🎯 تمرینات", callback_data="show_exercises")
        ])
        
        # دکمه‌های ناوبری درس (قبلی/بعدی درس)
        prev_lesson, next_lesson = self.curriculum_manager.get_adjacent_lessons(chapter, lesson)
        nav_lesson_buttons = []
        if prev_lesson:
            nav_lesson_buttons.append(InlineKeyboardButton("⏮ درس قبلی", callback_data=f"nav_lesson_{prev_lesson[0]}_{prev_lesson[1]}"))
        if next_lesson:
            nav_lesson_buttons.append(InlineKeyboardButton("درس بعدی ⏭", callback_data=f"nav_lesson_{next_lesson[0]}_{next_lesson[1]}"))
        
        if nav_lesson_buttons:
            control_buttons.append(nav_lesson_buttons)
        
        reply_markup = InlineKeyboardMarkup(control_buttons)
        
        await query.message.reply_text(header + prev_section, reply_markup=reply_markup)
    
    async def show_exercises_callback(self, query, context):
        """نمایش تمرینات"""
        user_id = query.from_user.id
        
        # دریافت پیشرفت فعلی کاربر
        chapter, lesson, section_index = self.db_manager.get_user_progress(user_id)
        
        # چک کردن وجود درس فعال
        if chapter == 0 or lesson == 0:
            await query.answer("ابتدا یک درس را شروع کنید!", show_alert=True)
            return
        
        # دریافت محتوای درس از کش
        cached_content = self.db_manager.get_lesson_content(chapter, lesson)
        if not cached_content:
            await query.message.reply_text("❌ محتوای درس یافت نشد.")
            return
        
        # پیدا کردن بخش تمرینات (آخرین بخش)
        sections = self.message_splitter.split_message(cached_content)
        if sections:
            exercise_section = sections[-1]
            if "تمرین" in exercise_section or "exercise" in exercise_section.lower():
                header = f"🎯 تمرینات – فصل {chapter} درس {lesson} – {self.curriculum_manager.get_lesson_title(chapter, lesson)}\n\n"
                await query.message.reply_text(header + exercise_section)
            else:
                await query.message.reply_text("❌ تمرینی برای این درس تعریف نشده است.")
        else:
            await query.message.reply_text("❌ خطایی در خواندن تمرینات رخ داده است.")
    
    async def progress_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش پیشرفت کاربر"""
        user_id = update.effective_user.id
        
        # دریافت پیشرفت کاربر
        chapter, lesson, section_index = self.db_manager.get_user_progress(user_id)
        
        if chapter == 0 or lesson == 0:
            progress_text = "📊 شما هنوز هیچ درسی را شروع نکرده‌اید.\nابتدا یک درس را شروع کنید."
        else:
            lesson_title = self.curriculum_manager.get_lesson_title(chapter, lesson)
            if not lesson_title:
                lesson_title = "عنوان نامشخص"
                
            progress_text = f"""📊 وضعیت پیشرفت شما:

فصل فعلی: {chapter}
درس فعلی: {lesson}
عنوان درس: {lesson_title}
بخش خوانده‌شده: {section_index + 1}

✅ برای ادامه به درس بعدی، ابتدا تمام بخش‌های این درس و تمرینات آن را تکمیل کنید."""
        
        await update.message.reply_text(progress_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش راهنما"""
        help_text = """ℹ️ راهنمای استفاده از ربات:

🔹 دکمه "فصل‌ها 📚": نمایش لیست فصل‌های آموزشی
🔹 دکمه "پیشرفت من 📊": مشاهده وضعیت پیشرفت شما
🔹 دکمه "راهنما ℹ️": نمایش این راهنما

در هر فصل:
- دکمه‌های شیشه‌ای برای انتخاب درس
- در هر درس دکمه‌های "قبلی"، "بعدی" و "تمرینات"

⚠️ قواند مهم:
- فقط می‌توانید به ترتیب حرکت کنید
- نمی‌توانید مستقیماً راه‌حل تمرین‌ها را بگیرید
- به تفکر خودتان اعتماد کنید
- باید به تمام تمرین‌ها پاسخ دهید قبل از رفتن به درس بعدی"""
        
        await update.message.reply_text(help_text)
    
    async def text_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت پیام‌های متنی"""
        text = update.message.text
        
        if text == "فصل‌ها 📚":
            await self.show_chapters_menu(update, context)
        elif text == "پیشرفت من 📊":
            await self.progress_command(update, context)
        elif text == "راهنما ℹ️":
            await self.help_command(update, context)
        elif text == "/start":
            await self.start_command(update, context)
        else:
            await update.message.reply_text("❓ دستور نامعتبر. از منوی اصلی استفاده کنید.")
    
    def run(self):
        """اجرای ربات"""
        try:
            app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
            
            # ثبت دستورات
            app.add_handler(CommandHandler("start", self.start_command))
            
            # ثبت هندلرهای دکمه‌ای
            app.add_handler(CallbackQueryHandler(self.button_handler))
            
            # ثبت هندلر پیام‌های متنی
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_message_handler))
            
            logger.info("ربات در حال اجرا است...")
            app.run_polling()
        except Exception as e:
            logger.error(f"خطا در اجرای ربات: {e}")
            print(f"خطا در اجرای ربات: {e}")

if __name__ == "__main__":
    # ایجاد شیء ربات و اجرای آن
    bot = PythonMentorBot()
    bot.run()