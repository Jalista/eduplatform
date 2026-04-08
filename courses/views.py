# ----------------------------------------------------------------------
# Merhaba! Bunu inceleyen kişiye selamlar, ben Yakup :)
# Courses views: ders oluşturma, konu yönetimi, öğrenci kayıt sistemi
# ----------------------------------------------------------------------

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Course, Enrollment, Lesson
from .forms import CourseForm, LessonForm


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


@login_required
def dashboard(request):
    user = request.user
    if user.is_teacher():
        courses = Course.objects.filter(teacher=user)
        context = {'courses': courses, 'is_teacher': True}
    else:
        enrollments = Enrollment.objects.filter(student=user, is_active=True).select_related('course')
        available_courses = Course.objects.filter(is_active=True).exclude(
            id__in=enrollments.values_list('course_id', flat=True)
        ).exclude(teacher=user)
        context = {
            'enrollments': enrollments,
            'available_courses': available_courses,
            'is_teacher': False,
        }
    return render(request, 'courses/dashboard.html', context)


@teacher_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, 'Ders oluşturuldu.')
            return redirect('courses:detail', pk=course.pk)
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Yeni Ders Oluştur'})


@teacher_required
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ders güncellendi.')
            return redirect('courses:detail', pk=course.pk)
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Dersi Düzenle', 'course': course})


@teacher_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Ders silindi.')
        return redirect('courses:dashboard')
    return render(request, 'courses/confirm_delete.html', {'object': course, 'type': 'ders'})


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    user = request.user

    if user.is_teacher():
        if course.teacher != user:
            raise PermissionDenied
        lessons = course.lessons.all()
        quizzes = course.quizzes.all()
        enrollments = course.enrollments.filter(is_active=True).select_related('student')
        return render(request, 'courses/course_detail_teacher.html', {
            'course': course,
            'lessons': lessons,
            'quizzes': quizzes,
            'enrollments': enrollments,
        })
    else:
        # student
        is_enrolled = Enrollment.objects.filter(student=user, course=course, is_active=True).exists()
        if not is_enrolled:
            messages.warning(request, 'Bu derse kayıtlı değilsiniz.')
            return redirect('courses:dashboard')
        lessons = course.lessons.all()
        quizzes = course.quizzes.all()
        return render(request, 'courses/course_detail_student.html', {
            'course': course,
            'lessons': lessons,
            'quizzes': quizzes,
        })


@student_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk, is_active=True)
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'is_active': True}
    )
    if created:
        messages.success(request, f'"{course.title}" dersine kayıt oldunuz!')
    else:
        enrollment.is_active = True
        enrollment.save()
        messages.info(request, 'Zaten bu derse kayıtlısınız.')
    return redirect('courses:detail', pk=course.pk)


@student_required
def unenroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, f'"{course.title}" dersinden ayrıldınız.')
        return redirect('courses:dashboard')
    return render(request, 'courses/confirm_delete.html', {'object': course, 'type': 'ders kaydı'})


@teacher_required
def add_lesson(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, teacher=request.user)
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, 'Konu eklendi.')
            return redirect('courses:detail', pk=course.pk)
    else:
        form = LessonForm()
    return render(request, 'courses/lesson_form.html', {'form': form, 'course': course, 'title': 'Konu Ekle'})


@teacher_required
def edit_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk, course__teacher=request.user)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Konu güncellendi.')
            return redirect('courses:detail', pk=lesson.course.pk)
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'courses/lesson_form.html', {'form': form, 'course': lesson.course, 'title': 'Konuyu Düzenle'})


@teacher_required
def delete_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk, course__teacher=request.user)
    course_pk = lesson.course.pk
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Konu silindi.')
        return redirect('courses:detail', pk=course_pk)
    return render(request, 'courses/confirm_delete.html', {'object': lesson, 'type': 'konu'})


@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    user = request.user
    if user.is_student():
        if not Enrollment.objects.filter(student=user, course=lesson.course, is_active=True).exists():
            raise PermissionDenied
    elif user.is_teacher():
        if lesson.course.teacher != user:
            raise PermissionDenied
    return render(request, 'courses/lesson_detail.html', {'lesson': lesson})
