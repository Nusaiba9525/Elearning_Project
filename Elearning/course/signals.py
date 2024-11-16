from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Course, Lecture

@receiver(post_save, sender=Course)
def update_course_count_on_save(sender, instance, created, **kwargs):
    if created:
        instance.category.course_count += 1
        instance.category.save()

@receiver(post_delete, sender=Lecture)
def update_video_count_on_delete(sender, instance, **kwargs):
    course = instance.course
    if course.video_count > 0:
        course.video_count -= 1
        course.save()

@receiver(post_save, sender=Lecture)
def update_video_count_on_save(sender, instance, created, **kwargs):
    if created:
        instance.course.video_count += 1
        instance.course.save()

