from django.contrib import admin
from .models import Course, Enrollment, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'get_enrolled_count', 'created_at', 'is_active']
    list_filter = ['is_active', 'teacher']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'is_active']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'created_at']
