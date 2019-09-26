from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError

from classroom.models import (Answer, Question, Student, StudentAnswer,
                              Subject, User, Topics)


class TeacherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
        return user


class StudentSignUpForm(UserCreationForm):
    interests = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.save()
        student = Student.objects.create(user=user)
        student.interests.add(*self.cleaned_data.get('interests'))
        return user


class StudentInterestsForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('interests',)
        widgets = {
            'interests': forms.CheckboxSelectMultiple
        }


class QuestionForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super(QuestionForm, self).__init__(*args, **kwargs)
    #     # self.user = user
    #     # super(QuestionForm, self).__init__(*args, **kwargs)
    #     # self.fields['topics'].initial = user.email
    #
    #     id = kwargs.pop('pk')
    #     self.fields['topics'] = forms.ModelMultipleChoiceField(
    #         required=False,
    #         queryset=Topics.objects.filter(subject=id).values_list('topic_name', flat=True),
    #         )


    #
    iquery = Topics.objects.values_list('topic_name', flat=True)
    # iquery2 = Topics.objects.values_list('id', flat=True)
    #
    # iquery3 = Topics.objects.values()
    # print(iquery)
    # print(iquery2)
    # print(iquery3)
    iquery_choices = [(id,id) for id in iquery]
    print(iquery_choices)
    topics = forms.ChoiceField(choices=iquery_choices,label="", initial='', required=True, widget=forms.Select())
	
	'''
    topics = forms.ModelChoiceField(
        queryset=Topics.objects.values_list('topic_name', flat=True),
        required=True,
        empty_label=None)
		'''

    class Meta:
        model = Question
        fields = ('text','topics')



class QuestionFormWithoutPost(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super(QuestionForm, self).__init__(*args, **kwargs)
    #     # self.user = user
    #     # super(QuestionForm, self).__init__(*args, **kwargs)
    #     # self.fields['topics'].initial = user.email
    #
    #     id = kwargs.pop('pk')
    #     self.fields['topics'] = forms.ModelMultipleChoiceField(
    #         required=False,
    #         queryset=Topics.objects.filter(subject=id).values_list('topic_name', flat=True),
    #         )

    #
    #
    # iquery = Topics.objects.values_list('topic_name', flat=True)
    # print(iquery)
    # iquery_choices = [(id,id) for id in iquery]
    # print(iquery_choices)
    # topics = forms.ChoiceField(choices=iquery_choices, required=True, widget=forms.Select())

    # topics = forms.ChoiceField(
    #     queryset=Topics.objects.values_list('topic_name', flat=True),
    #     required=True,
    #     empty_label=None)

    class Meta:
        model = Question
        fields = ('text',)


class BaseAnswerInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        has_one_correct_answer = False
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('is_correct', False):
                    has_one_correct_answer = True
                    break
        if not has_one_correct_answer:
            raise ValidationError('Mark at least one answer as correct.', code='no_correct_answer')


class TakeQuizForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        widget=forms.RadioSelect(),
        required=True,
        empty_label=None)

    class Meta:
        model = StudentAnswer
        fields = ('answer',)

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answers.order_by('text')
