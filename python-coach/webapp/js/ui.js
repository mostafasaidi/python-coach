/**
 * مدیریت رابط کاربری
 */

class UIManager {
    constructor() {
        this.modals = {};
    }
    
    showLoading(message = 'در حال بارگذاری...') {
        // ایجاد overlay لودینگ
        let overlay = document.getElementById('loading-overlay');
        
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loading-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                backdrop-filter: blur(4px);
            `;
            
            overlay.innerHTML = `
                <div style="background: white; padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
                    <div class="spinner" style="width: 50px; height: 50px; border: 5px solid #f3f3f3; border-top: 5px solid #4361ee; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
                    <p style="color: #333; font-size: 1.1rem; margin: 0;">${message}</p>
                </div>
            `;
            
            document.body.appendChild(overlay);
            
            // اضافه کردن انیمیشن
            const style = document.createElement('style');
            style.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
        
        overlay.style.display = 'flex';
    }
    
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    showModal(title, content, buttons = []) {
        const modalId = 'modal-' + Date.now();
        
        const modalHTML = `
            <div id="${modalId}" class="modal-overlay" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 10000; animation: fadeIn 0.3s ease;">
                <div class="modal-content" style="background: white; border-radius: 20px; padding: 30px; max-width: 500px; width: 90%; box-shadow: 0 20px 60px rgba(0,0,0,0.3); animation: slideUp 0.3s ease;">
                    <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3 style="margin: 0; color: #333; font-size: 1.3rem;">${title}</h3>
                        <button class="modal-close" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #666;">×</button>
                    </div>
                    <div class="modal-body" style="margin-bottom: 25px;">
                        ${content}
                    </div>
                    <div class="modal-footer" style="display: flex; justify-content: flex-end; gap: 10px;">
                        ${buttons.map(btn => `
                            <button class="modal-btn ${btn.type || 'primary'}" 
                                    style="padding: 12px 24px; border: none; border-radius: 10px; cursor: pointer; font-weight: 600; transition: all 0.2s ease;"
                                    data-action="${btn.action || ''}">
                                ${btn.text}
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        
        // اضافه کردن استایل‌ها
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            @keyframes slideUp { from { transform: translateY(30px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
            .modal-btn.primary { background: #4361ee; color: white; }
            .modal-btn.primary:hover { background: #3a0ca3; }
            .modal-btn.secondary { background: #e9ecef; color: #333; }
            .modal-btn.secondary:hover { background: #dee2e6; }
        `;
        document.head.appendChild(style);
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        const modal = document.getElementById(modalId);
        this.modals[modalId] = modal;
        
        // رویداد بستن
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn.addEventListener('click', () => this.closeModal(modalId));
        
        // رویداد دکمه‌ها
        modal.querySelectorAll('.modal-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                if (action) {
                    if (typeof window[action] === 'function') {
                        window[action]();
                    }
                }
                this.closeModal(modalId);
            });
        });
        
        // بستن با کلیک روی overlay
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal(modalId);
            }
        });
        
        return modalId;
    }
    
    closeModal(modalId) {
        const modal = this.modals[modalId];
        if (modal) {
            modal.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                modal.remove();
                delete this.modals[modalId];
            }, 300);
        }
    }
    
    showNotification(message, type = 'info', duration = 3000) {
        const notificationId = 'notification-' + Date.now();
        
        const colors = {
            info: '#4361ee',
            success: '#4cc9f0',
            warning: '#f72585',
            error: '#ff4d4d'
        };
        
        const icons = {
            info: 'ℹ️',
            success: '✅',
            warning: '⚠️',
            error: '❌'
        };
        
        const notificationHTML = `
            <div id="${notificationId}" class="notification" 
                 style="position: fixed; top: 20px; left: 20px; right: 20px; background: ${colors[type]}; color: white; padding: 15px 20px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); z-index: 9998; display: flex; align-items: center; gap: 12px; animation: slideInRight 0.3s ease;">
                <span style="font-size: 20px;">${icons[type]}</span>
                <span style="flex: 1; font-size: 0.95rem;">${message}</span>
                <button class="notification-close" style="background: none; border: none; color: white; font-size: 20px; cursor: pointer;">×</button>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', notificationHTML);
        
        const notification = document.getElementById(notificationId);
        
        // رویداد بستن
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        });
        
        // بستن خودکار
        if (duration > 0) {
            setTimeout(() => {
                if (document.getElementById(notificationId)) {
                    closeBtn.click();
                }
            }, duration);
        }
        
        // اضافه کردن انیمیشن‌ها
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOutRight {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // قابلیت کپی کد
    setupCodeCopy() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('copy-code-btn')) {
                const code = e.target.previousElementSibling?.textContent;
                if (code) {
                    navigator.clipboard.writeText(code).then(() => {
                        this.showNotification('کد کپی شد!', 'success');
                    });
                }
            }
        });
    }
}

// ایجاد نمونه global
window.uiManager = new UIManager();