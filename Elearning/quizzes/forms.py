from django import forms
from .models import Question, Choice, Quiz
from django.forms import inlineformset_factory, modelformset_factory

class QuizAttemptForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super(QuizAttemptForm, self).__init__(*args, **kwargs)
        
        for question in questions:
            choices = [(choice.id, choice.choice_text) for choice in question.choices.all()]
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label=question.question_text
            )
            
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['course', 'title', 'description', 'total_marks', 'passing_marks']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text','marks']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct']


QuestionFormSet = modelformset_factory(Question, form=QuestionForm)

# Create a formset for choices associated with each question
ChoiceFormSet = inlineformset_factory(
    Question, 
    Choice, 
    form=ChoiceForm, 
    extra=4, 
    can_delete=True
)
ChoiceFormSet0 = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=0, can_delete=True)

