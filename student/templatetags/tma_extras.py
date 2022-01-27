from django import template

from student.models import StudentTmaAnswer, StudentExamAnswer

register = template.Library()


@register.simple_tag
def marked_tma_answer(user, opt):
    student_tma_answer = StudentTmaAnswer.objects.filter(student=user.student, answer=opt)
    if student_tma_answer:
        if opt.is_correct:
            return 'correct'
        return 'wrong'
    return ''


@register.simple_tag
def marked_exam_answer(user, opt):
    student_exam_answer = StudentExamAnswer.objects.filter(student=user.student, answer=opt)
    if student_exam_answer:
        if opt.is_correct:
            return 'correct'
        return 'wrong'
    return ''


@register.simple_tag
def user_answer(user, opt):
    student_tma_answer = StudentTmaAnswer.objects.filter(student=user.student, answer=opt)
    if student_tma_answer:
        return True
