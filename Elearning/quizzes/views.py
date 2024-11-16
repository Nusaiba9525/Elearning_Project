from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Quiz, StudentQuizAttempt
from .forms import QuizAttemptForm,QuizForm, Question, QuestionForm, Quiz, ChoiceFormSet, ChoiceForm, Choice
from course.models import Course
from django.contrib.auth.decorators import user_passes_test
from django.forms import modelformset_factory
from django.contrib import messages



@login_required
def quiz_detail(request, course_id, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, course_id=course_id)
    
    # Get all questions for the quiz
    questions = quiz.questions.all()
    
    if request.method == 'POST':
        form = QuizAttemptForm(request.POST, questions=questions)
        if form.is_valid():
            score = 0
            total_marks = 0
            
            for question in questions:
                selected_choice_id = form.cleaned_data.get(f'question_{question.id}')
                if selected_choice_id:
                    selected_choice = question.choices.filter(id=selected_choice_id).first()
                    if selected_choice and selected_choice.is_correct:
                        score += question.marks
                    total_marks += question.marks
            
            passed = score >= quiz.passing_marks
            StudentQuizAttempt.objects.create(
                student=request.user,
                quiz=quiz,
                score=score,
                passed=passed
            )
            
            return redirect('quiz_result', course_id=course_id, quiz_id=quiz.id)
        else:
            print(form.errors)  # Debug form errors
    else:
        form = QuizAttemptForm(questions=questions)

    field_question_map = {field.name: field.name.split('_')[1] for field in form}
    
    return render(request, 'quizzes/quiz_detail.html', {
        'quiz': quiz,
        'form': form,
        'field_question_map': field_question_map
    })


def question_list(request, course_id, quiz_id):
    print(f"Course ID: {course_id}, Quiz ID: {quiz_id}")
    quiz = get_object_or_404(Quiz, id=quiz_id, course_id=course_id)
    
    # Get all questions for the quiz
    questions = quiz.questions.all()
    
    if request.method == 'POST':
        form = QuizAttemptForm(request.POST, questions=questions)
        if form.is_valid():
            score = 0
            total_marks = 0
            
            for question in questions:
                selected_choice_id = form.cleaned_data.get(f'question_{question.id}')
                if selected_choice_id:
                    selected_choice = question.choices.filter(id=selected_choice_id).first()
                    if selected_choice and selected_choice.is_correct:
                        score += question.marks
                    total_marks += question.marks
            
            passed = score >= quiz.passing_marks
            StudentQuizAttempt.objects.create(
                student=request.user,
                quiz=quiz,
                score=score,
                passed=passed
            )
            
            return redirect('quiz_result', course_id=course_id, quiz_id=quiz.id)
        else:
            print(form.errors)  # Debug form errors
    else:
        form = QuizAttemptForm(questions=questions)

    field_question_map = {field.name: field.name.split('_')[1] for field in form}
    
    return render(request, 'quizzes/question_list.html', {
        'quiz': quiz,
        'form': form,
        'field_question_map': field_question_map
    })
    
    
    
@login_required
def quiz_result(request, course_id, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    # Get all attempts by the current user for this quiz
    attempts = StudentQuizAttempt.objects.filter(student=request.user, quiz=quiz)

    if attempts.exists():
        attempt = attempts.latest('created_at')  # Now using the newly added field
    else:
        attempt = None

    return render(request, 'quizzes/quiz_result.html', {
        'quiz': quiz,
        'attempt': attempt,
    })
    
    

def retry_quiz(request, course_id, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, course_id=course_id)
    # Logic to handle retrying the quiz
    return redirect('quiz_detail', course_id=course_id, quiz_id=quiz_id)


def superuser_required(view_func):
    """Decorator to ensure only superusers can access the view."""
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view_func





@superuser_required
def upload_quiz(request):
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        
        if quiz_form.is_valid():
            quiz = quiz_form.save()  # Save and get the single Quiz instance
            messages.success(request, 'Quiz uploaded successfully!')
            return redirect('upload_question', quiz_id=quiz.id)  # Redirect with quiz_id
        else:
            messages.error(request, 'The quiz form is not valid.')
    else:
        quiz_form = QuizForm()  # Initialize the form in GET request

    return render(request, 'quizzes/upload_quiz.html', {'quiz_form': quiz_form})
        

def upload_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        choice_formset = ChoiceFormSet(request.POST, prefix='choices')
        
        if question_form.is_valid() and choice_formset.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz  # Set the quiz field here
            question.save()
            
            # Save choices
            for choice_form in choice_formset:
                if choice_form.cleaned_data.get('choice_text'):
                    choice = choice_form.save(commit=False)
                    choice.question = question
                    choice.save()

            messages.success(request, 'Question and choices uploaded successfully!')
            return redirect('upload_question', quiz_id=quiz_id)
        else:
            messages.error(request, 'There was an error with the form submission.')
            return render(request, 'quizzes/upload_question.html', {
                'quiz': quiz,
                'question_form': question_form,
                'choice_formset': choice_formset,
                'question_form_errors': question_form.errors,
                'choice_formset_errors': choice_formset.errors,
            })
    else:
        question_form = QuestionForm()
        choice_formset = ChoiceFormSet(prefix='choices', queryset=Choice.objects.none())

    return render(request, 'quizzes/upload_question.html', {
        'quiz': quiz,
        'question_form': question_form,
        'choice_formset': choice_formset,
    })
    
    
    
    
def course_quizzes_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    quizzes = Quiz.objects.filter(course=course)

    return render(request, 'quizzes/course_quizzes.html', {'course': course,'quizzes': quizzes,})   




def quiz_list_view(request):
    # Retrieve all courses with their associated quizzes
    courses = Course.objects.prefetch_related('quizzes').all()

    context = {
        'courses': courses,
    }

    return render(request, 'quizzes/quiz_list.html', context)



    

@superuser_required
def edit_quiz_view(request, course_id, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, course_id=course_id)
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect('quiz_list')  # Assuming 'quiz_list' is the name of the URL for listing quizzes
    else:
        form = QuizForm(instance=quiz)
    
    return render(request, 'quizzes/edit_quiz.html', {'form': form, 'quiz': quiz})

@superuser_required
def delete_quiz_view(request, course_id, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, course_id=course_id)
    
    if request.method == 'POST':
        quiz.delete()
        return redirect('quiz_list')  # Assuming 'quiz_list' is the name of the URL for listing quizzes
    
    return render(request, 'quizzes/delete_quiz_confirm.html', {'quiz': quiz})



@login_required
@superuser_required
def edit_question_view(request, course_id, quiz_id, question_id):
    question = get_object_or_404(Question, id=question_id, quiz_id=quiz_id)
    quiz = Quiz.objects.get(id=quiz_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.quiz_id = quiz_id  # Set the quiz_id manually
            question.save()
            return redirect('question_list', course_id=course_id, quiz_id=quiz_id)
        else:
            print(form.errors)  # For debugging purposes
    else:
        form = QuestionForm(instance=question)
    
    context = {'form': form, 'quiz': question.quiz}
    return render(request, 'quizzes/edit_question.html', context)



def edit_choices_view(request, course_id, quiz_id, question_id):
    question = get_object_or_404(Question, id=question_id, quiz_id=quiz_id)
    ChoiceFormSet = modelformset_factory(Choice, form=ChoiceForm, extra=0, can_delete=True)
    formset = ChoiceFormSet(queryset=Choice.objects.filter(question=question))

    if request.method == 'POST':
        formset = ChoiceFormSet(request.POST, queryset=Choice.objects.filter(question=question))
        if formset.is_valid():
            formset.save()
            return redirect('question_list', course_id=course_id, quiz_id=quiz_id)
    context = {'formset': formset, 'quiz': question.quiz}
    return render(request, 'quizzes/edit_choices.html', context)
    
    
    
@login_required
@superuser_required
def delete_question_view(request, course_id, quiz_id, question_id):
    question = get_object_or_404(Question, id=question_id, quiz__id=quiz_id, quiz__course__id=course_id)
    quiz = get_object_or_404(Quiz, id=quiz_id, course_id=course_id)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully.')
        return redirect('question_list', course_id=quiz.course.id, quiz_id=quiz.id)
    
    return render(request, 'quizzes/delete_question_confirm.html', {'question': question,'quiz': quiz})


def success_view(request):
    return render(request, 'quizzes/success.html', {'message': 'Operation completed successfully!'})


