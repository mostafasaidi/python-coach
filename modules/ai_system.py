"""
سیستم هوش مصنوعی با DeepSeek API
"""

import os
import json
import requests
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AISystem:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.timeout = 60
    
    def ask(self, prompt, system_prompt=None, max_tokens=2000):
        """ارسال درخواست به DeepSeek"""
        if not self.api_key:
            return "❌ کلید API تنظیم نشده است"
        
        for attempt in range(3):
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = requests.post(
                    self.base_url,
                    json={
                        "model": "deepseek-chat",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": max_tokens,
                        "top_p": 0.95
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()["choices"][0]["message"]["content"]
                    # حذف خطاهای احتمالی از ابتدای پاسخ
                    if result.startswith("خطا:") or result.startswith("Error:"):
                        result = result.replace("خطا:", "").replace("Error:", "").strip()
                    return result
                elif response.status_code == 401:
                    return "❌ کلید API نامعتبر است"
                elif response.status_code == 429:
                    time.sleep(2)
                    continue
                else:
                    return f"⚠️ خطای API: {response.status_code}"
                    
            except requests.exceptions.Timeout:
                if attempt < 2:
                    time.sleep(3)
                    continue
                return "⏱️ درخواست timeout شد"
            except requests.exceptions.ConnectionError:
                if attempt < 2:
                    time.sleep(3)
                    continue
                return "🔌 مشکل اتصال به اینترنت"
            except Exception as e:
                if attempt < 2:
                    time.sleep(3)
                    continue
                return f"⚠️ خطا: {str(e)[:100]}"
        
        return "⚠️ بعد از ۳ بار تلاش، عملیات ناموفق بود"
    
    def generate_lesson(self, day, topic, difficulty, language):
        """تولید محتوای یک درس کامل"""
        from utils.constants import PYTHON_TOPICS
        
        prompt = f"""
        تولید محتوای کامل برای درس روز {day} آموزش پایتون.
        
        موضوع: {topic}
        سطح: {difficulty}
        زبان: {'فارسی' if language == 'persian' else 'انگلیسی'}
        
        **لطفاً خروجی را در قالب JSON زیر ارائه دهید:**
        
        {{
          "day": {day},
          "topic": "{topic}",
          "difficulty": "{difficulty}",
          "language": "{language}",
          "goals": ["هدف ۱", "هدف ۲", "هدف ۳"],
          "concepts": "توضیحات مفاهیم اصلی",
          "examples": [
            {{
              "title": "مثال ۱",
              "description": "توضیح",
              "code": "# کد پایتون",
              "explanation": "توضیح کد"
            }}
          ],
          "exercises": [
            {{
              "title": "تمرین ۱",
              "description": "شرح تمرین",
              "input": "ورودی",
              "output": "خروجی",
              "hint": "راهنمایی",
              "solution": "# کد پاسخ",
              "explanation": "توضیح راه‌حل"
            }}
          ],
          "key_points": ["نکته ۱", "نکته ۲", "نکته ۳"]
        }}
        
        **نکات:**
        ۱. خروجی فقط JSON باشد
        ۲. کدها کامل و قابل اجرا باشند
        ۳. توضیحات به زبان درخواستی باشد
        """
        
        system_prompt = f"تو یک مربی پایتون هستی. روز {day} - {topic}. سطح: {difficulty}"
        
        response = self.ask(prompt, system_prompt, max_tokens=4000)
        
        try:
            # استخراج JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("JSON یافت نشد")
            
            json_str = response[json_start:json_end]
            lesson_data = json.loads(json_str)
            
            # اضافه کردن تاریخ
            lesson_data['date'] = datetime.now().strftime("%Y/%m/%d")
            lesson_data['generated_at'] = datetime.now().isoformat()
            
            return lesson_data
            
        except Exception as e:
            logger.error(f"خطا در پردازش پاسخ AI: {e}")
            logger.error(f"پاسخ: {response[:500]}")
            
            # ساختار پیش‌فرض
            return {
                "day": day,
                "topic": topic,
                "difficulty": difficulty,
                "language": language,
                "goals": [f"یادگیری {topic}"],
                "concepts": f"مفاهیم اصلی {topic}",
                "examples": [],
                "exercises": [],
                "key_points": [],
                "date": datetime.now().strftime("%Y/%m/%d")
            }
    
    def answer_question(self, question, context=""):
        """پاسخ به سوال پایتون"""
        prompt = f"""
        سوال پایتون: {question}
        
        {f'متن زمینه: {context}' if context else ''}
        
        لطفاً پاسخ کامل و آموزشی ارائه دهید.
        """
        
        return self.ask(prompt, max_tokens=1500)

# ایجاد instance全局
ai_system = AISystem()