from __future__ import unicode_literals

from datetime import date

from core.models import User, Expense, Course, Topic, Post, Session
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Sum
# from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, UpdateView
from django.views.generic import ListView
from mini_lms.decorators import student_required, anonymous_required
from student.forms import StudentSignUpForm, CourseRegistrationForm, TakeTmaForm, PostForm, \
    ExamRegistrationForm, TakeExamFormSet
from student.models import CreditTransaction, DebitTransaction, TmaQuestion, Exam, Student, TakenTma, Tma, TakenExam

# from weasyprint import HTML

RRR_TopUp = 128709876406


class PassRequestToFormMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


@method_decorator([anonymous_required], name='dispatch')
class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.user = form.save()
        auth_login(self.request, self.user)
        student = self.user.student
        student.session = Session.objects.get(active=True)
        student.save()
        messages.success(self.request, 'Student Account Created!')
        return redirect('student:dashboard')


@login_required
@student_required
def dashboard(request):
    student = request.user.student
    courses = student.courses.all()
    student_courses = student.courses.values_list('pk', flat=True)
    taken_tmas = student.tmas.values_list('pk', flat=True)
    tmas = Tma.objects.filter(course__in=student_courses).exclude(pk__in=taken_tmas)
    session = date.today().month
    return render(request, 'student/dashboard.html', {'courses': courses,
                                                      'tmas': tmas,
                                                      'session': session})


@login_required
@student_required
def wallet(request):
    student = request.user.student
    debit_payments = DebitTransaction.objects.filter(payer=student)
    deposit_payments = CreditTransaction.objects.filter(payer=student)

    if request.method == 'POST':
        rrr = int(request.POST.get('rrr'))
        if rrr == RRR_TopUp:
            student.wallet_balance += 20000
            student.used_topup = True
            student.save()

            CreditTransaction.objects.create(payer=student, c_type='RRR', transaction_id=rrr, amount=20000)
            messages.success(request, 'Wallet successfully credited with ₦20,000!!!')

    return render(request, 'student/wallet.html', {'debit_payments': debit_payments,
                                                   'deposit_payments': deposit_payments})


# def identity_card(request):
#     response = HttpResponse(content_type='application/pdf;')
#     response['Content-Disposition'] = 'inline; filename={username}-id-card.pdf'.format(username=request.user.username)
#     html = render_to_string('student/pdf/id_card.html', {'user': request.user})
#     HTML(string=html).write_pdf(response)
#     return response


@method_decorator([login_required, student_required, ], name='dispatch')
class SemesterRegisterView(ListView):
    template_name = 'student/sem_reg.html'
    context_object_name = 'expenses'

    def get_context_data(self, **kwargs):
        active_session = Session.objects.get(active=True)
        if date.today() < active_session.registration_end:
            reg_open = True
        else:
            reg_open = False

        if not self.request.user.student.paid_compulsory_fee:
            cost = Expense.objects.aggregate(Sum('amount'))['amount__sum']
            extra_context = {
                'cost': cost,
                'semester': True,
                'reg_open': reg_open,
                'session': str(date.today().year) + '/' + active_session.semester.title
            }
            kwargs.update(extra_context)
        else:
            cost = Expense.objects.filter(name__in=['Semester Fee']).aggregate(
                Sum('amount'))['amount__sum']
            extra_context = {
                'cost': cost,
                'reg_open': reg_open,
                'session': str(date.today().year) + '/' + active_session.semester.title,
                'semester': True
            }
            kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        if not self.request.user.student.paid_compulsory_fee:
            queryset = Expense.objects.all()
        else:
            queryset = Expense.objects.filter(name__in=['Semester Fee'])
        return queryset


@login_required
@student_required
def semester_payment(request):
    if request.method == 'GET':

        student = request.user.student
        if not student.paid_compulsory_fee:
            expenses = Expense.objects.all()
            semester_cost = expenses.aggregate(Sum('amount'))['amount__sum']
        else:
            expenses = Expense.objects.filter(name__in=['Semester Fee'])
            semester_cost = expenses.aggregate(Sum('amount'))['amount__sum']

        if not student.paid_compulsory_fee:
            student.paid_compulsory_fee = True

        student.semester_registered = True
        student.wallet_balance = student.wallet_balance - semester_cost

        for item in expenses:
            DebitTransaction.objects.create(
                payer=student,
                description="Semester Reg",
                title=item.name,
                cost=item.amount)

        student.save()
        messages.success(request, 'Semester Registered successfully!')
        return redirect('student:student_courses')


# def semester_slip(request):
#     response = HttpResponse(content_type='application/pdf;')
#     response['Content-Disposition'] = 'inline; filename=document.pdf'
#     html = render_to_string('student/pdf/semester_slip.html', {'user': request.user})
#     HTML(string=html).write_pdf(response)
#     return response


@method_decorator([login_required, student_required], name='dispatch')
class CourseRegistrationView(PassRequestToFormMixin, UpdateView):
    model = Student
    form_class = CourseRegistrationForm
    template_name = 'student/course_register.html'
    success_url = reverse_lazy('student:course_pay')

    def get_context_data(self, **kwargs):
        active_session = Session.objects.get(active=True)
        session, reg_open, user = '', '', self.request.user
        if date.today() < active_session.registration_end:
            reg_open = True

        if int(user.student.semesters_completed) % 2:
            session = "2"
        else:
            session = "1"
        
        reg_courses = user.student.courses.all().values_list('pk', flat=True)
        

        courses = Course.objects.filter(semester__title=session, level=user.student.level,
                                        host_faculty=self.request.user.faculty)
        others = Course.objects.filter(host_faculty__name="General Studies", level=user.student.level,
                                       semester__title=session)
        student_courses = self.request.user.student.courses.all()
        reg_check = self.request.user.student.courses.aggregate(Sum('credit_unit'))['credit_unit__sum']
        form_stat = courses | others


        extra_context = {
            'semester_courses': form_stat,
            'reg_check': reg_check,
            'session': str(date.today().year) + '/' + active_session.semester.title,
            'student_courses': list(student_courses.values_list('code', flat=True)),
            'regged_courses': student_courses,
            'form_stat': form_stat.exclude(pk__in=reg_courses),
            'reg_open': reg_open
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_object(self):
        return self.request.user.student

    def form_valid(self, form):
        student = self.request.user.student
        courses_cost = student.courses.all().aggregate(Sum('fee'))['fee__sum']
        if courses_cost:
            student.wallet_balance += courses_cost
            student.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Check Your Selection And Try Again.')
        return super(CourseRegistrationView, self).form_invalid(form)


@login_required
@student_required
def course_payment(request):
    if request.method == 'GET':
        student = request.user.student
        courses_cost = student.courses.aggregate(Sum('fee'))['fee__sum']
        student.wallet_balance = student.wallet_balance - courses_cost
        student.save()

        for item in student.courses.all():
            if not DebitTransaction.objects.filter(title=item.code).exists():
                DebitTransaction.objects.create(
                    payer=student,
                    description="Course",
                    title=item.code,
                    cost=item.fee)

        messages.success(request, 'Courses Registered successfully!')
        return redirect('student:student_courses')


# def courses_slip(request):
#     response = HttpResponse(content_type='application/pdf;')
#     response['Content-Disposition'] = 'inline; filename=document.pdf'
#     html = render_to_string('student/pdf/course_slip.html', {'user': request.user})
#     HTML(string=html).write_pdf(response)
#     return response


@method_decorator([login_required, student_required], name='dispatch')
class StudentCoursesView(ListView):
    model = Course
    ordering = ('code',)
    context_object_name = 'courses'
    template_name = 'student/course_list.html'

    def get_context_data(self, **kwargs):
        check = self.request.user.student.courses.aggregate(Sum('credit_unit'))['credit_unit__sum']
        active_session = Session.objects.get(active=True)
        extra_context = {
            'check': check,
            'session': str(date.today().year) + '/' + active_session.semester.title,
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = None
        if self.request.user.student.semester_registered:
            if self.request.user.student.courses.count() < 1:
                messages.warning(self.request, 'Courses Not Registered')
            else:
                queryset = self.request.user.student.courses.all()
        else:
            messages.warning(self.request, 'Semester not Registered!')

        return queryset


@method_decorator([login_required, student_required], name='dispatch')
class TmaListView(ListView):
    model = Tma
    ordering = ('course',)
    context_object_name = 'tmas'
    template_name = 'student/tma/tma_list.html'

    def get_queryset(self):
        student = self.request.user.student
        student_courses = student.courses.values_list('pk', flat=True)
        taken_tmas = student.tmas.values_list('pk', flat=True)
        queryset = Tma.objects.filter(course__in=student_courses) \
            .exclude(pk__in=taken_tmas) \
            .annotate(questions_count=Count('tma_questions')) \
            .filter(questions_count__gt=0)
        return queryset

    def get_context_data(self, **kwargs):
        extra_context = {
            'taken_tmas': self.request.user.student.taken_tmas \
                .select_related('tma', 'tma__course') \
                .order_by('tma__title'),
            'tma_page': True
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)


@method_decorator([login_required, student_required], name='dispatch')
class ExamListView(ListView):
    model = Exam
    ordering = ('created',)
    context_object_name = 'exams'
    template_name = 'student/exam_list.html'

    # def get_queryset(self):
    #     student = self.request.user.student
    #     taken_exams = TakenExam.objects.filter(student=student).exam.values_list('pk', flat=True)
    #     queryset = student.exams.exclude(pk__in=taken_exams) \
    #         .annotate(question_exam_count=Count('question_exam')) \
    #         .filter(question_exam_count__gt=0)
    #     return queryset

    def get_context_data(self, **kwargs):
        active_session = Session.objects.get(active=True)
        extra_context = {
            #  'taken_exams': self.request.user.student.takenexam_exam \
            #     .select_related('exam', 'exam__course') \
            #     .order_by('exam__created'),
            'exam_page': True,
            'session': str(date.today().year) + '/' + active_session.semester.title,
        }
     
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)


@login_required
@student_required
def take_tma(request, pk):
    tma = get_object_or_404(Tma, pk=pk)
    student = request.user.student

    if student.tmas.filter(pk=pk).exists():
        return redirect('student:tma_result', pk)

    total_questions = tma.tma_questions.count()
    unanswered_questions = student.get_unanswered_tma_questions(tma)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeTmaForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                student_answer = form.save(commit=False)
                student_answer.student = student
                student_answer.save()
                if student.get_unanswered_tma_questions(tma).exists():
                    return redirect('student:take_tma', pk)
                else:
                    all_answers = student.student_tma_answers.filter(answer__question__tma=tma)
                    correct_answers = all_answers.filter(answer__is_correct=True).count()
                    incorrect_answers = all_answers.filter(answer__is_correct=False).count()

                    percentage = round((correct_answers / total_questions) * 100.0, 2)
                    TakenTma.objects.create(student=student,
                                            tma=tma,
                                            score=correct_answers,
                                            correct_answers=correct_answers,
                                            incorrect_answers=incorrect_answers,
                                            percentage=percentage)
                    # tma_course = tma.course
                    # courses = student.courses.all()

                    # if '1' in tma.title:
                    #     for course in courses:
                    #         if course == tma_course:
                    #             course.tma1_done = True
                    #             course.save()
                    # elif '2' in tma.title:
                    #    for course in courses:
                    #         if course == tma_course:
                    #             course.tma2_done = True
                    #             course.save()
                    # else:
                    #    for course in courses:
                    #         if course == tma_course:
                    #             course.tma3_done = True
                    #             course.save()

                    all_taken_tma = student.taken_tmas.all()
                    recent = all_taken_tma.latest('date')
                    truth_box = []
                    for course in student.courses.all():
                        for taken_tma in all_taken_tma:
                            if course == taken_tma.tma.course:
                                truth_box.append(True)

                    if False not in truth_box:
                        student.tma_completed = True
                        student.save()

                    messages.success(request,
                                     'Congratulations! You completed %s - %s with success! You scored %s/%s' % (
                                         recent.tma.course.code, recent.tma.title, correct_answers, total_questions))
                    return redirect('student:tma_result', pk)

    else:
        form = TakeTmaForm(question=question)

    return render(request, 'student/tma/take_tma_form.html', {
        'take_tma': True,
        'tma': tma,
        'question': question,
        'form': form,
        'progress': progress,
        'answered_questions': total_questions - total_unanswered_questions,
        'total_questions': total_questions
    })


@method_decorator([login_required, student_required], name='dispatch')
class TmaResultsView(View):
    template_name = 'student/tma/tma_result.html'

    def get(self, request, **kwargs):
        tma = Tma.objects.get(id=kwargs['pk'])
        taken_tma = TakenTma.objects.filter(student=request.user.student, tma=tma)
        if not taken_tma:
            """
            Don't show the result if the user didn't attempted the tma
            """
            return render(request, '404.html')
        questions = TmaQuestion.objects.filter(tma=tma)

        messages.success(request,
                         taken_tma[0].tma.course.code + ' - ' + taken_tma[0].tma.title + ' Completed!!!')

        # questions = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'questions': questions,
                                                    'tma': tma,
                                                    'percentage': taken_tma[0].percentage})


def ajax_taken_tma(request, pk):
    taken_tma = get_object_or_404(TakenTma, pk=pk)
    data = dict()
    if request.method == 'GET':
        data['html_form'] = render_to_string('student/includes/taken_tma.html',
                                             {'taken_tma': taken_tma,
                                              'total_questions': taken_tma.tma.tma_questions.count()},
                                             request=request)
    return JsonResponse(data)


@method_decorator([login_required, student_required, ], name='dispatch')
class ExamRegistrationView(PassRequestToFormMixin, UpdateView):
    model = Student
    form_class = ExamRegistrationForm
    template_name = 'student/exam_reg.html'
    success_url = reverse_lazy('student:exam_pay')

    def get_context_data(self, **kwargs):
        
        student_courses = self.request.user.student.courses.all()
        student_exams = self.request.user.student.exams.all()
        json_exam = student_exams.values_list('pk', flat=True)
        exam_to_reg = Exam.objects.filter(course__in=student_courses).exclude(pk__in=json_exam)

        active_session = Session.objects.get(active=True)
        extra_context = {
            'student_courses': student_courses,
            'student_exams': student_exams,
            'json_exam': list(json_exam),
            'exam_to_reg': exam_to_reg,
            'session': str(date.today().year) + '/' + active_session.semester.title
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_object(self):
        return self.request.user.student

    def form_valid(self, form):
        student = self.request.user.student
        exams_cost = student.exams.all().aggregate(Sum('fee'))['fee__sum']
        if exams_cost:
            student.wallet_balance += exams_cost
            student.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Check Your Selection And Try Again.')
        return super(ExamRegistrationView, self).form_invalid(form)


@login_required
@student_required
def exam_payment(request):
    if request.method == 'GET':
        student = request.user.student
        exam_cost = student.exams.aggregate(Sum('fee'))['fee__sum']
        student.wallet_balance = student.wallet_balance - exam_cost

        for item in student.exams.all():
            if not DebitTransaction.objects.filter(title=item.course).exists():
                DebitTransaction.objects.create(
                    payer=student,
                    description="Exam",
                    title=item.course,
                    cost=item.fee)

        student.save()
        messages.success(request, 'Exams Registered successfully!')
        return redirect('student:exam_reg')


# def exams_slip(request):
#     response = HttpResponse(content_type='application/pdf;')
#     response['Content-Disposition'] = 'inline; filename=document.pdf'
#     html = render_to_string('student/pdf/exam_slip.html', {'user': request.user})
#     HTML(string=html).write_pdf(response)
#     return response


@login_required
@student_required
def take_exam(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    student = request.user.student

    total_questions = exam.exam_questions.count()
    unanswered_questions = student.get_unanswered_exam_questions(exam)
    total_unanswered_questions = unanswered_questions.count()
    question = unanswered_questions.first()

    if request.method == 'POST':
        formset= TakeExamFormSet(question=question, data=request.POST)
        if formset.is_valid():
            with transaction.atomic():
                student_answer = formset.save(commit=False)
                student_answer.student = student
                student_answer.save()

                if student.get_unanswered_exam_questions(exam).exists():
                    return redirect('student:take_exam', pk)
                else:
                    all_answers = student.student_exam_answers.filter(answer__question__exam=exam)
                    correct_answers = all_answers.filter(answer__is_correct=True).count()
                    incorrect_answers = all_answers.filter(answer__is_correct=False).count()

                    percentage = round((correct_answers / total_questions) * 100.0, 2)
                    TakenTma.objects.create(student=student,
                                            exam=exam,
                                            score=correct_answers,
                                            correct_answers=correct_answers,
                                            incorrect_answers=incorrect_answers,
                                            percentage=percentage)

                    all_taken_exam = student.taken_exam.all()
                    recent = all_taken_exam.latest('date')

                    messages.success(request,
                                     'Congratulations! You completed %s examination! You scored %s/%s' % (
                                         recent.tma.course, correct_answers, total_questions))
                    return redirect('student:exam_result', pk)
    else:
        formset = TakeExamFormSet(question=question)

    return render(request, 'student/exam/take_exam_form.html', {
        'take_tma': True,
        'exam': exam,
        'question': question,
        'formset': formset,
        'answered_questions': total_questions - total_unanswered_questions,
        'total_questions': total_questions
    })


@method_decorator([login_required, student_required], name='dispatch')
class ExamResultView(View):
    pass


@method_decorator([login_required, student_required], name='dispatch')
class StudentProjectsView(CreateView):
    pass


@method_decorator([login_required, student_required], name='dispatch')
class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'student/board/topics.html'
    paginate_by = 5

    def get_queryset(self):
        courses_id = self.request.user.student.courses.values_list('pk', flat=True)
        queryset = Topic.objects.filter(course_id__in=courses_id).order_by('-last_updated').annotate(
            replies=Count('posts'))
        return queryset


@method_decorator([login_required, student_required], name='dispatch')
class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'student/board/topic_posts.html'
    paginate_by = 4

    def get_context_data(self, session_key=None, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True

        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, pk=self.kwargs.get('pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


@login_required
@student_required
def reply_topic(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            topic_url = reverse('student:topic_posts', kwargs={'pk': pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            messages.success(request, 'Comment Added Successfully!')
            return redirect(topic_post_url)
        else:
            messages.error(request, 'Check Your Post and Try Again!!!')

    else:
        form = PostForm()

    return render(request, 'student/board/reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message',)
    template_name = 'student/board/reply_topic.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        messages.success(self.request, 'Comment Updated Successfully!')
        return redirect('student:topic_posts', pk=post.topic.pk)

    def form_invalid(self, form):
        messages.error(self.request, 'Check Your Input And Try Again.')
        return super(PostUpdateView, self).form_invalid(form)
