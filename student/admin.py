from django.contrib import admin

from student.models import Payment, Student, TakenTma, StudentAnswer

admin.site.register(TakenTma)
admin.site.register(StudentAnswer)
admin.site.register(Payment)


class StudentAdmin(admin.ModelAdmin):
    list_display = ('photo_tag', 'user', 'study_centre', 'programme', 'level', 'wallet_balance')

    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Details', {'fields': ('department', 'level', 'programme', 'study_centre', 'courses', 'wallet_balance')}),
        ('Actions', {'fields': ('semester_registered', 'paid_compulsory_fee', 'tma_completed')})
    )


readonly_field = ['photo_tag']

admin.site.register(Student, StudentAdmin)
