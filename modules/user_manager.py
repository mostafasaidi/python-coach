"""
مدیریت کاربران و ذخیره‌سازی داده‌ها
"""

import os
import json
from datetime import datetime
from utils.helpers import save_json, load_json

class UserManager:
    def __init__(self):
        self.users_dir = "data/users"
    
    def get_user_path(self, user_id):
        """دریافت مسیر فایل کاربر"""
        return os.path.join(self.users_dir, f"{user_id}.json")
    
    def create_user(self, user_id, username=""):
        """ایجاد کاربر جدید"""
        from utils.constants import DEFAULT_SETTINGS
        
        user_data = {
            "user_id": user_id,
            "username": username,
            "current_day": 1,
            "completed_lessons": [],
            "exercise_start_times": {},
            "last_active": datetime.now().isoformat(),
            "join_date": datetime.now().isoformat(),
            "settings": DEFAULT_SETTINGS.copy(),
            "lesson_data": {}
        }
        
        self.save_user(user_id, user_data)
        return user_data
    
    def load_user(self, user_id):
        """بارگذاری اطلاعات کاربر"""
        user_path = self.get_user_path(user_id)
        user_data = load_json(user_path)
        
        if user_data is None:
            return self.create_user(user_id)
        
        # اطمینان از وجود همه فیلدها
        from utils.constants import DEFAULT_SETTINGS
        
        required_fields = {
            "current_day": 1,
            "completed_lessons": [],
            "exercise_start_times": {},
            "settings": DEFAULT_SETTINGS.copy(),
            "lesson_data": {}
        }
        
        for field, default_value in required_fields.items():
            if field not in user_data:
                user_data[field] = default_value
        
        return user_data
    
    def save_user(self, user_id, user_data):
        """ذخیره اطلاعات کاربر"""
        user_path = self.get_user_path(user_id)
        return save_json(user_data, user_path)
    
    def update_activity(self, user_id, username=""):
        """به‌روزرسانی فعالیت کاربر"""
        user = self.load_user(user_id)
        
        if username and user.get("username") != username:
            user["username"] = username
        
        user["last_active"] = datetime.now().isoformat()
        self.save_user(user_id, user)
        return user
    
    def start_exercise_timer(self, user_id, day):
        """شروع تایمر تمرین"""
        user = self.load_user(user_id)
        user["exercise_start_times"][str(day)] = datetime.now().isoformat()
        self.save_user(user_id, user)
    
    def can_get_answers(self, user_id, day, min_minutes=15):
        """بررسی امکان دریافت پاسخ"""
        user = self.load_user(user_id)
        day_key = str(day)
        
        if day_key not in user["exercise_start_times"]:
            self.start_exercise_timer(user_id, day)
            return False, f"⏳ تایمر شروع شد. حداقل {min_minutes} دقیقه تلاش کنید."
        
        start_time = datetime.fromisoformat(user["exercise_start_times"][day_key])
        current_time = datetime.now()
        time_diff = current_time - start_time
        
        required_seconds = min_minutes * 60
        
        if time_diff.total_seconds() < required_seconds:
            remaining = required_seconds - time_diff.total_seconds()
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            return False, f"⏳ {minutes} دقیقه و {seconds} ثانیه دیگر تلاش کنید."
        
        return True, "✅ می‌توانید پاسخ‌ها را دریافت کنید."
    
    def save_lesson_data(self, user_id, day, lesson_data):
        """ذخیره داده‌های درس"""
        user = self.load_user(user_id)
        user["lesson_data"][str(day)] = lesson_data
        self.save_user(user_id, user)
    
    def get_lesson_data(self, user_id, day):
        """دریافت داده‌های درس"""
        user = self.load_user(user_id)
        return user["lesson_data"].get(str(day))
    
    def complete_lesson(self, user_id, day):
        """تکمیل درس"""
        user = self.load_user(user_id)
        
        if day not in user["completed_lessons"]:
            user["completed_lessons"].append(day)
            user["completed_lessons"].sort()
            
            # یافتن روز بعدی
            for next_day in range(day + 1, 61):
                if next_day not in user["completed_lessons"]:
                    user["current_day"] = next_day
                    break
            else:
                user["current_day"] = 61  # تمام شده
            
            self.save_user(user_id, user)
            return True
        
        return False
    
    def reset_user(self, user_id):
        """بازنشانی کاربر"""
        user_path = self.get_user_path(user_id)
        if os.path.exists(user_path):
            os.remove(user_path)
        return self.create_user(user_id)

# ایجاد instance全局
user_manager = UserManager()