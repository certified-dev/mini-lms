from __future__ import absolute_import, unicode_literals
from celery import shared_task

from datetime import datetime, date, time
from core.models import Tma
from student.models import Student
from core.models import Session

now = datetime.now()
today = date.today()
current_time = time(now.hour, now.minute, now.second)
today_date = datetime.combine(today, current_time)

if today > active_session.close_date:
    for session in Session.objects.all():
        session.active = False
        session.save()

for session in Session.objects.all():
    if today == session.start_date:
        session.active = True
        session.save()

active_session = Session.objects.get(active=True)

if today == active_session.close_date:
     students = Student.objects.all()
     for student in students:
         student.semester_registered = False

@shared_task(name="print_msg_with_name")
def print_message(name, *args, **kwargs):
    print("Celery is Working!!! {} has implemented it correctly.".format(name))
