from django.contrib import admin
from .models import Quiz, Question, Choice, StudentQuizAttempt

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('title', 'course', 'total_marks', 'passing_marks')
    search_fields = ('title', 'course__title')

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('quiz', 'question_text', 'marks')
    search_fields = ('quiz__title', 'question_text')

class StudentQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'passed')
    search_fields = ('student__username', 'quiz__title')

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(StudentQuizAttempt, StudentQuizAttemptAdmin)
# Customizing the admin site appearance
admin.site.site_header = "My Online Learning Platform Admin"
admin.site.site_title = "StudyNest Admin Portal"
admin.site.index_title = "Welcome to the StudyNest Admin"


