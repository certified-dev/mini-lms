import random
from django import forms as django_forms
import floppyforms.__future__ as forms
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.template.loader import render_to_string

from django.contrib.auth.forms import UserCreationForm

from core.models import Course, Faculty, Department, Studycentre, Programme, Post, Session

from student.models import Student, StudentTmaAnswer, ExamAnswer, Exam, TmaAnswer, StudentExamAnswer

from student.choices import GENDER, LEVEL

User = get_user_model()


class StudentSignUpForm(UserCreationForm):
    # Declare user option fields to form
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    other_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Other name'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Surname'}))
    birth_place = forms.ChoiceField(required=True)
    sex = forms.ChoiceField(required=True, choices=GENDER)
    birth_date = forms.DateField(required=True, widget=forms.DateInput)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter email address'}), required=True)
    phone = forms.CharField(required=True, widget=forms.PhoneNumberInput(attrs={'placeholder': 'Mobile Number'}))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'House/Street/City/Town '}),
                              max_length=100)
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.all())

    # Add Extra Student options fields to form
    study_centre = forms.ModelChoiceField(queryset=Studycentre.objects.all(), required=False)
    programme = forms.ModelChoiceField(queryset=Programme.objects.all())
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    level = forms.ChoiceField(choices=LEVEL, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'other_name', 'last_name', 'sex', 'birth_place',
                  'address', 'phone', 'email', 'faculty', 'department', 'level',
                  'programme', 'study_centre', 'birth_date',)

    # Add placeholders to UserCreationForm password fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Choose A Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Verify Password'})

        # Filter Department choice by selected faculty
        self.fields['department'].queryset = Department.objects.none()
        self.fields['programme'].queryset = Programme.objects.none()

        for field_name in ['password1', 'password2']:
            self.fields[field_name].help_text = None

        if 'faculty' in self.data:
            try:
                faculty_id = int(self.data.get('faculty'))
                self.fields['department'].queryset = Department.objects.filter(faculty_id=faculty_id).exclude(
                    name='General Studies').order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty department queryset
        elif self.instance.pk:
            self.fields['department'].queryset = self.instance.faculty.department_set.order_by('name')

        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['programme'].queryset = Programme.objects.filter(department_id=department_id).order_by(
                    'name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty department queryset
        elif self.instance.pk:
            self.fields['programme'].queryset = self.instance.department.programme_set.order_by('name')

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

        while True:
            gen_matric = 'stu' + str(random.randint(10000, 50000))
            if not Student.objects.filter(user__username=gen_matric).exists():
                user.username = gen_matric
                break
                

        user.is_student = True
        user.save()
        # retrieve student info from relevant form field
        study_centre = self.cleaned_data.get('study_centre')
        programme = self.cleaned_data.get('programme')
        department = self.cleaned_data.get('department')
        level = self.cleaned_data.get('level')
        # Create student object with user id
        Student.objects.create(user=user, study_centre=study_centre, programme=programme,
                               department=department, level=level)
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

    def __init__(self, *args, **kwargs):
        global session
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        user = self.request.user

        if int(user.student.semesters_completed) % 2:
            session = "2"
        else:
            session = "1"

        reg_courses = user.student.courses.all().values_list('pk', flat=True)

        main_courses = Course.objects.filter(semester__title=session,
                                        level=user.student.level,
                                        host_faculty=user.faculty)
        gen_courses = Course.objects.filter(host_faculty__name="General Studies",
                                       level=user.student.level,
                                       semester__title=session)
        form_courses = main_courses | gen_courses
        
        self.fields["courses"].queryset = form_courses.exclude(pk__in=reg_courses)

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
        student_courses = self.request.user.student.courses.all()
        regged_exams = self.request.user.student.exams.all().values_list('pk', flat=True)
        self.fields["exams"].queryset = Exam.objects.filter(course__in=student_courses).exclude(pk__in=regged_exams)


class TakeTmaForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=TmaAnswer.objects.none(),
        widget=django_forms.RadioSelect(),
        required=True,
        empty_label=None)

    class Meta:
        model = StudentTmaAnswer
        fields = ('answer',)

    # Filter answers by question
    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.tma_answers.order_by('text')


class TakeExamForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=ExamAnswer.objects.none(),
        required=True,
        empty_label=None)

    class Meta:
        model = StudentExamAnswer
        fields = ('answer',)

    # Filter answers by question
    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        if question.type == 'objective':
            self.fields['answer'].queryset = question.exam_answers.order_by('text')
            self.fields['answer'].widget = django_forms.RadioSelect()
        else:
            self.fields['answer'].widget = django_forms.TextInput()


TakeExamFormSet = forms.modelformset_factory(
    StudentExamAnswer, form=TakeExamForm, extra=5
)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter your Question.'})
        }
