from __future__  import absolute_import, unicode_literals
from celery import shared_task


from datetime import datetime, date, time
from core.models import Tma
from student.models import Student

now = datetime.now()
today = date.today()
current_time = time(now.hour, now.minute, now.second)
today_date = datetime.combine(today, current_time)

format_string = "%m-%d-%Y %H:%M:%S"

first_sem_reg_start = "10-06-2020 00:00:00"
first_sem_reg_close = "05-03-2020 00:00:00"
first_sem_reg_start_date = datetime.strptime(first_sem_reg_start, format_string)
first_sem_reg_close_date = datetime.strptime(first_sem_reg_close, format_string)


first_sem_tma1_start = "03-12-2020 00:00:00"
first_sem_tma1_close = "04-15-2020 00:00:00"
first_sem_tma1_start_date = datetime.strptime(first_sem_tma1_start, format_string)
first_sem_tma1_close_date = datetime.strptime(first_sem_tma1_close, format_string)

first_sem_tma2_start_date = "05-25-2020 00:00:00"
first_sem_tma2_close_date = "05-26-2020 00:00:00"
first_sem_tma2_start_date = datetime.strptime(first_sem_tma2_start_date, format_string)
first_sem_tma2_close_date = datetime.strptime(first_sem_tma2_close_date, format_string)

first_sem_tma3_start = "05-25-2020 00:00:00"
first_sem_tma3_close = "05-27-2020 00:00:00"
first_sem_tma3_start_date = datetime.strptime(first_sem_tma3_start, format_string)
first_sem_tma3_close_date = datetime.strptime(first_sem_tma3_close, format_string)


second_sem_reg_start = "05-31-2020 00:00:00"
second_sem_reg_close = "05-31-2020 00:00:00"
second_sem_reg_start_date = datetime.strptime(second_sem_reg_start, format_string)
second_sem_reg_close_date = datetime.strptime(second_sem_reg_close, format_string)


second_sem_tma1_start = "05-25-2020 00:00:00"
second_sem_tma1_close = "05-25-2020 00:00:00"
second_sem_tma1_start_date = datetime.strptime(second_sem_tma1_start, format_string)
second_sem_tma1_close_date = datetime.strptime(second_sem_tma1_close, format_string)

second_sem_tma2_start = "05-25-2020 00:00:00"
second_sem_tma2_close = "05-26-2020 00:00:00"
second_sem_tma2_start_date = datetime.strptime(second_sem_tma2_start , format_string)
second_sem_tma2_close_date = datetime.strptime(second_sem_tma2_close , format_string)

second_sem_tma3_start = "05-25-2020 00:00:00"
second_sem_tma3_close = "05-27-2020 00:00:00"
second_sem_tma3_start_date = datetime.strptime(second_sem_tma3_start , format_string)
second_sem_tma3_close_date = datetime.strptime(second_sem_tma3_close , format_string)


def first_semester_reg_open():
    if today_date > first_sem_reg_start_date:
        for student in Student.objects.all():
            if student.registration_open:
                pass
            else:
                student.registration_open = True
                student.save()

            if not student.semester_registered:
                pass
            else:
                student.semester_registered = False
                student.save()
            
def first_semester_reg_close():
    if today_date > first_sem_reg_close_date:
        for student in Student.objects.all():
            if not student.registration_open:
                pass
            else:
                student.registration_open = False
                student.save()
                
def second_sem_reg_open():
    if today_date > second_sem_reg_start_date:
        for student in Student.objects.all():
            if student.semester_registered:
                student.semester_registered = False
                student.save()
            else:
                pass

            if student.registration_open:
                pass
            else:
                student.registration_open = True
                student.save()

def second_semester_reg_close():
    if today_date > second_sem_reg_close_date:
        for student in Student.objects.all():
            if not student.registration_open:
                pass
            else:
                student.registration_open = False
                student.save()

def tma_status():
    if today_date > [first_sem_tma1_start_date,first_sem_tma2_start_date,first_sem_tma3_start_date,
                      second_sem_tma1_start,second_sem_tma2_start_date,second_sem_tma3_start]:
        for student in Student.objects.all():
            if student.tma_completed:
                student.tma_completed = False
                student.save()
            else:
                pass
            
def tma_close():
    if today_date == first_sem_tma1_close_date or today_date == second_sem_tma1_close_date:
        Tma.objects.filter(title='TMA 1').update(available=False)
    elif today_date == first_sem_tma2_close_date or today_date == second_sem_tma2_close_date:
        Tma.objects.first_sem_tma1_close_datefilter(title='TMA 2').update(available=False)
    elif today_date == first_sem_tma3_close_date or today_date == second_sem_tma3_close_date:
        Tma.objects.filter(title='TMA 3').update(available=False)



@shared_task(name = "print_msg_with_name")
def print_message(name, *args,**kwargs):
    print("Celery is Working!!! {} has implemented it correctly.".format(name))