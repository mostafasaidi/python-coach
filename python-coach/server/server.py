
import os
import json
import requests
from dotenv import load_dotenv

# بارگذاری محیط
load_dotenv()

# کلید DeepSeek API (اگر در .env باشد)
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')





from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
import os
import json
from datetime import datetime
import logging

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
           static_folder='../webapp',
           static_url_path='')
CORS(app)

# مسیر فایل‌های داده
DATA_DIR = os.path.join(os.path.dirname(__file__), '../webapp/data')

@app.route('/')
def index():
    """صفحه اصلی Mini App"""
    return send_file('../webapp/index.html')

@app.route('/chapter/<int:chapter_id>')
def chapter_page(chapter_id):
    """صفحه فصل"""
    return send_file('../webapp/chapter.html')

@app.route('/lesson/<chapter_id>/<lesson_id>')
def lesson_page(chapter_id, lesson_id):
    """صفحه درس"""
    return send_file('../webapp/lesson.html')

@app.route('/editor')
def editor_page():
    """صفحه ویرایشگر کد"""
    return send_file('../webapp/editor.html')

@app.route('/api/chapters')
def get_chapters():
    """دریافت لیست فصل‌ها"""
    chapters_file = os.path.join(DATA_DIR, 'chapters.json')
    
    if os.path.exists(chapters_file):
        try:
            with open(chapters_file, 'r', encoding='utf-8') as f:
                chapters = json.load(f)
            return jsonify(chapters)
        except Exception as e:
            logger.error(f"خطا در خواندن فایل فصل‌ها: {e}")
    
    # داده پیش‌فرض اگر فایل وجود نداشت
    default_chapters = [
        {"id": 1, "title": "شروع با پایتون", "description": "نصب، متغیرها، انواع داده", "lessons": 5, "progress": 0},
        {"id": 2, "title": "کنترل جریان و حلقه‌ها", "description": "شرط‌ها، حلقه for و while", "lessons": 5, "progress": 0},
        {"id": 3, "title": "توابع و ماژول‌ها", "description": "تعریف توابع، import ماژول‌ها", "lessons": 5, "progress": 0},
        {"id": 4, "title": "کار با فایل و استثناها", "description": "خواندن/نوشتن فایل، مدیریت خطا", "lessons": 5, "progress": 0},
        {"id": 5, "title": "برنامه‌نویسی شیءگرا", "description": "کلاس، وراثت، magic methods", "lessons": 5, "progress": 0},
        {"id": 6, "title": "کتابخانه‌های استاندارد", "description": "datetime, json, os, pathlib", "lessons": 5, "progress": 0},
        {"id": 7, "title": "NumPy کامل", "description": "آرایه‌ها، عملیات ریاضی", "lessons": 5, "progress": 0},
        {"id": 8, "title": "Pandas و تحلیل داده", "description": "DataFrame، تحلیل داده‌ها", "lessons": 5, "progress": 0},
        {"id": 9, "title": "مصورسازی داده", "description": "Matplotlib، Seaborn", "lessons": 5, "progress": 0},
        {"id": 10, "title": "مقدمه‌ای بر یادگیری ماشین", "description": "مفاهیم پایه ML", "lessons": 5, "progress": 0},
        {"id": 11, "title": "یادگیری عملی با Scikit-learn", "description": "مدل‌های طبقه‌بندی و رگرسیون", "lessons": 5, "progress": 0},
        {"id": 12, "title": "مقدمه‌ای بر یادگیری عمیق", "description": "شبکه‌های عصبی پایه", "lessons": 5, "progress": 0},
        {"id": 13, "title": "PyTorch مقدماتی", "description": "تنسورها، autograd", "lessons": 5, "progress": 0},
        {"id": 14, "title": "شبکه‌های عصبی با PyTorch", "description": "MLP، CNN، RNN", "lessons": 5, "progress": 0},
        {"id": 15, "title": "مدل‌های پیشرفته و Transformers", "description": "Transfer Learning، HuggingFace", "lessons": 5, "progress": 0},
        {"id": 16, "title": "استقرار مدل‌ها و پروژه نهایی", "description": "FastAPI، Streamlit، Docker", "lessons": 5, "progress": 0}
    ]
    
    return jsonify(default_chapters)

@app.route('/api/lesson/<int:chapter_id>/<lesson_id>')
def get_lesson(chapter_id, lesson_id):
    """دریافت محتوای یک درس"""
    basic_file = os.path.join(DATA_DIR, 'basic', f'{chapter_id}.json')
    
    if os.path.exists(basic_file):
        try:
            with open(basic_file, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
            
            # پیدا کردن درس مورد نظر
            for lesson in chapter_data.get('lessons', []):
                if lesson.get('id') == f"{chapter_id}.{lesson_id}":
                    return jsonify({
                        "status": "success",
                        "data": lesson,
                        "source": "basic"
                    })
        except Exception as e:
            logger.error(f"خطا در خواندن درس: {e}")
    
    # اگر درس پیدا نشد
    return jsonify({
        "status": "error",
        "message": "درس یافت نشد",
        "data": {
            "id": f"{chapter_id}.{lesson_id}",
            "title": "درس در حال آماده‌سازی",
            "content": "این درس به زودی اضافه خواهد شد.",
            "examples": [],
            "exercises": []
        }
    })

@app.route('/api/enhance', methods=['POST'])
def enhance_lesson():
    """درخواست محتوای بیشتر از DeepSeek"""
    try:
        data = request.json
        chapter_id = data.get('chapter_id')
        lesson_id = data.get('lesson_id')
        topic = data.get('topic')
        
        logger.info(f"درخواست محتوای بیشتر برای: فصل {chapter_id}، درس {lesson_id}")
        
        # اینجا در آینده به DeepSeek API وصل می‌شویم
        # فعلاً پاسخ ثابت می‌دهیم
        
        enhanced_content = {
            "enhanced": True,
            "timestamp": datetime.now().isoformat(),
            "additional_content": "این محتوای تکمیلی است که از DeepSeek دریافت شده است.",
            "extra_examples": [
                "مثال تکمیلی ۱",
                "مثال تکمیلی ۲"
            ],
            "advanced_exercises": [
                {"question": "تمرین پیشرفته ۱", "hint": "راهنمایی ۱"},
                {"question": "تمرین پیشرفته ۲", "hint": "راهنمایی ۲"}
            ]
        }
        
        return jsonify({
            "status": "success",
            "message": "محتوای تکمیلی تولید شد",
            "data": enhanced_content
        })
        
    except Exception as e:
        logger.error(f"خطا در تولید محتوای تکمیلی: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/progress', methods=['POST'])
def save_progress():
    """ذخیره پیشرفت کاربر"""
    try:
        data = request.json
        user_id = data.get('user_id')
        chapter_id = data.get('chapter_id')
        lesson_id = data.get('lesson_id')
        progress = data.get('progress', {})
        
        logger.info(f"ذخیره پیشرفت کاربر {user_id}: فصل {chapter_id}، درس {lesson_id}")
        
        # در اینجا می‌توانی در دیتابیس یا فایل ذخیره کنی
        # فعلاً فقط لاگ می‌کنیم
        
        return jsonify({
            "status": "success",
            "message": "پیشرفت ذخیره شد"
        })
        
    except Exception as e:
        logger.error(f"خطا در ذخیره پیشرفت: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/execute', methods=['POST'])
def execute_code():
    """اجرای کد پایتون"""
    try:
        data = request.json
        code = data.get('code', '')
        
        # امنیت: بررسی کدهای خطرناک
        dangerous_patterns = ['os.system', 'subprocess', '__import__', 'eval', 'exec']
        for pattern in dangerous_patterns:
            if pattern in code:
                return jsonify({
                    "status": "error",
                    "output": f"❌ کد ناامن: استفاده از {pattern} مجاز نیست"
                })
        
        # در اینجا می‌توانی از یک سرویس اجرای کد استفاده کنی
        # یا با Docker کد را اجرا کنی
        # فعلاً پاسخ ثابت می‌دهیم
        
        return jsonify({
            "status": "success",
            "output": "✅ کد با موفقیت اجرا شد.\nخروجی: Hello, World!",
            "execution_time": "0.15s"
        })
        
    except Exception as e:
        logger.error(f"خطا در اجرای کد: {e}")
        return jsonify({
            "status": "error",
            "output": f"❌ خطا در اجرای کد: {str(e)}"
        })

@app.route('/health')
def health_check():
    """بررسی سلامت سرور"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Python Coach Mini App Server"
    })

@app.route('/api/deepseek', methods=['POST'])
def deepseek_proxy():
    """
    پروکسی برای DeepSeek API
    """
    try:
        # دریافت داده‌ها از درخواست
        data = request.json
        prompt = data.get('prompt', '')
        options = data.get('options', {})
        
        if not prompt:
            return jsonify({
                'status': 'error',
                'message': 'Prompt is required'
            }), 400
        
        print(f'🤖 DeepSeek request: {prompt[:100]}...')
        
        # اگر API key نداریم، از mock data استفاده کن
        if not DEEPSEEK_API_KEY:
            print('⚠️ Using mock response (no API key)')
            return jsonify(get_mock_deepseek_response(prompt))
        
        # ارسال به DeepSeek API واقعی
        response = call_deepseek_api(prompt, options)
        return jsonify(response)
        
    except Exception as e:
        print(f'❌ DeepSeek error: {e}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def call_deepseek_api(prompt, options):
    """تماس با DeepSeek API واقعی"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}'
    }
    
    request_body = {
        'model': 'deepseek-chat',
        'messages': [
            {
                'role': 'system',
                'content': 'You are an expert Python programming teacher teaching in Persian. Provide clear, practical explanations.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'temperature': options.get('temperature', 0.7),
        'max_tokens': options.get('max_tokens', 1500),
        'stream': False
    }
    
    try:
        response = requests.post(
            'https://api.deepseek.com/chat/completions',
            headers=headers,
            json=request_body,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f'DeepSeek API call failed: {e}')
        # در صورت خطا، mock data برگردان
        return get_mock_deepseek_response(prompt)

def get_mock_deepseek_response(prompt):
    """داده‌های آزمایشی برای زمانی که API کار نمی‌کند"""
    # تشخیص نوع درخواست
    if 'درس' in prompt or 'lesson' in prompt.lower():
        return {
            'id': 'mock_123',
            'object': 'chat.completion',
            'created': 1234567890,
            'model': 'deepseek-chat',
            'choices': [
                {
                    'index': 0,
                    'message': {
                        'role': 'assistant',
                        'content': json.dumps({
                            'title': 'آموزش پایتون - نسخه آزمایشی',
                            'theory': 'این محتوای آزمایشی است. در نسخه واقعی از DeepSeek API استفاده خواهد شد.\n\nپایتون یک زبان برنامه‌نویسی سطح بالا است که برای شروع عالی می‌باشد.',
                            'examples': [
                                {
                                    'title': 'برنامه اول',
                                    'code': 'print("سلام! به پایتون کوچ خوش آمدید.")',
                                    'explanation': 'تابع print برای نمایش خروجی استفاده می‌شود.'
                                },
                                {
                                    'title': 'متغیرها',
                                    'code': 'name = "علی"\nage = 25\nprint(f"نام: {name}, سن: {age}")',
                                    'explanation': 'تعریف متغیر و استفاده از f-string'
                                }
                            ],
                            'exercises': [
                                {
                                    'title': 'تمرین ۱',
                                    'question': 'برنامه‌ای بنویسید که نام شما را چاپ کند.',
                                    'difficulty': 'آسان',
                                    'hint': 'از تابع print استفاده کنید',
                                    'solution': 'print("نام شما")'
                                },
                                {
                                    'title': 'تمرین ۲',
                                    'question': 'برنامه‌ای بنویسید که دو عدد را جمع کند.',
                                    'difficulty': 'آسان',
                                    'hint': 'از عملگر + استفاده کنید',
                                    'solution': 'a = 5\nb = 3\nresult = a + b\nprint(result)'
                                }
                            ],
                            'key_points': [
                                'پایتون زبان ساده و خوانایی است',
                                'برای شروع برنامه‌نویسی عالی است',
                                'کاربردهای گسترده‌ای دارد'
                            ],
                            'practical_applications': 'می‌توانید با پایتون اسکریپت بنویسید، داده تحلیل کنید، وب‌سایت بسازید و...'
                        }, ensure_ascii=False)
                    },
                    'finish_reason': 'stop'
                }
            ],
            'usage': {
                'prompt_tokens': 50,
                'completion_tokens': 300,
                'total_tokens': 350
            }
        }
    else:
        # پاسخ عمومی
        return {
            'choices': [
                {
                    'message': {
                        'content': 'این یک پاسخ آزمایشی است. برای استفاده از قابلیت کامل، کلید DeepSeek API را تنظیم کنید.'
                    }
                }
            ]
        }

@app.route('/api/deepseek-test', methods=['GET'])
def deepseek_test():
    """تست endpoint DeepSeek"""
    return jsonify({
        'status': 'ready',
        'message': 'DeepSeek endpoint is working',
        'api_key_configured': bool(DEEPSEEK_API_KEY),
        'endpoint': '/api/deepseek (POST)'
    })

if __name__ == '__main__':
    # اطمینان از وجود دایرکتوری داده
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, 'basic'), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, 'enhanced'), exist_ok=True)
    
    logger.info("🚀 سرور Mini App در حال راه‌اندازی...")
    logger.info(f"📁 دایرکتوری داده: {DATA_DIR}")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

    # در ابتدای فایل، بعد از importها
from api.deepseek import deepseek_bp

# بعد از ایجاد app، blueprint را ثبت کن
app.register_blueprint(deepseek_bp, url_prefix='/api')

# همچنین این endpoint جدید اضافه کن:
@app.route('/api/deepseek-test')
def deepseek_test():
    """تست اتصال به DeepSeek"""
    return jsonify({
        'status': 'ready',
        'message': 'DeepSeek API endpoint is working',
        'endpoints': {
            'post': '/api/deepseek',
            'test': '/api/deepseek-test'
        }
    })