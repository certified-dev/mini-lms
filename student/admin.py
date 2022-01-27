from django.contrib import admin

from core.models import Expense
from student.models import TakenExam, TakenTma, Tma, TmaQuestion, ExamQuestion, TmaAnswer, ExamAnswer, \
    CreditTransaction, DebitTransaction, Exam, Student

admin.site.register(TakenTma)
admin.site.register(TakenExam)
admin.site.register(Tma)
admin.site.register(Exam)
admin.site.register(TmaQuestion)
admin.site.register(ExamQuestion)
admin.site.register(Expense)
admin.site.register(TmaAnswer)
admin.site.register(ExamAnswer)
admin.site.register(CreditTransaction)
admin.site.register(DebitTransaction)


class StudentAdmin(admin.ModelAdmin):
    list_display = ('photo_tag', 'user', 'study_centre', 'programme', 'level', 'wallet_balance')

    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Details', {'fields': ('department', 'level', 'programme', 'study_centre', 'courses','exams', 'wallet_balance')}),
        ('Actions', {'fields': ('semester_registered', 'paid_compulsory_fee', 'tma_completed',  'semesters_completed')})
    )


readonly_field = ['photo_tag']

admin.site.register(Student, StudentAdmin)
