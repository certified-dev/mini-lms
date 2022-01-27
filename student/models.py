from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe


from lecturer.models import Lecturer
from core.models import Course, Studycentre, Programme, Department
from core.models import Session

from student.choices import LEVEL, DESIGNATION, TYPES, TMA


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    study_centre = models.ForeignKey(Studycentre, on_delete=models.CASCADE, related_name='students')
    level = models.CharField(choices=LEVEL, max_length=10)
    courses = models.ManyToManyField(Course, related_name='students', blank=True)
    tmas = models.ManyToManyField('Tma', through='TakenTma')
    exams = models.ManyToManyField("Exam", related_name='registered_exam', blank=True)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    semesters_completed = models.PositiveSmallIntegerField(default=0)
    paid_compulsory_fee = models.BooleanField(default=False)
    wallet_balance = models.PositiveIntegerField(default=0)
    semester_registered = models.BooleanField(default=False)
    tma_completed = models.BooleanField(default=False)
    used_topup = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' ' + self.user.other_name

    def photo_tag(self):
        return mark_safe('<img src="%s" width="50px" height="50px" />' % self.user.photo.url)

    photo_tag.short_description = 'Photo'

    def get_unanswered_tma_questions(self, tma):
        answered_questions = self.student_tma_answers \
            .filter(answer__question__tma=tma) \
            .values_list('answer__question__pk', flat=True)
        questions = tma.tma_questions.exclude(pk__in=answered_questions).order_by('text')
        return questions

    def get_unanswered_exam_questions(self, exam):
        answered_questions = self.student_exam_answers \
            .filter(answer__question__exam=exam) \
            .values_list('answer__question__pk', flat=True)
        questions = exam.exam_questions.exclude(pk__in=answered_questions).order_by('text')
        return questions


class Tma(models.Model):
    admin = models.ForeignKey(
        Lecturer, on_delete=models.CASCADE, related_name='tmas')
    title = models.CharField(max_length=50, choices=TMA)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='tmas')
    done = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='tmas')

    def __str__(self):
        return '%s %s %s' % (self.course, self.title, self.session)


class TmaQuestion(models.Model):
    tma = models.ForeignKey(
        Tma, on_delete=models.CASCADE, related_name='tma_questions')
    text = models.CharField('Question', max_length=4000)

    def __str__(self):
        return self.text


class TmaAnswer(models.Model):
    question = models.ForeignKey(
        TmaQuestion, on_delete=models.CASCADE, related_name='tma_answers')
    text = models.CharField('Answer', max_length=500)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text


class TakenTma(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='taken_tmas')
    tma = models.ForeignKey(Tma, on_delete=models.CASCADE, related_name='taken_tmas')
    correct_answers = models.PositiveSmallIntegerField(default=0)
    incorrect_answers = models.PositiveSmallIntegerField(default=0)
    score = models.IntegerField()
    percentage = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s %s ' % (self.student, self.tma)


class Exam(models.Model):
    course = models.ForeignKey("core.Course", on_delete=models.CASCADE, related_name='exams')
    admin = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='exams')
    fee = models.PositiveIntegerField(default=1000)
    available = models.BooleanField(default=True)
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name='exams')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        x = datetime.now()
        return '%s %s/%s' % (self.course, x.year, self.session.semester)


class TakenExam(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='taken_exams')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='taken_exams')
    correct_answers = models.PositiveSmallIntegerField(default=0)
    incorrect_answers = models.PositiveSmallIntegerField(default=0)
    score = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s %s' % (self.student, self.exam)


class ExamQuestion(models.Model):
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name='exam_questions')
    text = models.CharField('Question', max_length=4000)
    type = models.CharField(choices=TYPES, max_length=15)

    def __str__(self):
        return self.text


class ExamAnswer(models.Model):
    question = models.ForeignKey(
        ExamQuestion, on_delete=models.CASCADE, related_name='exam_answers')
    text = models.CharField('Answer', max_length=500)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text


class StudentTmaAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_tma_answers')
    answer = models.ForeignKey(TmaAnswer, on_delete=models.CASCADE, related_name='+')


class StudentExamAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_exam_answers')
    answer = models.ForeignKey(ExamAnswer, on_delete=models.CASCADE, related_name='+')


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name='grade')
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='grades')
    score = models.IntegerField()
    designation = models.CharField(choices=DESIGNATION, max_length=20)

    def __str__(self):
        return '%s %s' % (self.student, self.session)


class DebitTransaction(models.Model):
    payer = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='debit_payer')
    description = models.CharField(max_length=500)
    title = models.CharField(max_length=15)
    cost = models.PositiveIntegerField()

    def __str__(self):
        return '%s' % self.title


class CreditTransaction(models.Model):
    payer = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='credit_payer')
    c_type = models.CharField(max_length=10)
    transaction_id = models.CharField(max_length=20)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return '%s' % self.transaction_id
