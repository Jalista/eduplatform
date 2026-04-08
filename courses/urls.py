from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_course, name='create'),
    path('<int:pk>/', views.course_detail, name='detail'),
    path('<int:pk>/edit/', views.edit_course, name='edit'),
    path('<int:pk>/delete/', views.delete_course, name='delete'),
    path('<int:pk>/enroll/', views.enroll_course, name='enroll'),
    path('<int:pk>/unenroll/', views.unenroll_course, name='unenroll'),
    path('<int:course_pk>/lessons/add/', views.add_lesson, name='add_lesson'),
    path('lessons/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<int:pk>/edit/', views.edit_lesson, name='edit_lesson'),
    path('lessons/<int:pk>/delete/', views.delete_lesson, name='delete_lesson'),
]
