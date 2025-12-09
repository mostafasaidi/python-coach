/**
 * مدیریت فصول و درس‌ها
 */

class ChapterManager {
    constructor() {
        this.currentChapter = null;
        this.chapters = [];
    }
    
    async loadChapter(chapterId) {
        try {
            const response = await fetch(`/api/lesson/${chapterId}/1`);
            if (!response.ok) throw new Error('فصل یافت نشد');
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error loading chapter:', error);
            return null;
        }
    }
    
    async loadLesson(chapterId, lessonId) {
        try {
            const response = await fetch(`/api/lesson/${chapterId}/${lessonId}`);
            if (!response.ok) throw new Error('درس یافت نشد');
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error loading lesson:', error);
            return null;
        }
    }
    
    async enhanceLesson(chapterId, lessonId, topic) {
        try {
            const response = await fetch('/api/enhance', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    chapter_id: chapterId,
                    lesson_id: lessonId,
                    topic: topic
                })
            });
            
            if (!response.ok) throw new Error('خطا در دریافت محتوای تکمیلی');
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error enhancing lesson:', error);
            throw error;
        }
    }
    
    // تولید prompt برای DeepSeek
    generateLessonPrompt(chapterTitle, lessonTitle) {
        return `به عنوان استاد پایتون، یک درس کامل درباره "${lessonTitle}" از فصل "${chapterTitle}" بنویس.

نیازمندی‌ها:
۱. توضیح تئوری به فارسی روان و ساده
۲. حداقل ۳ مثال کد قابل اجرا
۳. ۲ تمرین با سطح آسان و ۲ تمرین با سطح متوسط
۴. راه‌حل کامل برای همه تمرین‌ها
۵. نکات کلیدی و بهترین روش‌ها
۶. کاربرد عملی در پروژه‌های واقعی

فرمت خروجی را به صورت JSON ارائه دهید با فیلدهای:
- title: عنوان درس
- content: محتوای تئوری
- examples: آرایه‌ای از مثال‌های کد
- exercises: آرایه‌ای از تمرین‌ها با فیلدهای question, hint, solution, difficulty
- key_points: آرایه‌ای از نکات کلیدی
- practical_applications: کاربردهای عملی`;
    }
}

// ایجاد نمونه global
window.chapterManager = new ChapterManager();