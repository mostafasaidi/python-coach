"""
توابع کمکی و ابزارها
"""

import os
import json
from datetime import datetime

def setup_directories():
    """ایجاد دایرکتوری‌های لازم"""
    directories = [
        "data/users",
        "data/pdfs/lessons",
        "data/pdfs/answers",
        "data/temp"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ دایرکتوری ایجاد شد: {directory}")

def format_time(seconds):
    """قالب‌بندی زمان به صورت خوانا"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours} ساعت و {minutes} دقیقه"
    elif minutes > 0:
        return f"{minutes} دقیقه و {secs} ثانیه"
    else:
        return f"{secs} ثانیه"

def save_json(data, filepath):
    """ذخیره داده در فایل JSON"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"خطا در ذخیره JSON: {e}")
        return False

def load_json(filepath):
    """بارگذاری داده از فایل JSON"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"خطا در بارگذاری JSON: {e}")
    return None

def split_message(text, max_length=4000):
    """تقسیم پیام طولانی"""
    if len(text) <= max_length:
        return [text]
    
    parts = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break
        
        split_point = text.rfind('\n\n', 0, max_length)
        if split_point == -1:
            split_point = text.rfind('\n', 0, max_length)
        if split_point == -1:
            split_point = text.rfind('. ', 0, max_length)
        if split_point == -1:
            split_point = max_length
        
        parts.append(text[:split_point + 1].strip())
        text = text[split_point + 1:].strip()
    
    return parts