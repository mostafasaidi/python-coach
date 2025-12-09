"""
تولید فایل‌های PDF
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import HexColor

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_styles()
    
    def setup_styles(self):
        """تنظیم استایل‌ها"""
        # استایل عنوان
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Heading1'],
            fontSize=24,
            alignment=TA_CENTER,
            textColor=HexColor('#2E86AB'),
            spaceAfter=30
        )
        
        # استایل متن عادی
        self.normal_style = ParagraphStyle(
            'Normal',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=12
        )
        
        # استایل کد
        self.code_style = ParagraphStyle(
            'Code',
            fontName='Courier',
            fontSize=9,
            leading=11,
            leftIndent=20,
            rightIndent=20,
            backColor=HexColor('#F8F9FA'),
            borderColor=HexColor('#DEE2E6'),
            borderWidth=1,
            borderPadding=10,
            spaceBefore=8,
            spaceAfter=12
        )
        
        # استایل هشدار
        self.warning_style = ParagraphStyle(
            'Warning',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor('#C0392B'),
            alignment=TA_CENTER,
            backColor=HexColor('#FDEDEC'),
            borderColor=HexColor('#F5B7B1'),
            borderWidth=1,
            borderPadding=15,
            spaceBefore=20,
            spaceAfter=30
        )
    
    def create_lesson_pdf(self, lesson_data, output_path, include_answers=False):
        """ایجاد PDF درس"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # صفحه اول
        story.append(Paragraph(f"درس روز {lesson_data['day']}", self.title_style))
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"موضوع: {lesson_data['topic']}", self.normal_style))
        story.append(PageBreak())
        
        # اهداف
        story.append(Paragraph("🎯 اهداف یادگیری", self.styles['Heading2']))
        for goal in lesson_data.get('goals', []):
            story.append(Paragraph(f"• {goal}", self.normal_style))
        story.append(Spacer(1, 20))
        
        # مفاهیم
        story.append(Paragraph("📚 مفاهیم اصلی", self.styles['Heading2']))
        story.append(Paragraph(lesson_data.get('concepts', ''), self.normal_style))
        story.append(Spacer(1, 20))
        
        # مثال‌ها
        story.append(Paragraph("👨‍💻 مثال‌ها", self.styles['Heading2']))
        for example in lesson_data.get('examples', []):
            if 'code' in example:
                code_block = Preformatted(example['code'], self.code_style)
                story.append(code_block)
                story.append(Spacer(1, 10))
        
        # تمرینات
        story.append(Paragraph("💪 تمرینات", self.styles['Heading2']))
        
        if not include_answers:
            story.append(Paragraph("پاسخ‌ها در فایل جداگانه ارائه می‌شوند.", self.warning_style))
        
        for exercise in lesson_data.get('exercises', []):
            story.append(Paragraph(exercise.get('title', ''), self.styles['Heading3']))
            story.append(Paragraph(exercise.get('description', ''), self.normal_style))
            
            if include_answers and 'solution' in exercise:
                story.append(Paragraph("پاسخ:", self.normal_style))
                code_block = Preformatted(exercise['solution'], self.code_style)
                story.append(code_block)
            
            story.append(Spacer(1, 15))
        
        # ساخت PDF
        doc.build(story)
        return output_path

class LessonPDFGenerator(PDFGenerator):
    """مولد PDF درس (بدون پاسخ)"""
    pass

class AnswersPDFGenerator(PDFGenerator):
    """مولد PDF پاسخ‌نامه"""
    
    def create_answers_pdf(self, lesson_data, output_path):
        """ایجاد PDF پاسخ‌نامه"""
        return self.create_lesson_pdf(lesson_data, output_path, include_answers=True)

# ایجاد instances
lesson_pdf_generator = LessonPDFGenerator()
answers_pdf_generator = AnswersPDFGenerator()