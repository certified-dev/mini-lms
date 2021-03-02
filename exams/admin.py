from django.contrib import admin
from .models import Exam,Question,Answer,TakenExam,QuestionAnswer

admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(TakenExam)
admin.site.register(Answer)
admin.site.register(QuestionAnswer)
