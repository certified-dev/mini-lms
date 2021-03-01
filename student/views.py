from __future__ import unicode_literals

from datetime import date

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DetailView
from django.views.generic import ListView
from weasyprint import HTML

from core.models import User, Tma, Expense, Course, Topic, Post, Session
from mini_lms.decorators import student_required, anonymous_required
from student.forms import StudentSignUpForm, CourseRegistrationForm, TakeTmaForm, PhotoUploadForm, PostForm, \
    ExamRegistrationForm
from student.models import Student, TakenTma, Payment
from student.tasks import today_date, first_sem_reg_start_date, second_sem_reg_start_date


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
        if today_date > first_sem_reg_start_date or today_date > second_sem_reg_start_date:
            pass
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.user = form.save()
        auth_login(self.request, self.user)
        student = self.user.student
        student.session = Session.objects.get(active=True)
        if today_date > first_sem_reg_start_date or today_date > second_sem_reg_start_date:
            student.registration_open = True
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
    payments = Payment.objects.filter(owner=request.user.student)
    return render(request, 'student/wallet.html', {'payments': payments})


# @method_decorator([login_required, student_required], name='dispatch')
# class PhotoUpdateView(UpdateView):
#     model = User
#     form_class = PhotoUploadForm
#     template_name = 'student/upload_photo.html'
#     success_url = reverse_lazy('student:dashboard')

#     def get_object(self):
#         return self.request.user

#     def form_valid(self, form):
#         self.request.user.passport_uploaded = True
#         messages.success(self.request, 'Photo uploaded Successfully!')
#         return super().form_valid(form)


def identity_card(request):
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename={username}-id-card.pdf'.format(username=request.user.username)
    html = render_to_string('student/pdf/id_card.html', {'user': request.user})
    HTML(string=html).write_pdf(response)
    return response


@method_decorator([login_required, student_required, ], name='dispatch')
class SemesterRegisterView(ListView):
    template_name = 'student/sem_reg.html'
    context_object_name = 'expenses'

    def get_context_data(self, **kwargs):
        if not self.request.user.student.paid_compulsory_fee:
            cost = Expense.objects.aggregate(Sum('amount'))['amount__sum']
            extra_context = {'cost': cost, 'semester': True}
        else:
            cost = \
                Expense.objects.filter(name__in=['Jamb Regularisation Fee', 'Examination Levy']).aggregate(
                    Sum('amount'))[
                    'amount__sum']
            extra_context = {'cost': cost, 'semester': True}

        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        if not self.request.user.student.paid_compulsory_fee:
            queryset = Expense.objects.all()
        else:
            queryset = Expense.objects.filter(name__in=['Jamb Regularisation Fee', 'Examination Levy'])
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
            expenses = Expense.objects.filter(name__in=['Jamb Regularisation Fee', 'Examination Levy'])
            semester_cost = expenses.aggregate(Sum('amount'))['amount__sum']

        if student.paid_compulsory_fee:
            pass
        else:
            student.paid_compulsory_fee = True

        student.semester_registered = True
        student.wallet_balance = student.wallet_balance - semester_cost

        for item in expenses:
            Payment.objects.create(
                owner=request.user.student,
                description="Semester",
                title=item.name,
                cost=item.amount)

        student.save()
        messages.success(request, 'Semester Registered successfully!')
        return redirect('student:student_courses')


def semester_slip(request):
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=document.pdf'
    html = render_to_string('student/pdf/semester_slip.html', {'user': request.user})
    HTML(string=html).write_pdf(response)
    return response


@method_decorator([login_required, student_required], name='dispatch')
class CourseRegistrationView(PassRequestToFormMixin, UpdateView):
    model = Student
    form_class = CourseRegistrationForm
    template_name = 'student/course_register.html'
    success_url = reverse_lazy('student:course_pay')

    def get_context_data(self, **kwargs):
        courses = Course.objects.filter(level=self.request.user.student.level, host_faculty=self.request.user.faculty)
        others = Course.objects.filter(host_faculty__name="General Studies", level=self.request.user.student.level)
        session = date.today().month

        student_courses = list(self.request.user.student.courses.all().values_list('code', flat=True))
        reg_check = self.request.user.student.courses.aggregate(Sum('credit_unit'))['credit_unit__sum']

        extra_context = {
            'session': session,
            'level_courses': courses | others,
            'reg_check': reg_check,
            'student_courses': student_courses
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_object(self):
        return self.request.user.student

    def form_valid(self, form):
        student = self.request.user.student
        refund = student.courses.aggregate(Sum('fee'))['fee__sum']
        courses_payment = Payment.objects.filter(owner=self.request.user.student, description="Course")

        if refund is None:
            pass
        else:
            student.wallet_balance = student.wallet_balance + refund
            courses_payment.delete()

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

        for item in student.courses.all():
            Payment.objects.create(
                owner=request.user.student,
                description="Course",
                title=item.code,
                cost=item.fee)

        student.save()
        messages.success(request, 'Courses Registered successfully!')
        return redirect('student:student_courses')


def courses_slip(request):
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=document.pdf'
    html = render_to_string('student/pdf/course_slip.html', {'user': request.user})
    HTML(string=html).write_pdf(response)
    return response


@method_decorator([login_required, student_required], name='dispatch')
class StudentCoursesView(ListView):
    model = Course
    ordering = ('code',)
    context_object_name = 'courses'
    template_name = 'student/course_list.html'

    def get_context_data(self, **kwargs):
        check = self.request.user.student.courses.aggregate(Sum('credit_unit'))['credit_unit__sum']
        session = date.today().month
        extra_context = {
            'check': check,
            'session': session
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
    template_name = 'student/tma_list.html'

    def get_queryset(self):
        student = self.request.user.student
        student_courses = student.courses.values_list('pk', flat=True)
        taken_tmas = student.tmas.values_list('pk', flat=True)
        queryset = Tma.objects.filter(course__in=student_courses) \
            .exclude(pk__in=taken_tmas) \
            .annotate(questions_count=Count('questions')) \
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


@login_required
@student_required
def take_tma(request, pk):
    tma = get_object_or_404(Tma, pk=pk)
    student = request.user.student

    if student.tmas.filter(pk=pk).exists():
        return render(request, 'student/taken_tma.html')

    total_questions = tma.questions.count()
    unanswered_questions = student.get_unanswered_questions(tma)
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
                if student.get_unanswered_questions(tma).exists():
                    return redirect('student:take_tma', pk)
                else:
                    correct_answers = student.tma_answers.filter(answer__question__tma=tma,
                                                                 answer__is_correct=True).count()
                    incorrect_answers = student.tma_answers.filter(answer__question__tma=tma,
                                                                   answer__is_correct=False).count()
                    percentage = round((correct_answers / total_questions) * 100.0, 2)
                    TakenTma.objects.create(student=student,
                                            tma=tma,
                                            score=correct_answers,
                                            correct_answers=correct_answers,
                                            incorrect_answers=incorrect_answers,
                                            percentage=percentage)

                    if '1' in tma.title:
                        tma_course = tma.course
                        course = student.courses.get(id=tma_course.id)
                        course.tma1_done = True
                        course.save()
                        student.save()

                    elif '2' in tma.title:
                        tma_course = tma.course
                        course = student.courses.get(id=tma_course.id)
                        course.tma2_done = True
                        course.save()
                        student.save()
                    else:
                        tma_course = tma.course
                        course = student.courses.get(id=tma_course.id)
                        course.tma3_done = True
                        course.save()
                        student.save()

                    taken_tma = TakenTma.objects.order_by('id')[0]

                    # student_takentma = TakenTma.objects.filter(student=request.user.student)
                    # student_courses = student.courses.all()

                    messages.success(request,
                                     taken_tma.tma.course.code + ' [' + taken_tma.tma.title + ']' + ' Completed!!!')
                    return redirect('student:tma_list')

    else:
        form = TakeTmaForm(question=question)

    return render(request, 'student/take_tma_form.html', {
        'take_tma': True,
        'tma': tma,
        'question': question,
        'form': form,
        'progress': progress,
        'answered_questions': total_questions - total_unanswered_questions,
        'total_questions': total_questions
    })


def ajax_taken_tma(request, pk):
    taken_tma = get_object_or_404(TakenTma, pk=pk)
    data = dict()
    if request.method == 'GET':
        data['html_form'] = render_to_string('student/includes/taken_tma.html',
                                             {'taken_tma': taken_tma,
                                              'total_questions': taken_tma.tma.questions.count()},
                                             request=request)
    return JsonResponse(data)


@method_decorator([login_required, student_required, ], name='dispatch')
class ExamRegistrationView(PassRequestToFormMixin, UpdateView):
    model = Student
    form_class = ExamRegistrationForm
    template_name = 'student/exam_reg.html'
    success_url = reverse_lazy('student:exam_pay')

    def get_context_data(self, **kwargs):
        student_exams = list(self.request.user.student.exams.all().values_list('course__code', flat=True))
        extra_context = {
            'student_exams': student_exams
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_object(self):
        return self.request.user.student

    def form_valid(self, form):
        student = self.request.user.student
        refund = student.exams.aggregate(Sum('fee'))['fee__sum']
        exams_payment = Payment.objects.filter(owner=self.request.user.student, description="Exam")
        if refund is None:
            pass
        else:
            student.wallet_balance = student.wallet_balance + refund
            exams_payment.delete()

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
            Payment.objects.create(
                owner=request.user.student,
                description="Exam",
                title=item.course,
                cost=item.fee)

        student.save()
        messages.success(request, 'Exams Registered successfully!')
        return redirect('student:exam_reg')


def exams_slip(request):
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=document.pdf'
    html = render_to_string('student/pdf/exam_slip.html', {'user': request.user})
    HTML(string=html).write_pdf(response)
    return response


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
        return super(ExamRegistrationView, self).form_invalid(form)