from django import forms as django_forms
import floppyforms.__future__ as forms
from django.forms.utils import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from core.models import Faculty, Course, Topic
from lecturer.models import Lecturer
from student.models import Tma, Exam, TmaQuestion, ExamQuestion

from student.choices import GENDER, TYPES, STATES, TMA

User = get_user_model()


class LecturerSignUpForm(UserCreationForm):
    # Declare user option fields to form
    first_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'placeholder': 'First name'}))
    other_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Other name'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Surname '}))
    birth_place = forms.ChoiceField(required=True, choices=STATES)
    sex = forms.ChoiceField(required=True, choices=GENDER)
    birth_date = forms.DateField(required=True, widget=forms.DateInput)
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'placeholder': 'Enter email address'}), required=True)
    phone = forms.CharField(required=True, widget=forms.PhoneNumberInput(
        attrs={'placeholder': 'Mobile Number'}))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'House/Street/City/Town '}),
                              max_length=100)
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all(), required=False)

    class Meta:
        model = User
        fields = ('first_name', 'other_name', 'last_name', 'sex', 'birth_place', 'address',
                  'phone', 'email', 'faculty', 'birth_date', 'username',)

    # Add placeholder to UserCreationForm fields
    def __init__(self, *args, **kwargs):
        super(LecturerSignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'placeholder': 'Choose A Unique Username'})
        self.fields['password1'].widget.attrs.update(
            {'placeholder': 'Choose A Password'})
        self.fields['password2'].widget.attrs.update(
            {'placeholder': 'Verify Password'})

    # Check if inputted email has not been used by another user
    def clean_email(self):
        email = self.cleaned_data['email']
        check = User.objects.values('email')
        if email in check:
            msg = 'this email has been used!'
            self.add_error('email', msg)
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        if commit:
            user.save()
            # Create lecturer object with user id
            Lecturer.objects.create(user=user)

        return user


class PassportForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('photo',)


class TmaForm(forms.ModelForm):
    title = forms.ChoiceField(choices=TMA, required=True)

    class Meta:
        model = Tma
        fields = ['title', 'course']

    # Filter Tma courses list for appointed lecturer
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = Course.objects.filter(
            lecturer=self.request.user.lecturer)


class QuestionForm(forms.ModelForm):
    text = forms.CharField(required=True,
                           widget=forms.Textarea(
                               attrs={'rows': 2, 'placeholder': 'Enter your Question.'}),
                           max_length=4000,
                           help_text='The max length of the question is 4000.')

    class Meta:
        model = TmaQuestion
        fields = ('text',)


class ExamQuestionForm(forms.ModelForm):
    type = forms.ChoiceField(required=True, choices=TYPES, widget=forms.RadioSelect)
    text = forms.CharField(required=True,
                           widget=forms.Textarea(
                               attrs={'rows': 2, 'placeholder': 'Enter your Question.'}),
                           max_length=4000,
                           help_text='The max length of the question is 4000.')

    class Meta:
        model = ExamQuestion
        fields = ('text', 'type')


class ExamQuestionUpdateForm(forms.ModelForm):
    text = forms.CharField(required=True,
                           widget=forms.Textarea(
                               attrs={'rows': 2, 'placeholder': 'Enter your Question.'}),
                           max_length=4000,
                           help_text='The max length of the question is 4000.')

    class Meta:
        model = ExamQuestion
        fields = ('text',)


class BaseAnswerInlineFormSet(forms.BaseInlineFormSet):

    def clean(self):
        super().clean()
        # Check that an answer is selected for a question
        has_one_correct_answer = False
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('is_correct', False):
                    has_one_correct_answer = True
                    break
        if not has_one_correct_answer:
            raise ValidationError(
                'Mark at least one answer as correct.', code='no_correct_answer')


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['course', ]

    # Filter Exam courses list for appointed lecturer
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = Course.objects.filter(
            lecturer=self.request.user.lecturer)


class NewTopicForm(forms.ModelForm):
    subject = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Add Subject'}))
    files = forms.FileField(required=False)

    class Meta:
        model = Topic
        fields = ['subject', 'course', 'message', 'files']

    # Filter topic courses list for appointed lecturer
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = Course.objects.filter(
            lecturer=self.request.user.lecturer)


class UpdateTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('subject', 'message', 'files')
