# ----------------------------------------------------------------------
# Merhaba! Bunu inceleyen kişiye selamlar, ben Yakup :)
# Views: Quiz oluşturma, soru yönetimi, test çözme, sonuç görüntüleme
# Özellikler: Süre sınırlı quiz, otomatik teslim, geçmiş sonuçlar
# ----------------------------------------------------------------------

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.http import JsonResponse
from courses.models import Enrollment
from .models import Quiz, Question, Choice, QuizAttempt, StudentAnswer
from .forms import QuizForm, QuestionForm, ChoiceFormSet


def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        if not request.user.is_teacher():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        if not request.user.is_student():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def _check_student_enrolled(student, course):
    if not Enrollment.objects.filter(student=student, course=course, is_active=True).exists():
        raise PermissionDenied


def _process_attempt(request, quiz, timed_out=False):
    """Ortak quiz teslim mantığı — hem normal hem otomatik teslimde kullanılır."""
    questions = quiz.questions.prefetch_related('choices').all()
    attempt = QuizAttempt.objects.create(
        student=request.user,
        quiz=quiz,
        total_questions=questions.count(),
        timed_out=timed_out,
    )
    correct_count = 0
    answers_data = []

    for question in questions:
        choice_id = request.POST.get(f'question_{question.pk}')
        selected_choice = None
        is_correct = False

        if choice_id:
            try:
                selected_choice = Choice.objects.get(pk=choice_id, question=question)
                is_correct = selected_choice.is_correct
                if is_correct:
                    correct_count += 1
            except Choice.DoesNotExist:
                pass

        answers_data.append(StudentAnswer(
            attempt=attempt,
            question=question,
            selected_choice=selected_choice,
            is_correct=is_correct,
        ))

    StudentAnswer.objects.bulk_create(answers_data)
    attempt.correct_answers = correct_count
    attempt.score = round((correct_count / questions.count()) * 100, 1) if questions.count() > 0 else 0
    attempt.completed_at = timezone.now()
    attempt.save()
    return attempt


# ── TEACHER VIEWS ─────────────────────────────────────────────────────

@teacher_required
def create_quiz(request, course_pk):
    from courses.models import Course
    course = get_object_or_404(Course, pk=course_pk, teacher=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.save()
            messages.success(request, 'Test oluşturuldu. Şimdi sorular ekleyebilirsiniz.')
            return redirect('quizzes:detail', pk=quiz.pk)
    else:
        form = QuizForm()
    return render(request, 'quizzes/quiz_form.html', {'form': form, 'course': course, 'title': 'Yeni Test Oluştur'})


@teacher_required
def edit_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, course__teacher=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Test güncellendi.')
            return redirect('quizzes:detail', pk=quiz.pk)
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'quizzes/quiz_form.html', {'form': form, 'course': quiz.course, 'title': 'Testi Düzenle', 'quiz': quiz})


@teacher_required
def delete_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, course__teacher=request.user)
    course_pk = quiz.course.pk
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Test silindi.')
        return redirect('courses:detail', pk=course_pk)
    return render(request, 'quizzes/confirm_delete.html', {'object': quiz, 'type': 'test'})


@teacher_required
def add_question(request, quiz_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, course__teacher=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            choices = formset.save(commit=False)
            for choice in choices:
                choice.question = question
                choice.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, 'Soru eklendi.')
            return redirect('quizzes:detail', pk=quiz.pk)
    else:
        form = QuestionForm(initial={'order': quiz.questions.count() + 1})
        formset = ChoiceFormSet()
    return render(request, 'quizzes/question_form.html', {
        'form': form, 'formset': formset, 'quiz': quiz, 'title': 'Soru Ekle',
    })


@teacher_required
def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk, quiz__course__teacher=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = ChoiceFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            form.save()
            choices = formset.save(commit=False)
            for choice in choices:
                choice.question = question
                choice.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, 'Soru güncellendi.')
            return redirect('quizzes:detail', pk=question.quiz.pk)
    else:
        form = QuestionForm(instance=question)
        formset = ChoiceFormSet(instance=question)
    return render(request, 'quizzes/question_form.html', {
        'form': form, 'formset': formset, 'quiz': question.quiz, 'title': 'Soruyu Düzenle',
    })


@teacher_required
def delete_question(request, pk):
    question = get_object_or_404(Question, pk=pk, quiz__course__teacher=request.user)
    quiz_pk = question.quiz.pk
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Soru silindi.')
        return redirect('quizzes:detail', pk=quiz_pk)
    return render(request, 'quizzes/confirm_delete.html', {'object': question, 'type': 'soru'})


@teacher_required
def quiz_results_overview(request, pk):
    """Öğretmen: tüm öğrenci sonuçlarını tek sayfada görür."""
    quiz = get_object_or_404(Quiz, pk=pk, course__teacher=request.user)
    attempts = (
        quiz.attempts
        .select_related('student')
        .filter(completed_at__isnull=False)
        .order_by('-started_at')
    )
    return render(request, 'quizzes/results_overview.html', {
        'quiz': quiz,
        'attempts': attempts,
    })


# ── SHARED VIEW ───────────────────────────────────────────────────────

@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    user = request.user

    if user.is_teacher():
        if quiz.course.teacher != user:
            raise PermissionDenied
        questions = quiz.questions.prefetch_related('choices').all()
        attempts = (
            quiz.attempts
            .select_related('student')
            .filter(completed_at__isnull=False)
            .order_by('-started_at')
        )
        return render(request, 'quizzes/quiz_detail_teacher.html', {
            'quiz': quiz,
            'questions': questions,
            'attempts': attempts,
        })
    else:
        _check_student_enrolled(user, quiz.course)
        questions = quiz.questions.prefetch_related('choices').all()
        past_attempts = (
            QuizAttempt.objects
            .filter(student=user, quiz=quiz, completed_at__isnull=False)
            .order_by('-started_at')
        )
        return render(request, 'quizzes/quiz_detail_student.html', {
            'quiz': quiz,
            'questions': questions,
            'past_attempts': past_attempts,
        })


# ── STUDENT VIEWS ─────────────────────────────────────────────────────

@student_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_active=True)
    _check_student_enrolled(request.user, quiz.course)
    questions = quiz.questions.prefetch_related('choices').all()

    if not questions.exists():
        messages.warning(request, 'Bu testte henüz soru bulunmuyor.')
        return redirect('quizzes:detail', pk=quiz.pk)

    if request.method == 'POST':
        timed_out = request.POST.get('timed_out') == '1'
        attempt = _process_attempt(request, quiz, timed_out=timed_out)
        if timed_out:
            messages.warning(request, '⏰ Süre doldu! Test otomatik olarak teslim edildi.')
        return redirect('quizzes:result', pk=attempt.pk)

    # Süreyi saniye cinsinden JS'e gönder (0 = süresiz)
    time_limit_seconds = quiz.time_limit_minutes * 60 if quiz.time_limit_minutes else 0
    return render(request, 'quizzes/take_quiz.html', {
        'quiz': quiz,
        'questions': questions,
        'time_limit_seconds': time_limit_seconds,
    })


@student_required
def quiz_result(request, pk):
    attempt = get_object_or_404(QuizAttempt, pk=pk, student=request.user)
    answers = attempt.answers.select_related(
        'question', 'selected_choice'
    ).prefetch_related('question__choices').all()
    return render(request, 'quizzes/quiz_result.html', {
        'attempt': attempt,
        'answers': answers,
    })


@student_required
def my_results(request):
    """Öğrenci kendi tüm quiz geçmişini görür."""
    attempts = (
        QuizAttempt.objects
        .filter(student=request.user, completed_at__isnull=False)
        .select_related('quiz', 'quiz__course')
        .order_by('-started_at')
    )
    return render(request, 'quizzes/my_results.html', {'attempts': attempts})


@teacher_required
def quiz_attempt_detail(request, pk):
    attempt = get_object_or_404(QuizAttempt, pk=pk, quiz__course__teacher=request.user)
    answers = attempt.answers.select_related(
        'question', 'selected_choice'
    ).prefetch_related('question__choices').all()
    return render(request, 'quizzes/quiz_result.html', {
        'attempt': attempt,
        'answers': answers,
        'is_teacher_view': True,
    })
