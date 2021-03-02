from django.db import models
from django.conf import settings
from student.models import Student
from lecturer.models import Lecturer


class Exam(models.Model):
    course = models.OneToOneField("core.Course", on_delete=models.CASCADE, related_name='exams')
    admin = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='exams')
    fee = models.PositiveIntegerField(default=1000)

    def __str__(self):
        return self.course.code


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=4000)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Answer', max_length=500)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text

class TakenExam(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='taken_exams')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='taken_exams')
    correct_answers = models.PositiveSmallIntegerField(default=0)
    incorrect_answers = models.PositiveSmallIntegerField(default=0)
    score = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s' % self.student


class QuestionAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+')
