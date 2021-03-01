from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe


class Lecturer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, default='')

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' ' + self.user.other_name

    def photo_tag(self):
        return mark_safe('<img src="%s" width="70px" height="70px" />' % self.user.photo.url)

    photo_tag.short_description = 'Photo'
