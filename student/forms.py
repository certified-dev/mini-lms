import random
from django import forms as django_forms
import floppyforms.__future__ as forms
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.template.loader import render_to_string

from django.contrib.auth.forms import UserCreationForm

from core.models import Course, Answer, Faculty, Department, Studycentre, Programme, Post, Session

from student.models import Student, StudentAnswer
from exams.models import Exam

User = get_user_model()

GENDER = (
    ('-------', '-------'),
    ('Male', 'Male'),
    ('Female', 'Female'),

)

STATES = (
    ('-------', '-------'),
    ('Lagos', 'Lagos'),
    ('Edo', 'Edo'),
    ('Abuja', 'Abuja'),
    ('Yola', 'Yola'),

)


class StudentSignUpForm(UserCreationForm):
    # Declare user option fields to form
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    other_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Other name'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Surname'}))
    birth_place = forms.ChoiceField(required=True, choices=STATES)
    sex = forms.ChoiceField(required=True, choices=GENDER)
    birth_date = forms.DateField(required=True, widget=forms.DateInput)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter email address'}), required=True)
    phone = forms.CharField(required=True, widget=forms.PhoneNumberInput(attrs={'placeholder': 'Mobile Number'}))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'House/Street/City/Town '}),
                              max_length=100)
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.all())

    # Add Extra Student options fields to form
    study_centre = forms.ModelChoiceField(queryset=Studycentre.objects.all())
    programme = forms.ModelChoiceField(queryset=Programme.objects.all())
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)

    class Meta:
        model = User
        fields = ('first_name', 'other_name', 'last_name', 'sex', 'birth_place',
                  'address', 'phone', 'email', 'faculty', 'department',
                  'programme', 'study_centre', 'birth_date',)

    # Add placeholders to UserCreationForm password fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Choose A Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Verify Password'})

        # Filter Department choice by selected faculty
        self.fields['department'].queryset = Department.objects.none()

        for field_name in ['password1', 'password2']:
            self.fields[field_name].help_text = None

        if 'faculty' in self.data:
            try:
                faculty_id = int(self.data.get('faculty'))
                self.fields['department'].queryset = Department.objects.filter(faculty_id=faculty_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty department queryset
        elif self.instance.pk:
            self.fields['department'].queryset = self.instance.faculty.department_set.order_by('name')

    # Check if inputted email has not been used by another user
    def clean_email(self):
        email = self.cleaned_data['email']
        check = User.objects.values('email')
        if email in check:
            msg = 'this email has been used!'
            self.add_error('email', msg)
        return email

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        # Generate student matric number
        n = random.randint(10000, 50000)
        user.username = 'stu' + str(n)
        user.is_student = True
        user.save()
        # retrieve student info from relevant form field
        study_centre = self.cleaned_data.get('study_centre')
        programme = self.cleaned_data.get('programme')
        department = self.cleaned_data.get('department')
        # Create student object with user id
        Student.objects.create(user=user, study_centre=study_centre, programme=programme,
                               department=department)
        return user


class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('photo',)


class CourseRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('courses',)
        widgets = {
            'courses': forms.CheckboxSelectMultiple
        }

    # Filter semester registrable  courses by student level and faculty
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        active_session = Session.objects.get(active=True)

        if '/1' in active_session.title:
            session = 1
        elif '/2' in active_session.title:
            session = 2

        courses = Course.objects.filter(semester__title=session, host_faculty=self.request.user.faculty)
        others = Course.objects.filter(host_faculty__name="General Studies", semester__title=session)
        self.fields["courses"].queryset = courses | others

    # Check if selected courses is empty or has more than 24 credit unit
    def clean_courses(self):
        courses = self.cleaned_data['courses']
        msg = render_to_string('student/error/insufficient.html')
        msg3 = render_to_string('student/error/no_selection.html')

        if courses:
            check = courses.aggregate(Sum('credit_unit'))['credit_unit__sum']
            check1 = courses.aggregate(Sum('fee'))['fee__sum']

            if self.request.user.student.courses.aggregate(Sum('fee'))['fee__sum'] is None:
                check2 = 0
            else:
                check2 = self.request.user.student.courses.aggregate(Sum('fee'))['fee__sum']

            check3 = check1 - check2
            check4 = self.request.user.student.courses.all()

            msg1 = render_to_string('student/error/course.html', {'check': check, })

            if check is None or check > 24 or set(courses) == set(check4):
                self.add_error('courses', msg1)

            if check is not None and check3 > self.request.user.student.wallet_balance:
                self.add_error('courses', msg)
        else:
            self.add_error('courses', msg3)

        return courses


class ExamRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('exams',)
        widgets = {
            'exams': forms.SelectMultiple
        }

    # Filter registrable exams by student courses
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["exams"].queryset = Exam.objects.filter(course__in=self.request.user.student.courses.all())


class TakeTmaForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        widget=django_forms.RadioSelect(),
        required=True,
        empty_label=None)

    class Meta:
        model = StudentAnswer
        fields = ('answer',)

    # Filter answers by question
    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answers.order_by('text')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', ]
