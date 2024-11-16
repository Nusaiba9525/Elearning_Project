from django.urls import path
from . import views

urlpatterns = [
   path('superuser/manage-courses/', views.manage_courses, name='manage_courses'),
    path('superuser/upload-category/', views.upload_category, name='upload_category'),
    path('superuser/manage-users/', views.manage_users, name='manage_users'),
    path('superuser/<int:user_id>/ban-user/', views.ban_user, name='ban_user'),
    path('superuser/unban-user/<int:user_id>/', views.unban_user, name='unban_user'),
    path('upload/course/', views.upload_course, name='upload_course'),
    path('course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('course/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('reviews/', views.review_management, name='review_management'),
    path('reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('categories/', views.manage_categories, name='manage_categories'),  # No leading slash
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('courses/<int:course_id>/lectures/manage/', views.manage_lectures, name='manage_lectures'),
    path('lectures/edit/<int:pk>/', views.edit_lecture, name='edit_lecture'),
    path('lectures/<int:lecture_id>/delete/', views.delete_lecture, name='delete_lecture'),
    path('dashboardcourses/<int:course_id>/lectures/upload/', views.upload_lecture, name='upload_lecture'),
    path('course/<int:course_id>/add_video/', views.add_lecture_video, name='add_lecture_video'),
    path('course/<int:course_id>/add_pdf/', views.add_lecture_pdf, name='add_lecture_pdf'),
    
]
