from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.safestring import mark_safe

from core.models import Course, Studycentre, Programme, Tma, Answer, Department

LEVEL = (
    ('Access', 'Access'),
    ('100', '100'),
    ('200', '200'),
    ('300', '300'),
    ('400', '400')
)

CREDIT_TYPE = (
    ('CC/DC', 'CC/DC'),
    ('RRR', 'RRR')
)


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='student_dept')
    study_centre = models.ForeignKey(Studycentre, on_delete=models.CASCADE, related_name='center')
    level = models.CharField(choices=LEVEL, max_length=10, blank=True)
    courses = models.ManyToManyField(Course, related_name='registered_courses', blank=True)
    tmas = models.ManyToManyField(Tma, through='TakenTma')
    exams = models.ManyToManyField("exams.Exam", related_name="registered_exams")
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    paid_compulsory_fee = models.BooleanField(default=False)
    wallet_balance = models.PositiveIntegerField(default=0)
    semester_registered = models.BooleanField(default=False)
    tma_completed = models.BooleanField(default=False)
    used_topup = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' ' + self.user.other_name

    def photo_tag(self):
        return mark_safe('<img src="%s" width="70px" height="70px" />' % self.user.photo.url)

    photo_tag.short_description = 'Photo'

    def get_unanswered_questions(self, tma):
        answered_questions = self.tma_answers \
            .filter(answer__question__tma=tma) \
            .values_list('answer__question__pk', flat=True)
        questions = tma.questions.exclude(pk__in=answered_questions).order_by('text')
        return questions


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


class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='tma_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+')


class DebitTransaction(models.Model):
    payer = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='debit_payer')
    description = models.CharField(max_length=500)
    title = models.CharField(max_length=15)
    cost = models.PositiveIntegerField()

    def __str__(self):
        return '%s' % self.title


class CreditTransaction(models.Model):
    payer = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='credit_payer')
    type = models.CharField(max_length=5, choices=CREDIT_TYPE)
    transaction_id = models.CharField(max_length=10)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return '%s' % self.transaction_id
