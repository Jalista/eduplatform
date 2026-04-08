# ----------------------------------------------------------------------
# Merhaba! Bunu inceleyen kişiye selamlar, ben Yakup :)
# Courses models: Ders, Konu ve Kayıt modelleri
# ----------------------------------------------------------------------

from django.db import models
from django.conf import settings


class Course(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='taught_courses',
        verbose_name='Öğretmen'
    )
    title = models.CharField(max_length=200, verbose_name='Ders Adı')
    description = models.TextField(verbose_name='Açıklama')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    def __str__(self):
        return self.title

    def get_enrolled_count(self):
        return self.enrollments.filter(is_active=True).count()

    class Meta:
        verbose_name = 'Ders'
        verbose_name_plural = 'Dersler'
        ordering = ['-created_at']


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Öğrenci'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Ders'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['student', 'course']
        verbose_name = 'Kayıt'
        verbose_name_plural = 'Kayıtlar'

    def __str__(self):
        return f"{self.student} → {self.course}"


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Ders'
    )
    title = models.CharField(max_length=200, verbose_name='Başlık')
    content = models.TextField(verbose_name='İçerik')
    order = models.PositiveIntegerField(default=0, verbose_name='Sıra')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Konu'
        verbose_name_plural = 'Konular'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"
