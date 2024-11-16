from django.urls import path
from . import views

urlpatterns = [
    path('courses/<int:course_id>/quiz/<int:quiz_id>/detail/', views.quiz_detail, name='quiz_detail'),
    path('courses/<int:course_id>/quiz/<int:quiz_id>/questions/', views.question_list, name='question_list'),
    path('courses/<int:course_id>/quiz/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
    path('courses/<int:course_id>/quiz/<int:quiz_id>/retry/', views.retry_quiz, name='retry_quiz'),
    path('upload/quiz/', views.upload_quiz, name='upload_quiz'),
    path('upload/success/', views.success_view, name='success_view_name'),
    path('upload-question/<int:quiz_id>/', views.upload_question, name='upload_question'),
    path('quizzes/', views.quiz_list_view, name='quiz_list'),
    path('courses/<int:course_id>/quiz/<int:quiz_id>/edit/', views.edit_quiz_view, name='edit_quiz'),
    path('courses/<int:course_id>/quiz/<int:quiz_id>/delete/', views.delete_quiz_view, name='delete_quiz'),
    path('quizzescourse/<int:course_id>/quiz/<int:quiz_id>/question/<int:question_id>/edit/', views.edit_question_view, name='edit_question'),
    path('quizzescourse/<int:course_id>/quiz/<int:quiz_id>/question/<int:question_id>/choices/edit/', views.edit_choices_view, name='edit_choices'),
    path('course/<int:course_id>/quiz/<int:quiz_id>/question/<int:question_id>/delete/', views.delete_question_view, name='delete_question'),
]