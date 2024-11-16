from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class CourseCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    course_count = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='Categories', null=True, blank=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='courses', null=True, blank=True)
    description = models.TextField()
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    video_count = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def __str__(self):
        return self.title

    def student_count(self):
        return self.enrollments.count()

    def lecture_count(self):
        return self.lecture_set.count()
    



class Lecture(models.Model):
    course = models.ForeignKey(Course, related_name="lectures", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class LecturePDF(models.Model):
    lecture = models.ForeignKey(Lecture, related_name="pdfs", on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to='lectures/pdfs/')
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)  # This is the field you added

    def __str__(self):
        return self.name

class LectureVideo(models.Model):
    lecture = models.ForeignKey(Lecture, related_name="videos", on_delete=models.CASCADE)
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='lectures/videos/', blank=True, null=True)
    title = models.CharField(max_length=200, blank=True)
    name = models.CharField(max_length=255) 

    def __str__(self):
        return self.name

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user} enrolled in {self.course} - {self.payment_status}"
    
    
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()  # Main content of the review
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  # Rating given by the user # Rating given by the user
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the review was created

    def __str__(self):
        return f"Review by {self.user.username}"
    
    





