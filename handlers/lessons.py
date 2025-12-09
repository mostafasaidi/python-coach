"""
هندلرهای مربوط به درس‌ها
"""

import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from modules.user_manager import user_manager
from modules.ai_system import ai_system
from modules.pdf_generator import lesson_pdf_generator, answers_pdf_generator
from modules.keyboards import main_keyboard, lesson_options_keyboard
from utils.constants import PYTHON_TOPICS, MESSAGES

logger = logging.getLogger(__name__)

async def start_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع درس امروز"""
    user_id = update.effective_user.id
    user = user_manager.update_activity(user_id)
    
    current_day = user["current_day"]
    
    if current_day > 60:
        await update.message.reply_text(
            "🎉 **تبریک! دوره ۶۰ روزه را کامل کردید!**\n\n"
            "برای ادامه می‌توانید پروژه‌های پیشرفته شروع کنید.",
            reply_markup=main_keyboard()
        )
        return
    
    await update.message.reply_text(
        MESSAGES["lesson_generating"],
        reply_markup=main_keyboard()
    )
    
    try:
        # دریافت موضوع
        topic = PYTHON_TOPICS.get(current_day, f"مباحث روز {current_day}")
        
        # تولید محتوا
        lesson_data = ai_system.generate_lesson(
            day=current_day,
            topic=topic,
            difficulty=user["settings"]["difficulty"],
            language=user["settings"]["language"]
        )
        
        # ذخیره داده‌ها
        user_manager.save_lesson_data(user_id, current_day, lesson_data)
        
        # شروع تایمر
        user_manager.start_exercise_timer(user_id, current_day)
        
        # تولید PDF درس
        pdf_path = f"data/pdfs/lessons/lesson_{current_day}_user_{user_id}.pdf"
        lesson_pdf_generator.create_lesson_pdf(lesson_data, pdf_path)
        
        # ارسال PDF
        with open(pdf_path, 'rb') as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                caption=f"📘 درس روز {current_day}: {topic}\n\n"
                       f"⏱️ حداقل ۱۵ دقیقه روی تمرینات فکر کنید.",
                filename=f"python_lesson_{current_day}.pdf",
                reply_markup=lesson_options_keyboard(current_day)
            )
        
        # پیام انگیزشی
        await update.message.reply_text(
            f"🎯 **تمرینات را با دقت حل کنید!**\n\n"
            f"پاسخ‌نامه پس از ۱۵ دقیقه فعال می‌شود.",
            reply_markup=main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"خطا در تولید درس: {e}")
        await update.message.reply_text(
            f"⚠️ خطا در تولید درس: {str(e)[:100]}",
            reply_markup=main_keyboard()
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    logger.info(f"Callback: {data} from {user_id}")
    
    if data.startswith("get_answers_"):
        # دریافت پاسخ‌نامه
        day = int(data.split("_")[-1])
        
        can_get, message = user_manager.can_get_answers(user_id, day)
        
        if not can_get:
            await query.edit_message_text(
                MESSAGES["need_more_time"].format(message=message),
                reply_markup=main_keyboard()
            )
            return
        
        await query.edit_message_text(
            "⏳ در حال تولید پاسخ‌نامه...",
            reply_markup=main_keyboard()
        )
        
        try:
            # دریافت داده‌های درس
            lesson_data = user_manager.get_lesson_data(user_id, day)
            
            if not lesson_data:
                user = user_manager.load_user(user_id)
                topic = PYTHON_TOPICS.get(day, f"مباحث روز {day}")
                lesson_data = ai_system.generate_lesson(
                    day=day,
                    topic=topic,
                    difficulty=user["settings"]["difficulty"],
                    language=user["settings"]["language"]
                )
            
            # تولید PDF پاسخ‌نامه
            pdf_path = f"data/pdfs/answers/answers_{day}_user_{user_id}.pdf"
            answers_pdf_generator.create_answers_pdf(lesson_data, pdf_path)
            
            # ارسال پاسخ‌نامه
            with open(pdf_path, 'rb') as pdf_file:
                await query.message.reply_document(
                    document=pdf_file,
                    caption=f"🔐 پاسخ‌نامه درس روز {day}",
                    filename=f"python_answers_{day}.pdf"
                )
            
            await query.message.reply_text(
                "✅ پاسخ‌نامه ارسال شد!\n\nآیا تمرین را کامل کردید؟",
                reply_markup=lesson_options_keyboard(day)
            )
            
        except Exception as e:
            logger.error(f"خطا در تولید پاسخ‌نامه: {e}")
            await query.message.reply_text(
                f"⚠️ خطا در تولید پاسخ‌نامه",
                reply_markup=main_keyboard()
            )
    
    elif data.startswith("complete_"):
        # تکمیل درس
        day = int(data.split("_")[-1])
        
        if user_manager.complete_lesson(user_id, day):
            user = user_manager.load_user(user_id)
            await query.edit_message_text(
                MESSAGES["lesson_completed"].format(day=day),
                reply_markup=main_keyboard()
            )
        else:
            await query.answer("این درس قبلاً تکمیل شده است.", show_alert=True)
    
    elif data.startswith("review_code_"):
        await query.answer("این قابلیت به زودی اضافه می‌شود!", show_alert=True)
    
    elif data.startswith("help_"):
        await query.answer("راهنمایی ارسال شد!", show_alert=True)
        await query.message.reply_text(
            "💡 برای دریافت راهنمایی بیشتر، سوال خود را دقیق بنویسید.",
            reply_markup=main_keyboard()
        )