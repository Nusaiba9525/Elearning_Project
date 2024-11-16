from Elearning import settings
import stripe
from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Lecture, CourseCategory, Enrollment, Review
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm, LectureForm, LecturePDFForm, LectureVideoForm,ReviewForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.db.models import Count, Q
stripe.api_key = settings.STRIPE_SECRET_KEY

def superuser_required(view_func):
    """Decorator to ensure only superusers can access the view."""
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view_func
@never_cache
def home(request):
    categories = CourseCategory.objects.prefetch_related('courses').all()
    reviews = Review.objects.all()
    return render(request, 'courses/home.html', {'categories': categories, 'reviews': reviews})

@never_cache
@login_required(login_url='/login/')
def course_category(request):
    categories = CourseCategory.objects.all()
    return render(request, 'courses/CourseCategory.html', {'categories': categories})
@never_cache
@login_required(login_url='/login/')
def course_detail(request, foo):
    foo = foo.replace('-', ' ')
    category_obj = get_object_or_404(CourseCategory, name=foo)
    
    # Annotate courses with enrollment_count (number of enrollments) and lecture_count (number of lectures)
    courses = Course.objects.filter(category=category_obj).annotate(
        enrollment_count=Count('enrollments'),
        lecture_count=Count('lectures')
    )
    
    # Store the actual enrollment object or None if not enrolled
    enrolled_courses = {
        course.id: Enrollment.objects.filter(user=request.user, course=course).first()
        for course in courses
    }
    
    return render(request, 'courses/courses.html', {
        'courses': courses,
        'category_obj': category_obj,
        'enrolled_courses': enrolled_courses
    })

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user

    # Check if the user is already enrolled
    enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)

    if enrollment.payment_status == 'Paid':
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('course_detail', foo=course.category.name)

    # If the payment is not completed, create a Stripe PaymentIntent
    if enrollment.payment_status == 'Pending':
        intent = stripe.PaymentIntent.create(
            amount=int(course.price * 100),  # Convert price to cents
            currency='usd',
            metadata={'user_id': user.id, 'course_id': course.id},
        )

        # Store the payment intent ID for later verification
        enrollment.stripe_payment_intent_id = intent.id
        enrollment.payment_status = 'Pending'  # Set status to pending
        enrollment.save()

        context = {
            'course': course,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'client_secret': intent.client_secret,
            'enrollment_id': enrollment.id  # Pass enrollment.id to the template
        }

        return render(request, 'courses/payment.html', context)

    return redirect('course_detail', foo=course.category.name)


    
@login_required
def payment_success(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    
    # Check the PaymentIntent status on Stripe
    try:
        intent = stripe.PaymentIntent.retrieve(enrollment.stripe_payment_intent_id)
        
        if intent.status == 'succeeded':
            enrollment.payment_status = 'Paid'
            enrollment.save()
            print("Payment Intent ID:", enrollment.stripe_payment_intent_id, "Status:", intent.status)
            messages.success(request, 'Payment completed successfully! You are now enrolled.')
        elif intent.status == 'requires_action' or intent.status == 'requires_payment_method':
            messages.warning(request, 'Payment requires additional action. Please complete it to finish enrollment.')
        else:
            messages.error(request, 'Payment was not successful. Please try again.')      
    
    except stripe.error.StripeError as e:
        messages.error(request, f"Error verifying payment: {e.user_message}")

    return redirect('course_detail', foo=enrollment.course.category.name)




@login_required(login_url='/login/')
def enrolled_courses(request):
    # Get only courses the user is enrolled in and have completed payment
    enrollments = Enrollment.objects.filter(user=request.user, payment_status='Paid')
    courses = [enrollment.course for enrollment in enrollments]
    
    # Debugging: print courses to confirm
    print("Courses with 'Paid' status:", courses)
    
    return render(request, 'courses/enrolled_courses.html', {'courses': courses})


@login_required(login_url='/login/')
def unenroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment = Enrollment.objects.filter(course=course, user=request.user).first()
    
    if enrollment:
        enrollment.delete()
    
    return redirect('enrolled_courses')

@login_required(login_url='/login/')
def course_quizzes(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    quizzes = course.quizzes.all()  # Assuming 'quizzes' is a related name for quizzes in the Course model
    return render(request, 'courses/course_quizzes.html', {'course': course, 'quizzes': quizzes})

@never_cache
@login_required(login_url='/login/')
def create_lecture(request, course_id):
    course = Course.objects.get(id=course_id)  # Get the course to which the lecture will belong
    
    if request.method == 'POST':
        lecture_form = LectureForm(request.POST)
        pdf_form = LecturePDFForm(request.POST, request.FILES)
        video_form = LectureVideoForm(request.POST, request.FILES)
        
        if lecture_form.is_valid():
            lecture = lecture_form.save(commit=False)
            lecture.course = course  # Associate the lecture with the course
            lecture.save()
            
            # Save associated PDFs
            if pdf_form.is_valid():
                pdf = pdf_form.save(commit=False)
                pdf.lecture = lecture
                pdf.save()
            
            # Save associated Videos
            if video_form.is_valid():
                video = video_form.save(commit=False)
                video.lecture = lecture
                video.save()
                
            return redirect('course_detail', course_id=course.id)  # Redirect to the course detail page
    else:
        lecture_form = LectureForm(initial={'course': course})
        pdf_form = LecturePDFForm()
        video_form = LectureVideoForm()

    return render(request, 'dashboard/upload_lecture.html', {
        'lecture_form': lecture_form,
        'pdf_form': pdf_form,
        'video_form': video_form,
        'course': course,
    })
@never_cache
@login_required(login_url='/login/')
def lecture_detail(request, pk):
    # Fetch the lecture object using the pk
    lecture = get_object_or_404(Lecture, pk=pk)

    # Access the course related to this lecture
    course = lecture.course

    # Fetch all lectures for this course, ordered by 'order'
    lectures = Lecture.objects.filter(course=course).order_by('order')

    # Fetch videos related to each lecture
    lecture_videos = {lec.id: lec.videos.all() for lec in lectures}

    # Fetch PDFs related to each lecture
    lecture_pdfs = {lec.id: lec.pdfs.all() for lec in lectures}

    return render(request, 'courses/lecture_detail.html', {
        'lectures': lectures,
        'course': course,
        'lecture_videos': lecture_videos,
        'lecture_pdfs': lecture_pdfs,
        'current_lecture': lecture,  # Pass the current lecture for display
    })

@never_cache
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after successful registration
            return redirect('home')  # Redirect to home page or any other page
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'courses/register.html', {'form': form})

@never_cache
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, ('you have been logged in.....'))
            return redirect('home')
        else:
            return render(request, 'courses/login.html', {'form': form, 'error': 'Invalid username or password'})
    else:
        form = AuthenticationForm()
    
    return render(request, 'courses/login.html', {'form': form})

@never_cache
def user_logout(request):
    logout(request)
    messages.success(request,("you have been logged out....."))
    return redirect('home')


@never_cache
@login_required(login_url='/login/')
def review_view(request):
    # Check if the user has already submitted a review
    existing_review = Review.objects.filter(user=request.user).first()
    
    if existing_review:
        messages.info(request, "You have already submitted a review.")
        return render(request,'courses/reviewstop.html')  # Redirect if a review already exists
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('reviews')  # Redirect after successful form submission
    else:
        form = ReviewForm()
    
    reviews = Review.objects.all()
    return render(request, 'courses/review_page.html', {'form': form, 'reviews': reviews})

def about(request):
    return render(request, 'courses/about.html')










