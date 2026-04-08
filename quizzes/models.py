from django.db import models
from django.conf import settings
from django.utils import timezone
from courses.models import Course

# ----------------------------------------------------------------------
# Merhaba! Bunu inceleyen kişiye selamlar, ben Yakup :)
# Bu proje Django ile yazılmış çok kullanıcılı bir eğitim platformudur.
# Öğretmen/öğrenci rolleri, ders yönetimi, süreli quiz sistemi içerir.
# ----------------------------------------------------------------------


class Quiz(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name='Ders'
    )
    title = models.CharField(max_length=200, verbose_name='Test Adı')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    time_limit_minutes = models.PositiveIntegerField(
        default=10,
        verbose_name='Süre (dakika)',
        help_text='0 girilirse süre sınırı uygulanmaz.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def get_question_count(self):
        return self.questions.count()

    class Meta:
        verbose_name = 'Test'
        verbose_name_plural = 'Testler'
        ordering = ['-created_at']


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Test'
    )
    text = models.TextField(verbose_name='Soru')
    order = models.PositiveIntegerField(default=0, verbose_name='Sıra')

    def __str__(self):
        return f"Soru {self.order}: {self.text[:60]}"

    class Meta:
        verbose_name = 'Soru'
        verbose_name_plural = 'Sorular'
        ordering = ['order']


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name='Soru'
    )
    text = models.CharField(max_length=300, verbose_name='Şık')
    is_correct = models.BooleanField(default=False, verbose_name='Doğru mu?')

    def __str__(self):
        return f"{'✓' if self.is_correct else '✗'} {self.text[:60]}"

    class Meta:
        verbose_name = 'Şık'
        verbose_name_plural = 'Şıklar'


class QuizAttempt(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name='Öğrenci'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Test'
    )
    score = models.FloatField(default=0, verbose_name='Puan')
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    started_at = models.DateTimeField(default=timezone.now, verbose_name='Başlangıç')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Bitiş')
    timed_out = models.BooleanField(default=False, verbose_name='Süre Doldu')

    def get_percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.correct_answers / self.total_questions) * 100, 1)

    def get_duration_seconds(self):
        if self.completed_at and self.started_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return None

    def __str__(self):
        return f"{self.student} - {self.quiz.title} (%{self.get_percentage()})"

    class Meta:
        verbose_name = 'Test Girişimi'
        verbose_name_plural = 'Test Girişimleri'
        ordering = ['-started_at']


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Girişim'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='Soru'
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Seçilen Şık'
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Öğrenci Cevabı'
        verbose_name_plural = 'Öğrenci Cevapları'
