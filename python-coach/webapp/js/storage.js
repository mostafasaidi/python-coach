/**
 * مدیریت ذخیره‌سازی محلی
 */

class StorageManager {
    constructor() {
        this.prefix = 'python_coach_';
    }
    
    set(key, value) {
        try {
            const serialized = JSON.stringify(value);
            localStorage.setItem(this.prefix + key, serialized);
            return true;
        } catch (error) {
            console.error('Error saving to localStorage:', error);
            return false;
        }
    }
    
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(this.prefix + key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return defaultValue;
        }
    }
    
    remove(key) {
        localStorage.removeItem(this.prefix + key);
    }
    
    clear() {
        // فقط آیتم‌های مربوط به برنامه ما را پاک می‌کند
        Object.keys(localStorage).forEach(key => {
            if (key.startsWith(this.prefix)) {
                localStorage.removeItem(key);
            }
        });
    }
    
    // متدهای مخصوص برنامه
    saveProgress(progress) {
        return this.set('progress', progress);
    }
    
    getProgress() {
        return this.get('progress', {
            completedChapters: [],
            completedLessons: [],
            totalProgress: 0,
            lastActivity: null
        });
    }
    
    saveCompletedLesson(chapterId, lessonId) {
        const progress = this.getProgress();
        const lessonKey = `${chapterId}.${lessonId}`;
        
        if (!progress.completedLessons.includes(lessonKey)) {
            progress.completedLessons.push(lessonKey);
            
            // اضافه کردن فصل اگر تمام درس‌های آن تکمیل شده باشد
            const chapterLessons = progress.completedLessons.filter(l => l.startsWith(`${chapterId}.`));
            if (chapterLessons.length >= 5) { // فرض: ۵ درس در هر فصل
                if (!progress.completedChapters.includes(chapterId)) {
                    progress.completedChapters.push(chapterId);
                }
            }
            
            // محاسبه پیشرفت کلی
            progress.totalProgress = Math.min(100, Math.round((progress.completedLessons.length / 80) * 100));
            progress.lastActivity = new Date().toISOString();
            
            this.saveProgress(progress);
            return true;
        }
        
        return false;
    }
    
    getCompletedLessons(chapterId = null) {
        const progress = this.getProgress();
        if (chapterId) {
            return progress.completedLessons.filter(lesson => lesson.startsWith(`${chapterId}.`));
        }
        return progress.completedLessons;
    }
    
    getLastActivity() {
        const progress = this.getProgress();
        return progress.lastActivity;
    }
}

// ایجاد نمونه global
window.storageManager = new StorageManager();