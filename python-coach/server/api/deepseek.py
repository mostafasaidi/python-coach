# server/api/deepseek.py
"""
API endpoint برای ارتباط با DeepSeek از طریق سرور (ایمن‌تر)
"""

import os
import json
import logging
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import requests

# بارگذاری محیط
load_dotenv()

# تنظیمات
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = 'https://api.deepseek.com/chat/completions'
MODEL = 'deepseek-chat'

# ایجاد blueprint
deepseek_bp = Blueprint('deepseek', __name__)

logger = logging.getLogger(__name__)

@deepseek_bp.route('/deepseek', methods=['POST'])
def deepseek_proxy():
    """
    endpoint پروکسی برای DeepSeek API
    """
    try:
        # دریافت داده‌ها
        data = request.json
        prompt = data.get('prompt', '')
        options = data.get('options', {})
        
        if not prompt:
            return jsonify({
                'status': 'error',
                'message': 'Prompt is required'
            }), 400
        
        logger.info(f'📤 DeepSeek request: {prompt[:100]}...')
        
        # اگر API key نداریم، پاسخ پیش‌فرض بده
        if not DEEPSEEK_API_KEY:
            logger.warning('DeepSeek API key not configured, using mock response')
            return generate_mock_response(prompt, options)
        
        # درخواست به DeepSeek API
        response = make_deepseek_request(prompt, options)
        
        logger.info(f'✅ DeepSeek response received')
        return jsonify(response)
        
    except Exception as e:
        logger.error(f'❌ DeepSeek proxy error: {e}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def make_deepseek_request(prompt: str, options: dict):
    """
    ارسال درخواست به DeepSeek API
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}'
    }
    
    request_body = {
        'model': MODEL,
        'messages': [
            {
                'role': 'system',
                'content': 'You are an expert Python teacher. Respond in Persian.'
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
            DEEPSEEK_API_URL,
            headers=headers,
            json=request_body,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f'DeepSeek API request failed: {e}')
        raise

def generate_mock_response(prompt: str, options: dict):
    """
    پاسخ mock برای زمانی که API key نداریم
    """
    # تشخیص نوع درخواست از prompt
    if 'درس کامل' in prompt or 'lesson' in prompt.lower():
        return get_mock_lesson()
    elif 'مثال' in prompt or 'example' in prompt.lower():
        return get_mock_examples()
    elif 'تمرین' in prompt or 'exercise' in prompt.lower():
        return get_mock_exercises()
    else:
        return get_general_mock_response()

def get_mock_lesson():
    """پاسخ mock برای درس"""
    return {
        'id': 'mock_123',
        'object': 'chat.completion',
        'created': 1234567890,
        'model': MODEL,
        'choices': [
            {
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': json.dumps({
                        'title': 'مقدمه‌ای بر پایتون',
                        'theory': 'پایتون یک زبان برنامه‌نویسی سطح بالا و تفسیری است...',
                        'examples': [
                            {
                                'title': 'سلام دنیا',
                                'code': 'print("سلام دنیا!")',
                                'explanation': 'اولین برنامه پایتون'
                            }
                        ],
                        'exercises': [
                            {
                                'title': 'نمایش نام',
                                'question': 'برنامه‌ای بنویسید که نام شما را چاپ کند.',
                                'difficulty': 'آسان',
                                'hint': 'از تابع print استفاده کنید',
                                'solution': 'print("نام شما")'
                            }
                        ],
                        'key_points': ['پایتون ساده است', 'یادگیری آسان'],
                        'practical_applications': 'اتوماسیون، وب، داده‌کاوی'
                    }, ensure_ascii=False)
                },
                'finish_reason': 'stop'
            }
        ],
        'usage': {
            'prompt_tokens': 100,
            'completion_tokens': 500,
            'total_tokens': 600
        }
    }

def get_mock_examples():
    """پاسخ mock برای مثال‌ها"""
    return {
        'choices': [
            {
                'message': {
                    'content': 'مثال‌های اضافی:\n1. کار با لیست‌ها\n2. حلقه‌های تو در تو\n3. توابع بازگشتی'
                }
            }
        ]
    }

def get_mock_exercises():
    """پاسخ mock برای تمرین‌ها"""
    return {
        'choices': [
            {
                'message': {
                    'content': 'تمرین‌های اضافی:\n1. ماشین حساب ساده\n2. بازی حدس عدد\n3. مدیریت مخاطبین'
                }
            }
        ]
    }

def get_general_mock_response():
    """پاسخ عمومی mock"""
    return {
        'choices': [
            {
                'message': {
                    'content': 'این یک پاسخ آزمایشی است. در نسخه واقعی از DeepSeek API استفاده می‌شود.'
                }
            }
        ]
    }