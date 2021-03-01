from django.contrib import admin

from lecturer.models import Lecturer


class LecturerAdmin(admin.ModelAdmin):
    list_display = ('photo_tag', 'user')


readonly_field = ['photo_tag']

admin.site.register(Lecturer, LecturerAdmin)
