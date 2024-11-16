from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from course.forms import CategoryForm,CourseForm, CategoryForm,LectureForm, LecturePDFForm, LectureVideoForm
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from course.models import Course,Review, Lecture, CourseCategory
from django.contrib.auth.decorators import login_required
from django.urls import reverse
# Create your views here.


#-------Superuser section-------



def superuser_required(view_func):
    """Decorator to ensure only superusers can access the view."""
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view_func

@never_cache
@superuser_required
def manage_courses(request):
    courses = Course.objects.all()
    return render(request, 'dashboard/manage_courses.html', {'courses': courses})

@never_cache
@superuser_required
def manage_users(request):
    superusers = User.objects.filter(is_superuser=True)
    regular_users = User.objects.filter(is_superuser=False)
    
    print("Superusers: ", list(superusers))
    print("Regular Users: ", list(regular_users))
    
    
    return render(request, 'dashboard/manage_user.html', {
        'superusers': superusers,
        'regular_users': regular_users
    })

@never_cache
@superuser_required
def ban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.is_active = False
        user.save()
        messages.success(request, f'User {user.username} has been banned.')
        return redirect('manage_users')
    return render(request, 'dashboard/ban_user_confirm.html', {'user': user})

@never_cache
@superuser_required
def unban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.is_active = True
        user.save()
        messages.success(request, f'User {user.username} has been unbanned.')
        return redirect('manage_users')
    return render(request, 'dashboard/unban_user_confirm.html', {'user': user})

@never_cache
@superuser_required
def upload_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category uploaded successfully.')
            return redirect('manage_categories')
    else:
        form = CategoryForm()

    return render(request, 'dashboard/upload_category.html', {'form': form})

@never_cache
@superuser_required
def manage_categories(request):
    categories = CourseCategory.objects.all()
    return render(request, 'dashboard/manage_categories.html', {'categories': categories})

def edit_category(request, category_id):
    category = get_object_or_404(CourseCategory, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('manage_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/edit_category.html', {'form': form, 'category': category})

def delete_category(request, category_id):
    category = get_object_or_404(CourseCategory, id=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('manage_categories')
    return render(request, 'dashboard/delete_category_confirm.html', {'category': category})

@never_cache
@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('manage_courses')
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'dashboard/edit_course.html', {'form': form, 'course': course})

@login_required
@superuser_required
def review_management(request):
    reviews = Review.objects.all()
    return render(request, 'dashboard/review_management.html', {'reviews': reviews})

@login_required
@superuser_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        review.delete()
        return redirect('review_management')  # Redirect to the management page after deletion
    return render(request, 'dashboard/review_confirm_delete.html', {'review': review})

@never_cache
@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        course.delete()
        return redirect('manage_courses')
    return render(request, 'dashboard/delete_course_confirm.html', {'course': course})

@never_cache
@login_required
def upload_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('manage_courses',)
    else:
        form = CourseForm()
    return render(request, 'dashboard/upload_course.html', {'form': form})


@login_required
def manage_lectures(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = LectureForm(request.POST, request.FILES)

        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.course = course  # Assign the course to the lecture
            lecture.save()

            if 'add_videos' in request.POST:
                return redirect(reverse('add_lecture_video', args=[course_id]))
            elif 'add_pdfs' in request.POST:
                return redirect(reverse('add_lecture_pdf', args=[course_id]))
            else:
                return redirect(reverse('manage_lectures', args=[course_id]))
    else:
        form = LectureForm()

    lectures = Lecture.objects.filter(course=course)

    return render(request, 'dashboard/manage_lectures.html', {
        'form': form,
        'lectures': lectures,
        'course': course,
        'course_id': course_id,
    })



@login_required
def edit_lecture(request, pk):
    # Fetch the lecture object
    lecture = get_object_or_404(Lecture, id=pk)

    if request.method == 'POST':
        # Initialize the main form
        form = LectureForm(request.POST, request.FILES, instance=lecture)

        # Initialize PDF and video forms with unique prefixes
        pdf_forms = [
            LecturePDFForm(request.POST, request.FILES, instance=pdf, prefix=f"pdf_{pdf.id}", lecture=lecture)
            for pdf in lecture.pdfs.all()
        ]
        video_forms = [
            LectureVideoForm(request.POST, request.FILES, instance=video, prefix=f"video_{video.id}")
            for video in lecture.videos.all()
        ]

        if form.is_valid() and all(pdf_form.is_valid() for pdf_form in pdf_forms):
            # Save the main form
            form.save()

            # Save PDF forms
            for pdf_form in pdf_forms:
                pdf_form.save()

            # Save video forms
            for video_form in video_forms:
                video_form.save()

            return redirect('lecture_detail', pk=lecture.id)
    else:
        # Initialize forms with unique prefixes
        form = LectureForm(instance=lecture)
        pdf_forms = [
            LecturePDFForm(instance=pdf, prefix=f"pdf_{pdf.id}", lecture=lecture)
            for pdf in lecture.pdfs.all()
        ]
        video_forms = [
            LectureVideoForm(instance=video, prefix=f"video_{video.id}")
            for video in lecture.videos.all()
        ]

    return render(request, 'dashboard/edit_lecture.html', {
        'form': form,
        'pdf_forms': pdf_forms,
        'video_forms': video_forms,
        'lecture': lecture,
    })




@login_required
def delete_lecture(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    if request.method == 'POST':
        course_id = lecture.course.id
        lecture.delete()
        return redirect('lecture_detail', pk=course_id)
    return render(request, 'dashboard/confirm_delete.html', {'lecture': lecture})

def upload_lecture(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    form = LectureForm(request.POST or None, request.FILES or None)
    video_form = LectureVideoForm()
    pdf_form = LecturePDFForm()

    if request.method == 'POST':
        if form.is_valid():
            # Save the lecture
            lecture = form.save(commit=False)
            lecture.course = course
            lecture.save()
            messages.success(request, 'Lecture uploaded successfully.')
            return redirect('manage_lectures', course_id=course.id)  # Redirect to manage lectures after success
        else:
            messages.error(request, 'Please correct the errors in the form.')

    return render(request, 'dashboard/upload_lecture.html', {
        'form': form,
        'video_form': video_form,
        'pdf_form': pdf_form,
        'course': course
    })

@login_required
def add_lecture_pdf(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        pdf_form = LecturePDFForm(request.POST, request.FILES, course=course)
        if pdf_form.is_valid():
            pdf_form.save()
            messages.success(request, "Lecture PDF uploaded successfully.")
            return redirect('manage_lectures', course_id=course.id)
    else:
        pdf_form = LecturePDFForm(course=course)

    return render(request, 'dashboard/lecture_pdfs.html', {
        'pdf_form': pdf_form,
        'course': course,
    })

def add_lecture_video(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        video_form = LectureVideoForm(request.POST, request.FILES, course=course)
        if video_form.is_valid():
            video_form.save()
            messages.success(request, "Lecture Video uploaded successfully.")
            return redirect('manage_lectures', course_id=course.id)
    else:
        video_form = LectureVideoForm(course=course)

    return render(request, 'dashboard/lecture_videos.html', {
        'video_form': video_form,
        'course': course,
    })
