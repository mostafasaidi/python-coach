/**
 * مدیریت احراز هویت تلگرام
 */

class TelegramAuth {
    constructor() {
        this.tg = window.Telegram.WebApp;
        this.user = null;
        this.initParams = null;
    }
    
    init() {
        // راه‌اندازی Telegram Web App
        this.tg.expand();
        this.tg.enableClosingConfirmation();
        this.tg.setHeaderColor('#4361ee');
        this.tg.setBackgroundColor('#f8f9fa');
        
        // دریافت اطلاعات کاربر
        this.initParams = this.tg.initDataUnsafe;
        this.user = this.initParams.user || null;
        
        console.log('Telegram Web App initialized:', {
            user: this.user,
            platform: this.tg.platform,
            colorScheme: this.tg.colorScheme
        });
        
        return this.user;
    }
    
    getUser() {
        return this.user;
    }
    
    getUserInfo() {
        if (!this.user) return null;
        
        return {
            id: this.user.id,
            firstName: this.user.first_name,
            lastName: this.user.last_name || '',
            username: this.user.username || '',
            languageCode: this.user.language_code || 'fa',
            photoUrl: this.user.photo_url || null
        };
    }
    
    isAuthorized() {
        return !!this.user;
    }
    
    sendDataToBot(data) {
        try {
            if (typeof data !== 'string') {
                data = JSON.stringify(data);
            }
            this.tg.sendData(data);
            return true;
        } catch (error) {
            console.error('Error sending data to bot:', error);
            return false;
        }
    }
    
    closeApp() {
        this.tg.close();
    }
    
    showAlert(message) {
        this.tg.showAlert(message);
    }
    
    showConfirm(message, callback) {
        this.tg.showConfirm(message, callback);
    }
    
    // اعمال تم تلگرام
    applyTheme() {
        const theme = this.tg.colorScheme;
        const html = document.documentElement;
        
        if (theme === 'dark') {
            html.setAttribute('data-theme', 'dark');
            html.style.setProperty('--bg-color', '#1a1a2e');
            html.style.setProperty('--card-bg', '#16213e');
            html.style.setProperty('--text-color', '#e6e6e6');
            html.style.setProperty('--text-secondary', '#a0a0a0');
            html.style.setProperty('--border-color', '#2d4059');
        } else {
            html.setAttribute('data-theme', 'light');
            html.style.setProperty('--bg-color', '#f8f9fa');
            html.style.setProperty('--card-bg', '#ffffff');
            html.style.setProperty('--text-color', '#2b2d42');
            html.style.setProperty('--text-secondary', '#6c757d');
            html.style.setProperty('--border-color', '#e9ecef');
        }
    }
}

// ایجاد نمونه global
const telegramAuth = new TelegramAuth();

// صادر کردن برای استفاده در فایل‌های دیگر
window.TelegramAuth = telegramAuth;