from django.contrib import admin
from django.contrib.auth.models import Group

from core.models import Faculty, Department, Course, Studycentre, User, Expense, Programme, Tma, \
    Question, Answer, Topic, Post, Session, Semester

admin.site.register(Course)
admin.site.register(Studycentre)
admin.site.register(Programme)
admin.site.register(Tma)
admin.site.register(Question)
admin.site.register(Expense)
admin.site.register(Answer)
admin.site.register(Post)
admin.site.register(Session)
admin.site.register(Semester)

admin.site.unregister(Group)


class DepartmentsAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty')


admin.site.register(Department, DepartmentsAdmin)


class FacultiesAdmin(admin.ModelAdmin):
    list_display = ('name', 'dean', 'email')


admin.site.register(Faculty, FacultiesAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = ('photo_tag', 'username', 'email', 'is_student', 'is_lecturer')

    # list_filter = ('is_staff',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': (
            'first_name', 'other_name', 'last_name', 'sex', 'birth_date', 'birth_place', 'phone', 'email', 'address')}),
        ('School info', {'fields': ('faculty',)}),
        ('Permissions', {'fields': ('is_student', 'is_lecturer')}),
        ('Actions', {'fields': ('passport_uploaded',)}),
        ('Others', {'fields': ('date_joined', 'last_login')}),
    )


readonly_field = ['photo_tag']
admin.site.register(User, UserAdmin)

admin.site.register(Topic)
