from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('<int:course_pk>/create/', views.create_quiz, name='create'),
    path('<int:pk>/', views.quiz_detail, name='detail'),
    path('<int:pk>/edit/', views.edit_quiz, name='edit'),
    path('<int:pk>/delete/', views.delete_quiz, name='delete'),
    path('<int:pk>/take/', views.take_quiz, name='take'),
    path('<int:pk>/results/', views.quiz_results_overview, name='results_overview'),
    path('result/<int:pk>/', views.quiz_result, name='result'),
    path('attempt/<int:pk>/', views.quiz_attempt_detail, name='attempt_detail'),
    path('<int:quiz_pk>/questions/add/', views.add_question, name='add_question'),
    path('questions/<int:pk>/edit/', views.edit_question, name='edit_question'),
    path('questions/<int:pk>/delete/', views.delete_question, name='delete_question'),
    path('my-results/', views.my_results, name='my_results'),
]
