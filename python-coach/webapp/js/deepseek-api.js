/**
 * مدیریت ارتباط با DeepSeek API
 */

class DeepSeekAPI {
    constructor() {
        // کلید API - در تولید از محیط یا سرور بگیر
        this.apiKey = null;
        this.baseURL = 'https://api.deepseek.com';
        this.model = 'deepseek-chat';
        
        // ذخیره‌سازی درخواست‌ها برای کاهش مصرف
        this.cache = new Map();
        this.maxCacheSize = 100;
    }
    
    /**
     * تنظیم کلید API
     */
    setApiKey(apiKey) {
        this.apiKey = apiKey;
        console.log('🔑 DeepSeek API key configured');
    }
    
    /**
     * درخواست تولید محتوا برای یک درس
     */
    async generateLessonContent(chapterTitle, lessonTitle, options = {}) {
        const cacheKey = `lesson_${chapterTitle}_${lessonTitle}`;
        
        // چک کش
        if (this.cache.has(cacheKey) && !options.forceRefresh) {
            console.log('📦 Using cached content');
            return this.cache.get(cacheKey);
        }
        
        const prompt = this.createLessonPrompt(chapterTitle, lessonTitle, options);
        
        try {
            console.log('🤖 Requesting lesson content from DeepSeek...');
            
            const response = await this.makeRequest(prompt, options);
            
            if (response && response.choices && response.choices[0]) {
                const content = response.choices[0].message.content;
                const parsedContent = this.parseResponse(content);
                
                // ذخیره در کش
                this.cache.set(cacheKey, parsedContent);
                this.cleanCache();
                
                console.log('✅ Lesson content generated successfully');
                return parsedContent;
            }
            
            throw new Error('Invalid response from DeepSeek API');
            
        } catch (error) {
            console.error('❌ DeepSeek API error:', error);
            throw error;
        }
    }
    
    /**
     * درخواست محتوای تکمیلی (Enhanced)
     */
    async generateEnhancedContent(chapterTitle, lessonTitle, topic, currentContent) {
        const prompt = this.createEnhancedPrompt(chapterTitle, lessonTitle, topic, currentContent);
        
        try {
            console.log('✨ Requesting enhanced content...');
            
            const response = await this.makeRequest(prompt, {
                temperature: 0.8,
                max_tokens: 1000
            });
            
            if (response && response.choices && response.choices[0]) {
                return this.parseEnhancedResponse(response.choices[0].message.content);
            }
            
            return this.getFallbackEnhancedContent();
            
        } catch (error) {
            console.warn('⚠️ Using fallback enhanced content:', error);
            return this.getFallbackEnhancedContent();
        }
    }
    
    /**
     * درخواست مثال‌های بیشتر
     */
    async generateMoreExamples(topic, difficulty = 'beginner', count = 3) {
        const prompt = this.createExamplesPrompt(topic, difficulty, count);
        
        try {
            const response = await this.makeRequest(prompt, {
                temperature: 0.7,
                max_tokens: 800
            });
            
            if (response && response.choices && response.choices[0]) {
                return this.parseExamplesResponse(response.choices[0].message.content);
            }
            
            return this.getFallbackExamples(topic, count);
            
        } catch (error) {
            console.warn('⚠️ Using fallback examples:', error);
            return this.getFallbackExamples(topic, count);
        }
    }
    
    /**
     * ایجاد تمرین‌های سفارشی
     */
    async generateExercises(topic, difficulty = 'beginner', count = 3) {
        const prompt = this.createExercisesPrompt(topic, difficulty, count);
        
        try {
            const response = await this.makeRequest(prompt, {
                temperature: 0.6,
                max_tokens: 600
            });
            
            if (response && response.choices && response.choices[0]) {
                return this.parseExercisesResponse(response.choices[0].message.content);
            }
            
            return this.getFallbackExercises(topic, count);
            
        } catch (error) {
            console.warn('⚠️ Using fallback exercises:', error);
            return this.getFallbackExercises(topic, count);
        }
    }
    
    /**
     * ارسال درخواست به API
     */
    async makeRequest(prompt, options = {}) {
        // اگر API key نداریم، از سرور خودمان استفاده می‌کنیم
        if (!this.apiKey) {
            return this.makeRequestThroughProxy(prompt, options);
        }
        
        const requestBody = {
            model: this.model,
            messages: [
                {
                    role: 'system',
                    content: 'You are an expert Python programming teacher teaching in Persian. Provide clear, concise, and practical explanations.'
                },
                {
                    role: 'user',
                    content: prompt
                }
            ],
            temperature: options.temperature || 0.7,
            max_tokens: options.max_tokens || 1500,
            stream: false
        };
        
        try {
            const response = await fetch(`${this.baseURL}/chat/completions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify(requestBody)
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('❌ Direct API request failed, trying proxy...');
            return this.makeRequestThroughProxy(prompt, options);
        }
    }
    
    /**
     * درخواست از طریق سرور پروکسی (ایمن‌تر)
     */
    async makeRequestThroughProxy(prompt, options = {}) {
        try {
            const response = await fetch('/api/deepseek', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: prompt,
                    options: options
                })
            });
            
            if (!response.ok) {
                throw new Error(`Proxy error: ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('❌ Proxy request failed:', error);
            throw error;
        }
    }
    
    /**
     * ایجاد prompt برای درس
     */
    createLessonPrompt(chapterTitle, lessonTitle, options = {}) {
        return `به عنوان استاد حرفه‌ای پایتون که به فارسی تدریس می‌کنی، یک درس کامل درباره "${lessonTitle}" از فصل "${chapterTitle}" بنویس.

نیازمندی‌های درس:
۱. توضیح تئوری به فارسی روان و ساده
۲. حداقل ۳ مثال کد قابل اجرا با توضیح
۳. ۲ تمرین آسان و ۲ تمرین متوسط با راه‌حل
۴. نکات کلیدی و بهترین روش‌ها
۵. کاربرد عملی در پروژه‌های واقعی

سطح: ${options.difficulty || 'مبتدی'}
زبان: فارسی روان
قالب: JSON ساختاریافته

لطفاً پاسخ را به این فرمت JSON بده:
{
  "title": "عنوان درس",
  "theory": "محتوی تئوری کامل",
  "examples": [
    {
      "title": "عنوان مثال",
      "code": "کد پایتون",
      "explanation": "توضیح مثال"
    }
  ],
  "exercises": [
    {
      "title": "عنوان تمرین",
      "question": "صورت تمرین",
      "difficulty": "آسان/متوسط",
      "hint": "راهنمایی",
      "solution": "راه‌حل کامل"
    }
  ],
  "key_points": ["نکته ۱", "نکته ۲"],
  "practical_applications": "کاربردهای عملی"
}`;
    }
    
    /**
     * ایجاد prompt برای محتوای تکمیلی
     */
    createEnhancedPrompt(chapterTitle, lessonTitle, topic, currentContent) {
        return `به عنوان استاد پایتون، محتوای تکمیلی و پیشرفته درباره "${topic}" از درس "${lessonTitle}" بنویس.

محتوای فعلی:
${currentContent}

لطفاً:
۱. نکات پیشرفته‌تر اضافه کن
۲. مثال‌های پیچیده‌تر بده
۳. اشتباهات رایج را توضیح بده
۴. بهترین روش‌ها (best practices) را ذکر کن
۵. منابع برای مطالعه بیشتر پیشنهاد بده

زبان: فارسی
سطح: پیشرفته`;
    }
    
    /**
     * پردازش پاسخ API
     */
    parseResponse(responseText) {
        try {
            // سعی کن JSON را parse کن
            const jsonMatch = responseText.match(/```json\n([\s\S]*?)\n```/) || 
                             responseText.match(/{[\s\S]*}/);
            
            if (jsonMatch) {
                const jsonStr = jsonMatch[1] || jsonMatch[0];
                return JSON.parse(jsonStr);
            }
            
            // اگر JSON نبود، متن ساده
            return {
                title: "درس تولید شده",
                theory: responseText,
                examples: [],
                exercises: [],
                key_points: [],
                practical_applications: ""
            };
            
        } catch (error) {
            console.warn('⚠️ Failed to parse JSON response:', error);
            return this.getFallbackContent();
        }
    }
    
    /**
     * محتوای پیش‌فرض در صورت خطا
     */
    getFallbackContent() {
        return {
            title: "آموزش پایتون",
            theory: "در این درس با مفاهیم پایه پایتون آشنا می‌شوید...",
            examples: [
                {
                    title: "برنامه اول",
                    code: "print('سلام دنیا!')",
                    explanation: "اولین برنامه پایتون"
                }
            ],
            exercises: [
                {
                    title: "تمرین ساده",
                    question: "برنامه‌ای بنویسید که نام شما را چاپ کند.",
                    difficulty: "آسان",
                    hint: "از تابع print استفاده کنید",
                    solution: "print('نام شما')"
                }
            ],
            key_points: ["پایتون زبان ساده‌ای است", "برای شروع عالی است"],
            practical_applications: "اتوماسیون، تحلیل داده، وب‌سایت"
        };
    }
    
    /**
     * تمیز کردن کش قدیمی
     */
    cleanCache() {
        if (this.cache.size > this.maxCacheSize) {
            const keys = Array.from(this.cache.keys());
            const keysToDelete = keys.slice(0, this.cache.size - this.maxCacheSize);
            keysToDelete.forEach(key => this.cache.delete(key));
        }
    }
    
    /**
     * دریافت وضعیت API
     */
    getStatus() {
        return {
            configured: !!this.apiKey,
            cacheSize: this.cache.size,
            model: this.model,
            baseURL: this.baseURL
        };
    }
    
    /**
     * پاک کردن کش
     */
    clearCache() {
        this.cache.clear();
        console.log('🗑️ Cache cleared');
    }
}

// ایجاد نمونه global
window.deepSeekAPI = new DeepSeekAPI();