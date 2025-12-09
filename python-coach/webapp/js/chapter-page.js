/**
 * مدیریت صفحه فصل - نسخه ساده
 */

console.log('📖 Chapter page loaded');

// وقتی صفحه لود شد
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM ready');
    
    try {
        // ۱. دریافت شماره فصل از URL
        const chapterId = getChapterIdFromURL();
        console.log('🎯 Chapter ID:', chapterId);
        
        if (!chapterId) {
            showError('فصل یافت نشد!');
            setTimeout(() => window.location.href = '/', 2000);
            return;
        }
        
        // ۲. بارگذاری اطلاعات فصل
        loadChapterData(chapterId);
        
        // ۳. راه‌اندازی رویدادها
        setupEventListeners(chapterId);
        
        // ۴. بارگذاری درس‌ها
        loadLessons(chapterId);
        
    } catch (error) {
        console.error('❌ Error:', error);
        showError('خطا در بارگذاری صفحه');
        showFallbackData();
    }
});

// --- توابع اصلی ---

function getChapterIdFromURL() {
    const path = window.location.pathname;
    const match = path.match(/\/chapter\/(\d+)/);
    return match ? parseInt(match[1]) : null;
}

async function loadChapterData(chapterId) {
    console.log('📚 Loading chapter data...');
    
    try {
        // درخواست از API
        const response = await fetch('/api/chapters');
        const chapters = await response.json();
        
        // پیدا کردن فصل مورد نظر
        const chapter = chapters.find(ch => ch.id === chapterId);
        
        if (chapter) {
            updateChapterUI(chapter);
        } else {
            showFallbackChapter(chapterId);
        }
        
    } catch (error) {
        console.warn('⚠️ API error, using fallback:', error);
        showFallbackChapter(chapterId);
    }
}

function updateChapterUI(chapter) {
    console.log('🎨 Updating UI with:', chapter);
    
    // به‌روزرسانی عنوان
    document.getElementById('chapter-title').textContent = chapter.title;
    document.getElementById('chapter-description').textContent = chapter.description;
    
    // به‌روزرسانی متادیتا
    document.getElementById('chapter-duration').textContent = chapter.duration || '۴ ساعت';
    document.getElementById('chapter-difficulty').textContent = chapter.difficulty || 'مبتدی';
    
    // محاسبه پیشرفت (در آینده از localStorage بخوان)
    const progressPercent = 0; // فعلاً صفر
    
    // به‌روزرسانی آمار
    document.getElementById('completed-lessons').textContent = '0';
    document.getElementById('total-lessons').textContent = chapter.lessons || '5';
    document.getElementById('progress-percent').textContent = `${progressPercent}%`;
    document.getElementById('chapter-status').textContent = 'شروع نشده';
    
    // به‌روزرسانی دایره پیشرفت
    updateProgressCircle(progressPercent);
}

function updateProgressCircle(percent) {
    const circle = document.getElementById('progress-circle');
    if (circle) {
        const circumference = 2 * Math.PI * 27;
        const offset = circumference - (percent / 100) * circumference;
        circle.style.strokeDashoffset = offset;
    }
}

async function loadLessons(chapterId) {
    console.log('📝 Loading lessons for chapter', chapterId);
    
    const lessonsList = document.getElementById('lessons-list');
    if (!lessonsList) {
        console.error('❌ lessons-list element not found');
        return;
    }
    
    // مخفی کردن لودینگ
    const loading = lessonsList.querySelector('.loading');
    if (loading) {
        loading.style.display = 'none';
    }
    
    // ایجاد ۵ درس نمونه
    const lessons = [];
    for (let i = 1; i <= 5; i++) {
        lessons.push({
            id: i,
            title: `درس ${i}: ${getLessonTitle(i)}`,
            description: 'آموزش مفاهیم اصلی این فصل',
            status: i === 1 ? 'unlocked' : 'locked', // فقط درس اول باز است
            duration: '۳۰ دقیقه',
            difficulty: getLessonDifficulty(i)
        });
    }
    
    // نمایش درس‌ها
    renderLessons(lessons, chapterId);
}

function getLessonTitle(lessonNumber) {
    const titles = {
        1: 'مقدمه و آشنایی',
        2: 'مفاهیم اصلی',
        3: 'تمرین‌های عملی',
        4: 'پروژه کوچک',
        5: 'جمع‌بندی و آزمون'
    };
    return titles[lessonNumber] || 'مفاهیم پایه';
}

function getLessonDifficulty(lessonNumber) {
    if (lessonNumber <= 2) return 'آسان';
    if (lessonNumber === 3) return 'متوسط';
    return 'پیشرفته';
}

function renderLessons(lessons, chapterId) {
    const lessonsList = document.getElementById('lessons-list');
    if (!lessonsList) return;
    
    lessonsList.innerHTML = '';
    
    lessons.forEach(lesson => {
        const lessonItem = createLessonItem(lesson, chapterId);
        lessonsList.appendChild(lessonItem);
    });
}

function createLessonItem(lesson, chapterId) {
    const div = document.createElement('div');
    div.className = 'lesson-item';
    
    // تعیین وضعیت
    let iconClass, statusText, statusClass, iconName;
    
    switch (lesson.status) {
        case 'locked':
            iconClass = 'locked';
            statusText = 'قفل شده';
            statusClass = 'status-locked';
            iconName = 'lock';
            break;
        case 'unlocked':
            iconClass = 'unlocked';
            statusText = 'باز است';
            statusClass = 'status-unlocked';
            iconName = 'book-open';
            break;
        case 'completed':
            iconClass = 'completed';
            statusText = 'تکمیل شده';
            statusClass = 'status-completed';
            iconName = 'check-circle';
            break;
    }
    
    div.innerHTML = `
        <div class="lesson-icon ${iconClass}">
            <i class="fas fa-${iconName}"></i>
        </div>
        <div class="lesson-details">
            <div class="lesson-title">${lesson.title}</div>
            <div class="lesson-description">${lesson.description}</div>
            <div class="lesson-meta">
                <span><i class="fas fa-clock"></i> ${lesson.duration}</span>
                <span><i class="fas fa-signal"></i> ${lesson.difficulty}</span>
            </div>
        </div>
        <div class="lesson-status ${statusClass}">${statusText}</div>
    `;
    
    // اگر درس قفل نشده باشد، کلیک پذیر است
    if (lesson.status !== 'locked') {
        div.style.cursor = 'pointer';
        div.addEventListener('click', () => {
            openLesson(chapterId, lesson.id);
        });
    } else {
        div.style.opacity = '0.7';
    }
    
    return div;
}

function setupEventListeners(chapterId) {
    // دکمه بازگشت
    const backBtn = document.getElementById('back-btn');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            window.history.back();
        });
    }
    
    // دکمه شروع یادگیری
    const startBtn = document.getElementById('start-learning');
    if (startBtn) {
        startBtn.addEventListener('click', () => {
            openLesson(chapterId, 1); // شروع از درس ۱
        });
    }
    
    // دکمه‌های محتوای تکمیلی
    document.getElementById('ask-deepseek')?.addEventListener('click', () => {
        askDeepSeek(chapterId);
    });
    
    document.getElementById('get-examples')?.addEventListener('click', () => {
        showNotification('این قابلیت به زودی اضافه می‌شود', 'info');
    });
    
    document.getElementById('practice-projects')?.addEventListener('click', () => {
        showNotification('پروژه‌های عملی به زودی اضافه می‌شوند', 'info');
    });
}

function openLesson(chapterId, lessonId) {
    console.log(`🎯 Opening lesson ${chapterId}.${lessonId}`);
    window.location.href = `/lesson/${chapterId}/${lessonId}`;
}

function askDeepSeek(chapterId) {
    console.log('🤖 Asking DeepSeek...');
    
    showNotification('در حال درخواست از DeepSeek...', 'info');
    
    // شبیه‌سازی درخواست
    setTimeout(() => {
        showNotification('محتوای تکمیلی تولید شد!', 'success');
        
        // نمایش محتوای نمونه
        const modalHTML = `
            <div style="padding: 20px; max-width: 500px;">
                <h3 style="color: #4361ee; margin-bottom: 15px;">🎯 نکات تکمیلی از DeepSeek</h3>
                <p style="line-height: 1.6; margin-bottom: 15px;">
                    برای این فصل، DeepSeek نکات زیر را پیشنهاد می‌دهد:
                </p>
                <ul style="padding-right: 20px; margin-bottom: 20px;">
                    <li>مفاهیم را قدم‌به‌قدم یاد بگیرید</li>
                    <li>همراه با درس کد بزنید</li>
                    <li>تمرین‌ها را حتماً انجام دهید</li>
                    <li>در صورت مشکل، سوال بپرسید</li>
                </ul>
                <button onclick="this.closest('.modal').remove()" 
                        style="width: 100%; padding: 12px; background: #4361ee; color: white; border: none; border-radius: 8px; cursor: pointer;">
                    متوجه شدم
                </button>
            </div>
        `;
        
        showModal('🤖 پاسخ DeepSeek', modalHTML);
        
    }, 1500);
}

// --- توابع کمکی ---

function showFallbackChapter(chapterId) {
    document.getElementById('chapter-title').textContent = `فصل ${chapterId}: آموزش پایتون`;
    document.getElementById('chapter-description').textContent = 'آموزش جامع و تعاملی پایتون';
}

function showFallbackData() {
    // نمایش داده‌های پیش‌فرض
    const lessonsList = document.getElementById('lessons-list');
    if (lessonsList) {
        lessonsList.innerHTML = `
            <div class="lesson-item">
                <div class="lesson-icon unlocked">
                    <i class="fas fa-book-open"></i>
                </div>
                <div class="lesson-details">
                    <div class="lesson-title">درس ۱: شروع کار</div>
                    <div class="lesson-description">آشنایی با مفاهیم پایه</div>
                    <div class="lesson-meta">
                        <span><i class="fas fa-clock"></i> ۳۰ دقیقه</span>
                        <span><i class="fas fa-signal"></i> آسان</span>
                    </div>
                </div>
                <div class="lesson-status status-unlocked">باز است</div>
            </div>
        `;
    }
}

function showError(message) {
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
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    `;
    
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    document.body.appendChild(errorDiv);
    
    setTimeout(() => errorDiv.remove(), 5000);
}

function showNotification(message, type = 'info') {
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
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    `;
    
    notification.innerHTML = message;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 3000);
}

function showModal(title, content) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        padding: 20px;
    `;
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 15px; max-width: 500px; width: 100%; max-height: 80vh; overflow-y: auto;">
            <div style="padding: 25px;">
                <h3 style="margin-top: 0; color: #333;">${title}</h3>
                <div>${content}</div>
            </div>
        </div>
    `;
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
    
    document.body.appendChild(modal);
}

// توابع global
window.openLesson = openLesson;
window.askDeepSeek = askDeepSeek;