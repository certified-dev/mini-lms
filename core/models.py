import math

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import mark_safe
from django.utils.text import Truncator

from lecturer.models import Lecturer

from markdown2 import markdown

STATES = (
    ('------', '------'),
    ('Abia', 'Abia'),
    ('Adamawa', 'Adamawa'),
    ('Akwa Ibom', 'Akwa ibom'),
    ('Anambra', 'Anambra'),
    ('Bauchi', 'Bauchi'),
    ('Benue', 'Benue'),
    ('Borno', 'Borno'),
    ('Cross River', 'Cross River'),
    ('Delta', 'Delta'),
    ('Ebonyi', 'Ebonyi'),
    ('Edo', 'Edo'),
    ('Enugu', 'Enugu'),
    ('Imo', 'Imo'),
    ('Plateau', 'Plateau'),
    ('Rivers', 'Rivers'),
    ('Lagos', 'Lagos'),
    ('Taraba', 'Taraba'),
    ('Abuja', 'Abuja'),
    ('Yola', 'Yola'),

)


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.username, filename)


def user_topic_directory_path(instance, filename):
    return 'user_{0}/{1}/{2}'.format(instance.lecturer.user.username, 'topic', filename)


class Semester(models.Model):
    title = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.title


class Session(models.Model):
    semester = models.OneToOneField(Semester, on_delete=models.CASCADE)
    start_date = models.DateField()
    close_date = models.DateField()
    registration_end = models.DateField()
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.semester.title


class Faculty(models.Model):
    name = models.CharField(max_length=30)
    dean = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = "Faculties"

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=50)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name='dept_faculty')

    def __str__(self):
        return self.name


class User(AbstractUser):
    other_name = models.CharField(max_length=20, null=True)
    photo = models.ImageField(
        upload_to=user_directory_path, default='placeholder/image.jpeg')
    phone = models.CharField(max_length=15, null=True, blank=True)
    birth_date = models.DateField()
    address = models.CharField(max_length=100, blank=True)
    birth_place = models.CharField(
        max_length=50, choices=STATES, default='Unknown')
    sex = models.CharField(max_length=10, default='------')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='student_faculty', blank=True,
                                null=True)
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    passport_uploaded = models.BooleanField(default=False)

    def __str__(self):
        return '%s %s %s' % (self.first_name, self.last_name, self.other_name)

    def full_name(self):
        full_name = '%s %s %s' % (
            self.first_name, self.last_name, self.other_name)
        return full_name.strip()

    def photo_tag(self):
        return mark_safe('<img src="%s" width="35px" height="35px" />' % self.photo.url)

    photo_tag.short_description = 'Photo'


class Programme(models.Model):
    name = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='program_department')

    def __str__(self):
        return self.name


class Course(models.Model):
    DESIGNATION = (
        ('Core', 'Core'),
        ('Elective', 'Elective'),
    )
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    designation = models.CharField(
        choices=DESIGNATION, max_length=15, null=True)
    code = models.CharField(max_length=8)
    credit_unit = models.SmallIntegerField()
    fee = models.PositiveIntegerField(null=True)
    lecturer = models.ForeignKey(
        Lecturer, on_delete=models.DO_NOTHING, blank=True, null=True)
    host_faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, null=True, blank=True)
    tma1_done = models.BooleanField(default=False)
    tma2_done = models.BooleanField(default=False)
    tma3_done = models.BooleanField(default=False)

    def __str__(self):
        return self.code


class Studycentre(models.Model):
    name = models.CharField(max_length=20, null=True)
    code = models.CharField(max_length=10, null=True)
    address = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name


class Expense(models.Model):
    name = models.CharField(max_length=50)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Tma(models.Model):
    TMA = (
        ('TMA 1', 'TMA 1'),
        ('TMA 2', 'TMA 2'),
        ('TMA 3', 'TMA 3'),
    )

    admin = models.ForeignKey(
        Lecturer, on_delete=models.CASCADE, related_name='tmas')
    title = models.CharField(max_length=50, choices=TMA)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='tmas')
    done = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name='tma_session')

    def __str__(self):
        return '%s %s %s' % (self.course, self.title, self.session)


class Question(models.Model):
    tma = models.ForeignKey(
        Tma, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=4000)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Answer', max_length=500)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text


class Topic(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField(max_length=100000)
    files = models.FileField(
        upload_to=user_topic_directory_path, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    lecturer = models.ForeignKey(
        Lecturer, related_name='topics', on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, related_name='topics', on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject

    def get_page_count(self):
        count = self.posts.count()
        pages = count / 4
        return math.ceil(pages)

    def has_many_pages(self, count=None):
        if count is None:
            count = self.get_page_count()
        return count > 6

    def get_page_range(self):
        count = self.get_page_count()
        if self.has_many_pages(count):
            return range(1, 5)
        return range(1, count + 1)

    def get_last_ten_posts(self):
        return self.posts.order_by('-created_at')[:10]

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))


class Post(models.Model):
    message = models.TextField(max_length=100000)
    topic = models.ForeignKey(
        Topic, related_name='posts', on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        User, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    updated_by = models.ForeignKey(
        User, null=True, related_name='+', on_delete=models.CASCADE)

    def __str__(self):
        truncated_message = Truncator(self.message)
        return truncated_message.chars(30)

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))
