from django.db import models
from course.models import Course
from django.contrib.auth import get_user_model
from django.utils import timezone

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField()
    total_marks = models.PositiveIntegerField( default=100)
    passing_marks = models.PositiveIntegerField(default=50)

    def __str__(self):
        return self.title
    
    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    marks = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.question_text
    
    
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text





User = get_user_model()

class StudentQuizAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    passed = models.BooleanField()
    created_at = models.DateTimeField(default=timezone.now)  # Add this field to track the attempt time

    def __str__(self):
        return f'{self.student.username} - {self.quiz.title}'
