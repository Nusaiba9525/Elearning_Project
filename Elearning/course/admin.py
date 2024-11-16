from django.contrib import admin
from .models import Course, CourseCategory, Lecture,Review, LecturePDF, LectureVideo

# Inline class for Lecture
class LectureInline(admin.TabularInline):
    model = Lecture
    extra = 1  # Number of empty lecture fields to display by default
    can_delete = True
    fields = ('title', 'order')

# Admin class for Course
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'created_at', 'video_count')
    search_fields = ('title', 'instructor__username', 'category__name')
    list_filter = ('category', 'instructor', 'created_at')
    inlines = [LectureInline]  # Include lectures inline within the course

# Admin class for CourseCategory
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_count')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at')
    search_fields = ('content',)
    list_filter = ('rating', 'created_at')

class LecturePDFInline(admin.TabularInline):
    model = LecturePDF
    extra = 1  # Number of empty PDF fields displayed initially

class LectureVideoInline(admin.TabularInline):
    model = LectureVideo
    extra = 1  # Number of empty video fields displayed initially

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    inlines = [LecturePDFInline, LectureVideoInline]
    list_display = ['title', 'created_at']

# Registering models with the admin site
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseCategory, CourseCategoryAdmin)
