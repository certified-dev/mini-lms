from django import template
from django.db.models import Sum

from student.models import StudentAnswer
import hashlib

register = template.Library()


@register.simple_tag
def marked_answer(user, opt):
    studentanswer = StudentAnswer.objects.filter(student=user.student, answer=opt)
    if studentanswer:
        if opt.is_correct:
            return 'correct'
        return 'wrong'
    return ''
