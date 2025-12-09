/**
 * مدیریت صفحه درس
 */

class LessonPage {
    constructor() {
        this.chapterId = null;
        this.lessonId = null;
        this.lessonData = null;
        this.userProgress = 0;
    }
    
    async init() {
        console.log('📖 Initializing lesson page...');
        
        // دریافت پارامترهای URL
        this.extractParamsFromURL();
        
        if (!this.chapterId || !this.lessonId) {
            this.showError('درس یافت نشد!');
            setTimeout(() => window.location.href = '/', 2000);
            return;
        }
        
        // راه‌اندازی اولیه
        this.setupEventListeners();
        this.updateUI();
        
        // بارگذاری محتوای درس
        await this.loadLessonContent();
        
        console.log(`✅ Lesson ${this.chapterId}.${this.lessonId} loaded`);
    }
    
    extractParamsFromURL() {
        const path = window.location.pathname;
        const match = path.match(/\/lesson\/(\d+)\/(\d+)/);
        
        if (match) {
            this.chapterId = parseInt(match[1]);
            this.lessonId = parseInt(match[2]);
            console.log(`📚 Chapter ${this.chapterId}, Lesson ${this.lessonId}`);
        }
    }
    
    setupEventListeners() {
        // دکمه بازگشت
        document.getElementById('back-btn').addEventListener('click', () => {
            window.history.back();
        });
        
        // دکمه تکمیل درس
        document.getElementById('complete-btn').addEventListener('click', () => {
            this.completeLesson();
        });
        
        // دکمه درخواست محتوای بیشتر
        document.getElementById('request-enhanced').addEventListener('click', () => {
            this.requestEnhancedContent();
        });
        
        // دکمه‌های ناوبری
        document.getElementById('prev-lesson').addEventListener('click', () => {
            this.navigateToPrevLesson();
        });
        
        document.getElementById('next-lesson').addEventListener('click', () => {
            this.navigateToNextLesson();
        });
        
        // دکمه کپی کد
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('copy-btn')) {
                this.copyCode(e.target);
            }
        });
    }
    
    updateUI() {
        // به‌روزرسانی breadcrumb
        document.getElementById('breadcrumb').innerHTML = `
            <span>فصل ${this.chapterId}</span> / <span>درس ${this.lessonId}</span>
        `;
        
        // به‌روزرسانی عنوان
        document.getElementById('lesson-title').textContent = 
            `درس ${this.lessonId}: در حال بارگذاری...`;
    }
    
    async loadLessonContent() {
        try {
            // نمایش لودینگ
            this.showLoading();
            
            // در آینده از API سرور بگیریم
            // فعلاً از داده‌های نمونه استفاده می‌کنیم
            this.lessonData = await this.getSampleLessonData();
            
            // نمایش محتوا
            this.renderLessonContent();
            
            // به‌روزرسانی پیشرفت
            this.updateProgress(20);
            
        } catch (error) {
            console.error('❌ Error loading lesson:', error);
            this.showError('خطا در بارگذاری درس');
            this.showSampleContent();
        }
    }
    
    async getSampleLessonData() {
        // داده‌های نمونه برای درس
        return {
            title: `درس ${this.lessonId}: مفاهیم پایه`,
            theory: `
                <p>در این درس با مفاهیم پایه پایتون آشنا می‌شوید. پایتون یک زبان برنامه‌نویسی سطح بالا است که خوانایی و سادگی از ویژگی‌های اصلی آن است.</p>
                
                <h3>مهم‌ترین ویژگی‌های پایتون:</h3>
                <ul>
                    <li><strong>ساده و خوانا:</strong> نحو (syntax) ساده‌ای دارد</li>
                    <li><strong>مفسری:</strong> نیازی به کامپایل ندارد</li>
                    <li><strong>چندمنظوره:</strong> برای وب، داده، هوش مصنوعی و...</li>
                    <li><strong>کتابخانه‌های غنی:</strong> هزاران کتابخانه رایگان</li>
                </ul>
                
                <p>پایتون برای شروع برنامه‌نویسی بسیار مناسب است زیرا یادگیری آن آسان است و بازار کار خوبی دارد.</p>
            `,
            examples: [
                {
                    title: 'برنامه اول: سلام دنیا',
                    code: `# اولین برنامه پایتون
print("سلام دنیا!")
print("خوش آمدید به آموزش پایتون")`
                },
                {
                    title: 'متغیرها و انواع داده',
                    code: `# تعریف متغیرها
name = "علی"        # رشته
age = 25            # عدد صحیح
height = 175.5      # عدد اعشاری
is_student = True   # بولین

# چاپ مقادیر
print(f"نام: {name}")
print(f"سن: {age}")
print(f"قد: {height}")
print(f"دانشجو: {is_student}")`
                }
            ],
            exercises: [
                {
                    title: 'تمرین ۱: نمایش نام',
                    question: 'برنامه‌ای بنویسید که نام شما را بگیرد و پیام خوش‌آمد بدهد.',
                    hint: 'از تابع input() برای گرفتن ورودی استفاده کنید.'
                },
                {
                    title: 'تمرین ۲: محاسبه جمع',
                    question: 'برنامه‌ای بنویسید که دو عدد از کاربر بگیرد و حاصل جمع آن‌ها را نمایش دهد.',
                    hint: 'ورودی را با int() به عدد تبدیل کنید.'
                }
            ]
        };
    }
    
    renderLessonContent() {
        // مخفی کردن لودینگ
        this.hideLoading();
        
        // به‌روزرسانی عنوان
        document.getElementById('lesson-title').textContent = this.lessonData.title;
        
        // نمایش تئوری
        document.getElementById('theory-content').innerHTML = this.lessonData.theory;
        
        // نمایش مثال‌های کد
        this.renderCodeExamples();
        
        // نمایش تمرین‌ها
        this.renderExercises();
    }
    
    renderCodeExamples() {
        const examplesContainer = document.getElementById('code-examples');
        
        if (!this.lessonData.examples || this.lessonData.examples.length === 0) {
            examplesContainer.innerHTML = '<p class="no-content">مثالی برای نمایش وجود ندارد.</p>';
            return;
        }
        
        examplesContainer.innerHTML = this.lessonData.examples.map((example, index) => `
            <div class="code-example">
                <div class="code-header">
                    <span class="code-title">${example.title}</span>
                    <button class="copy-btn" data-code="${index}">
                        <i class="fas fa-copy"></i> کپی
                    </button>
                </div>
                <pre><code>${this.escapeHtml(example.code)}</code></pre>
            </div>
        `).join('');
    }
    
    renderExercises() {
        const exercisesContainer = document.getElementById('exercises');
        
        if (!this.lessonData.exercises || this.lessonData.exercises.length === 0) {
            exercisesContainer.innerHTML = '<p class="no-content">تمرینی برای نمایش وجود ندارد.</p>';
            return;
        }
        
        exercisesContainer.innerHTML = this.lessonData.exercises.map((exercise, index) => `
            <div class="exercise-card">
                <div class="exercise-title">
                    <i class="fas fa-dumbbell"></i>
                    <span>${exercise.title}</span>
                </div>
                <div class="exercise-question">${exercise.question}</div>
                <button class="hint-btn" data-hint-index="${index}">
                    <i class="fas fa-lightbulb"></i> نمایش راهنمایی
                </button>
                <div class="exercise-hint" id="hint-${index}">
                    <strong>راهنمایی:</strong> ${exercise.hint}
                </div>
            </div>
        `).join('');
        
        // اضافه کردن رویداد برای دکمه‌های راهنمایی
        document.querySelectorAll('.hint-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const hintIndex = e.target.dataset.hintIndex;
                const hintElement = document.getElementById(`hint-${hintIndex}`);
                hintElement.classList.toggle('show');
            });
        });
    }
    
    showSampleContent() {
        document.getElementById('theory-content').innerHTML = `
            <p>این درس در حال آماده‌سازی است. محتوای کامل به زودی اضافه می‌شود.</p>
            <p>برای دریافت محتوای سفارشی، روی دکمه "درخواست محتوای بیشتر" کلیک کنید.</p>
        `;
    }
    
    async requestEnhancedContent() {
        console.log('🤖 Requesting enhanced content from DeepSeek...');
        
        // نمایش لودینگ
        const enhancedSection = document.getElementById('enhanced-section');
        const enhancedContent = document.getElementById('enhanced-content');
        
        enhancedSection.style.display = 'block';
        enhancedContent.innerHTML = `
            <div class="loading" style="text-align: center; padding: 30px;">
                <i class="fas fa-spinner fa-spin fa-2x"></i>
                <p style="margin-top: 15px;">در حال تولید محتوای تکمیلی با DeepSeek...</p>
            </div>
        `;
        
        try {
            // در آینده اینجا به DeepSeek API متصل می‌شویم
            // فعلاً محتوای نمونه نمایش می‌دهیم
            
            setTimeout(() => {
                enhancedContent.innerHTML = `
                    <div class="enhanced-result">
                        <h3><i class="fas fa-robot"></i> پاسخ DeepSeek:</h3>
                        
                        <p>برای درس فعلی، محتوای تکمیلی زیر پیشنهاد می‌شود:</p>
                        
                        <h4>🎯 نکات پیشرفته:</h4>
                        <ul>
                            <li>پایتون از تورفتگی (indentation) برای تعریف بلوک‌های کد استفاده می‌کند</li>
                            <li>متغیرها در پایتون نیازی به تعیین نوع ندارند (Dynamic Typing)</li>
                            <li>می‌توانید از type hints برای مشخص کردن نوع متغیرها استفاده کنید</li>
                        </ul>
                        
                        <h4>💡 مثال تکمیلی:</h4>
                        <div class="code-example">
                            <div class="code-header">
                                <span class="code-title">بررسی نوع متغیر</span>
                                <button class="copy-btn">
                                    <i class="fas fa-copy"></i> کپی
                                </button>
                            </div>
                            <pre><code># بررسی نوع متغیرها
x = 10
y = "سلام"
z = [1, 2, 3]

print(f"نوع x: {type(x)}")    # <class 'int'>
print(f"نوع y: {type(y)}")    # <class 'str'>
print(f"نوع z: {type(z)}")    # <class 'list'>

# تبدیل نوع
number_str = "123"
number_int = int(number_str)  # تبدیل به عدد
print(f"عدد: {number_int}")</code></pre>
                        </div>
                        
                        <div class="enhanced-tip" style="margin-top: 20px; padding: 15px; background: rgba(76, 201, 240, 0.1); border-radius: 10px;">
                            <strong>💪 نکته:</strong> سعی کنید همه مثال‌ها را خودتان اجرا و تغییر دهید تا بهتر یاد بگیرید.
                        </div>
                    </div>
                `;
                
                // دوباره راه‌اندازی دکمه کپی
                this.setupCopyButtons();
                
            }, 2000); // شبیه‌سازی تاخیر API
            
        } catch (error) {
            console.error('❌ Error getting enhanced content:', error);
            enhancedContent.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>خطا در دریافت محتوای تکمیلی. لطفاً دوباره تلاش کنید.</p>
                </div>
            `;
        }
    }
    
    completeLesson() {
        const completeBtn = document.getElementById('complete-btn');
        
        // تغییر وضعیت دکمه
        completeBtn.classList.add('completed');
        completeBtn.innerHTML = '<i class="fas fa-check-circle"></i><span>تکمیل شده</span>';
        completeBtn.disabled = true;
        
        // به‌روزرسانی پیشرفت
        this.updateProgress(100);
        
        // ذخیره در localStorage
        this.saveProgress();
        
        // نمایش پیام موفقیت
        this.showNotification('🎉 درس با موفقیت تکمیل شد!', 'success');
        
        console.log(`✅ Lesson ${this.chapterId}.${this.lessonId} completed`);
    }
    
    updateProgress(percent) {
        this.userProgress = percent;
        
        // به‌روزرسانی نوار پیشرفت
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        if (progressFill) {
            progressFill.style.width = `${percent}%`;
        }
        
        if (progressText) {
            progressText.textContent = `${percent}%`;
        }
    }
    
    saveProgress() {
        try {
            // ذخیره در localStorage
            const progressKey = `chapter_${this.chapterId}_lesson_${this.lessonId}`;
            localStorage.setItem(progressKey, 'completed');
            
            // ذخیره در لیست درس‌های تکمیل شده
            let completedLessons = JSON.parse(localStorage.getItem('completed_lessons') || '[]');
            const lessonKey = `${this.chapterId}.${this.lessonId}`;
            
            if (!completedLessons.includes(lessonKey)) {
                completedLessons.push(lessonKey);
                localStorage.setItem('completed_lessons', JSON.stringify(completedLessons));
            }
            
            console.log('💾 Progress saved');
            
        } catch (error) {
            console.error('❌ Error saving progress:', error);
        }
    }
    
    navigateToPrevLesson() {
        if (this.lessonId > 1) {
            const prevLessonId = this.lessonId - 1;
            window.location.href = `/lesson/${this.chapterId}/${prevLessonId}`;
        } else {
            this.showNotification('این اولین درس است', 'info');
        }
    }
    
    navigateToNextLesson() {
        const nextLessonId = this.lessonId + 1;
        window.location.href = `/lesson/${this.chapterId}/${nextLessonId}`;
    }
    
    copyCode(button) {
        const codeIndex = button.dataset.code;
        const code = this.lessonData.examples[codeIndex].code;
        
        navigator.clipboard.writeText(code).then(() => {
            // تغییر موقت متن دکمه
            const originalHTML = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i> کپی شد!';
            button.style.background = '#4cc9f0';
            
            setTimeout(() => {
                button.innerHTML = originalHTML;
                button.style.background = '';
            }, 2000);
            
            this.showNotification('کد کپی شد!', 'success');
        });
    }
    
    setupCopyButtons() {
        // راه‌اندازی مجدد دکمه‌های کپی
        document.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const codeBlock = e.target.closest('.code-example').querySelector('code');
                const code = codeBlock.textContent;
                
                navigator.clipboard.writeText(code).then(() => {
                    const originalHTML = e.target.innerHTML;
                    e.target.innerHTML = '<i class="fas fa-check"></i> کپی شد!';
                    e.target.style.background = '#4cc9f0';
                    
                    setTimeout(() => {
                        e.target.innerHTML = originalHTML;
                        e.target.style.background = '';
                    }, 2000);
                });
            });
        });
    }
    
    // --- توابع کمکی ---
    
    showLoading() {
        document.getElementById('theory-content').innerHTML = `
            <div class="loading" style="text-align: center; padding: 40px;">
                <i class="fas fa-spinner fa-spin fa-2x"></i>
                <p style="margin-top: 15px;">در حال بارگذاری درس...</p>
            </div>
        `;
    }
    
    hideLoading() {
        // لودینگ با renderLessonContent مخفی می‌شود
    }
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            left: 20px;
            background: #f72585;
            color: white;
            padding: 15px;
            border-radius: 10px;
            z-index: 9999;
            text-align: center;
            font-family: Tahoma;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        `;
        
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        document.body.appendChild(errorDiv);
        
        setTimeout(() => errorDiv.remove(), 5000);
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            bottom: 100px;
            right: 20px;
            left: 20px;
            background: ${type === 'success' ? '#4cc9f0' : '#4361ee'};
            color: white;
            padding: 15px;
            border-radius: 10px;
            z-index: 9999;
            text-align: center;
            font-family: Tahoma;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            animation: slideUp 0.3s ease;
        `;
        
        notification.innerHTML = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// اضافه کردن استایل‌های انیمیشن
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from { transform: translateY(100px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes slideDown {
        from { transform: translateY(0); opacity: 1; }
        to { transform: translateY(100px); opacity: 0; }
    }
`;
document.head.appendChild(style);

// راه‌اندازی صفحه وقتی DOM بارگذاری شد
document.addEventListener('DOMContentLoaded', () => {
    window.lessonPage = new LessonPage();
    window.lessonPage.init();
});