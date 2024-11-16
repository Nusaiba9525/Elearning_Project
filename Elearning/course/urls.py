from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('course_category/', views.course_category, name='course_category'),
    path('courses/<str:foo>/', views.course_detail, name='course_detail'),
    path('lectures/<int:pk>/', views.lecture_detail, name='lecture_detail'),  # Updated URL pattern name
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),    
    path('payment_success/<int:enrollment_id>/', views.payment_success, name='payment_success'),
    path('courses/unenroll/<int:course_id>/', views.unenroll_course, name='unenroll_course'),
    path('enrolled_courses/', views.enrolled_courses, name='enrolled_courses'), 
    path('about/', views.about, name='about'),
    path('reviews/', views.review_view, name='reviews'),
    path('courses/<int:course_id>/quizzes/', views.course_quizzes, name='course_quizzes'),
    
   
    
]
