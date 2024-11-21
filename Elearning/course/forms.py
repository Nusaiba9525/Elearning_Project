from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Enrollment,Course,CourseCategory,Lecture, LecturePDF, LectureVideo,Review
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')



class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = []
        
        
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'image', 'description', 'category','price']
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = CourseCategory
        fields = ['name', 'image']
        
        
class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['course', 'title', 'order', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically populate course choices
        self.fields['course'].queryset = Course.objects.all()

        if self.instance and self.instance.pk:  # Editing an existing lecture
            if self.instance.course:
                self.fields['title'].choices = [
                    (lecture.title, lecture.title)
                    for lecture in Lecture.objects.filter(course=self.instance.course)
                ]
        else:  # Creating a new lecture
            self.fields['title'].choices = []  # Empty choices for a new lecture


        
class LecturePDFForm(forms.ModelForm):
    lecture = forms.ModelChoiceField(
        queryset=None,  # This will be dynamically set
        label="Select Title",
        empty_label="Select Title",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = LecturePDF
        fields = ['lecture', 'name', 'pdf_file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'pdf_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Handle the `course` and `lecture` arguments explicitly
        course = kwargs.pop('course', None)
        lecture = kwargs.pop('lecture', None)  # Accept lecture argument

        super().__init__(*args, **kwargs)

        if course:
            # Filter lectures by course
            self.fields['lecture'].queryset = Lecture.objects.filter(course=course)
        elif lecture:
            # Limit the queryset to the given lecture
            self.fields['lecture'].queryset = Lecture.objects.filter(id=lecture.id)


        
class LectureVideoForm(forms.ModelForm):
    lecture = forms.ModelChoiceField(
        queryset=None,  # This will be dynamically set
        label="Select Title",
        empty_label="Select Title",
        widget=forms.Select(attrs={"class": "form-control"}), 
    )

    class Meta:
        model = LectureVideo
        fields = ['lecture', 'name', 'video_url', 'video_file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Video Title'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Video URL'}),
            'video_file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        # Pop the 'course' argument from kwargs (if it exists)
        course = kwargs.pop('course', None)

        # Call the parent constructor with the remaining arguments
        super().__init__(*args, **kwargs)

        # Filter the 'lecture' queryset based on the course, if provided
        if course:
            self.fields['lecture'].queryset = Lecture.objects.filter(course=course)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }
    
    rating = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5})
    )

