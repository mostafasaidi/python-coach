/**
 * برنامه اصلی پایتون کوچ
 */

console.log('🚀 Python Coach App starting...');

// وقتی صفحه کامل لود شد
document.addEventListener('DOMContentLoaded', async function() {
    console.log('✅ DOM loaded');
    
    try {
        // ۱. چک کردن تلگرام Web App
        if (!window.Telegram || !window.Telegram.WebApp) {
            console.warn('⚠️ Telegram Web App not detected, running in browser mode');
            showWarning('حالت آزمایشی: برای تجربه کامل از طریق تلگرام وارد شوید');
        } else {
            // راه‌اندازی تلگرام Web App
            const tg = window.Telegram.WebApp;
            tg.expand();
            
            // نمایش اطلاعات کاربر
            const user = tg.initDataUnsafe?.user;
            if (user) {
                updateUserInfo(user);
            }
            
            console.log('📱 Telegram Web App initialized');
        }
        
        // ۲. بارگذاری فصول آموزشی
        await loadChapters();
        
        // ۳. مخفی کردن لودینگ
        hideLoading();
        
        // ۴. راه‌اندازی رویدادها
        setupEventListeners();
        
        console.log('✅ App started successfully');
        
    } catch (error) {
        console.error('❌ App initialization error:', error);
        showError('خطا در راه‌اندازی برنامه');
        showFallbackChapters();
    }
});

// --- توابع اصلی ---

async function loadChapters() {
    console.log('📚 Loading chapters from API...');
    
    const chaptersGrid = document.getElementById('chapters-grid');
    if (!chaptersGrid) {
        console.error('❌ Element #chapters-grid not found');
        return;
    }
    
    try {
        // درخواست از API
        const response = await fetch('/api/chapters');
        
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }
        
        const chapters = await response.json();
        console.log(`✅ Received ${chapters.length} chapters`);
        
        // نمایش فصول
        renderChapters(chapters);
        
    } catch (error) {
        console.warn('⚠️ API error, using fallback data:', error);
        showFallbackChapters();
    }
}

function renderChapters(chapters) {
    const chaptersGrid = document.getElementById('chapters-grid');
    if (!chaptersGrid) return;
    
    // مخفی کردن لودینگ
    const loading = chaptersGrid.querySelector('.loading');
    if (loading) {
        loading.style.display = 'none';
    }
    
    // پاک کردن و ایجاد کارت‌های جدید
    chaptersGrid.innerHTML = '';
    
    chapters.forEach(chapter => {
        const card = createChapterCard(chapter);
        chaptersGrid.appendChild(card);
    });
}

function createChapterCard(chapter) {
    const card = document.createElement('div');
    card.className = 'chapter-card';
    card.dataset.chapterId = chapter.id;
    
    // محتوای کارت
    card.innerHTML = `
        <div class="chapter-header">
            <div class="chapter-icon">${chapter.icon || '📚'}</div>
            <div class="chapter-title">${chapter.title}</div>
        </div>
        
        <p class="chapter-description">
            ${chapter.description}
        </p>
        
        <div class="progress-container">
            <div class="progress-info">
                <span>پیشرفت</span>
                <span>0%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 0%"></div>
            </div>
        </div>
        
        <div class="chapter-meta">
            <div class="meta-item">
                <i class="fas fa-book-open"></i>
                <span class="meta-label">درس‌ها</span>
                <span class="meta-value">${chapter.lessons}</span>
            </div>
            <div class="meta-item">
                <i class="fas fa-clock"></i>
                <span class="meta-label">مدت</span>
                <span class="meta-value">${chapter.duration}</span>
            </div>
            <div class="meta-item">
                <i class="fas fa-signal"></i>
                <span class="meta-label">سطح</span>
                <span class="meta-value">${chapter.difficulty}</span>
            </div>
        </div>
        
        <button class="start-chapter-btn">
            شروع یادگیری
        </button>
    `;
    
    // رویداد کلیک
    card.addEventListener('click', (e) => {
        if (!e.target.classList.contains('start-chapter-btn')) {
            openChapter(chapter.id);
        }
    });
    
    const startBtn = card.querySelector('.start-chapter-btn');
    startBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        openChapter(chapter.id);
    });
    
    return card;
}

function showFallbackChapters() {
    console.log('🔄 Showing fallback chapters');
    
    const fallbackChapters = [
        {
            id: 1,
            title: "شروع با پایتون",
            description: "نصب، متغیرها، انواع داده",
            lessons: 5,
            duration: "۴ ساعت",
            difficulty: "مبتدی",
            icon: "🚀"
        },
        {
            id: 2,
            title: "کنترل جریان",
            description: "شرط‌ها، حلقه for و while",
            lessons: 5,
            duration: "۳ ساعت",
            difficulty: "مبتدی",
            icon: "🔄"
        },
        {
            id: 3,
            title: "توابع و ماژول‌ها",
            description: "تعریف توابع، import ماژول‌ها",
            lessons: 5,
            duration: "۳ ساعت",
            difficulty: "مبتدی",
            icon: "⚙️"
        },
        {
            id: 4,
            title: "کار با فایل",
            description: "خواندن/نوشتن فایل، مدیریت خطا",
            lessons: 5,
            duration: "۴ ساعت",
            difficulty: "متوسط",
            icon: "📁"
        }
    ];
    
    renderChapters(fallbackChapters);
}

function updateUserInfo(user) {
    const userNameElement = document.getElementById('user-name');
    const welcomeTitle = document.getElementById('welcome-title');
    
    if (userNameElement) {
        userNameElement.textContent = `سلام ${user.first_name}!`;
    }
    
    if (welcomeTitle) {
        welcomeTitle.textContent = `سلام ${user.first_name} 👋`;
    }
}

function hideLoading() {
    document.querySelectorAll('.loading').forEach(el => {
        el.style.display = 'none';
    });
}

function setupEventListeners() {
    // دکمه ادامه یادگیری
    const continueBtn = document.getElementById('continue-learning');
    if (continueBtn) {
        continueBtn.addEventListener('click', () => {
            openChapter(1); // به فصل ۱ برو
        });
    }
    
    // دکمه ویرایشگر کد
    const editorBtn = document.getElementById('open-editor');
    if (editorBtn) {
        editorBtn.addEventListener('click', () => {
            alert('ویرایشگر کد به زودی اضافه می‌شود');
        });
    }
}

function openChapter(chapterId) {
    console.log(`🎯 Opening chapter ${chapterId}`);
    window.location.href = `/chapter/${chapterId}`;
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
        font-family: Tahoma;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    `;
    
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => errorDiv.remove(), 5000);
}

function showWarning(message) {
    const warningDiv = document.createElement('div');
    warningDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        left: 20px;
        background: #ff9800;
        color: white;
        padding: 12px;
        border-radius: 8px;
        z-index: 9998;
        text-align: center;
        font-size: 0.9rem;
    `;
    
    warningDiv.innerHTML = `⚠️ ${message}`;
    document.body.appendChild(warningDiv);
    
    setTimeout(() => warningDiv.remove(), 3000);
}

// توابع global برای استفاده در HTML
window.openChapter = openChapter;