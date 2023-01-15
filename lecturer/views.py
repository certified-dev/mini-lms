import json, requests
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, ListView, DetailView

from core.models import User, Topic, Post, Course, Session
from mini_lms.decorators import lecturer_required, anonymous_required
from lecturer.forms import LecturerSignUpForm, QuestionForm, BaseAnswerInlineFormSet, TmaForm, \
    NewTopicForm, UpdateTopicForm, ExamForm, ExamQuestionForm, ExamQuestionUpdateForm
from student.forms import PhotoUploadForm
from student.models import Student, Tma, Exam, TmaQuestion, TmaAnswer, ExamQuestion, ExamAnswer

api_url = "http://127.0.0.1:7000/api/states"

class PassRequestToFormMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


@method_decorator([anonymous_required], name='dispatch')
class LecturerSignUpView(CreateView):
    model = User
    form_class = LecturerSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'lecturer'

        try:
            response = requests.request("GET", url = api_url, headers={}, data={})
            data = response.json()
        except:
            with open('lecturer\states.json', 'r') as read_file:
                data = json.load(read_file)

        extra_context = { "states": data }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Lecturer Account Created!')
        return redirect('lecturer:dashboard')


@login_required
@lecturer_required
def dashboard(request):
    return render(request, 'lecturer/dashboard.html')


@method_decorator([login_required, lecturer_required], name='dispatch')
class PhotoUpdateView(UpdateView):
    model = User
    form_class = PhotoUploadForm
    template_name = 'lecturer/upload_photo.html'
    success_url = reverse_lazy('lecturer:dashboard')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        self.request.user.passport_uploaded = True
        messages.success(self.request, 'Photo uploaded Successfully!')
        return super().form_valid(form)


@method_decorator([login_required, lecturer_required], name='dispatch')
class StudentListView(ListView):
    model = Student
    template_name = "lecturer/student.html"
    context_object_name = "students"
    paginate_by = 12

    def get_queryset(self):
        courses = Course.objects.filter(lecturer=self.request.user.lecturer)
        students = Student.objects.filter(courses__in=courses).order_by('user')
        queryset = []
        for student in students:
            if student not in queryset:
                queryset.append(student)

        return queryset


def save_tma_form(request, form, template_name):
    active_session = Session.objects.get(active=True)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            tma_title = form.cleaned_data['title']
            tma_course = form.cleaned_data['course']
            check_tma = Tma.objects.filter(title=tma_title, course=tma_course).exists()

            if check_tma:
                data['form_is_valid'] = False
            else:
                tma = form.save(commit=False)
                tma.is_open = True
                tma.admin = request.user.lecturer
                tma.session = active_session
                tma.save()
                data['form_is_valid'] = True
                data['html_tma_list'] = render_to_string('lecturer/includes/partial_tma_list.html', {
                    'tmas': Tma.objects.filter(admin=request.user.lecturer)
                })

        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name, {'form': form}, request=request)
    return JsonResponse(data)


@login_required
@lecturer_required
def tma_create(request):
    if request.method == 'POST':
        form = TmaForm(request.POST, request=request)
    else:
        form = TmaForm(request=request)
    return save_tma_form(request, form, 'lecturer/includes/partial_tma_create.html')


@login_required
@lecturer_required
def tma_update(request, pk):
    tma = get_object_or_404(Tma, pk=pk)
    if request.method == 'POST':
        form = TmaForm(request.POST, instance=tma)
    else:
        form = TmaForm(instance=tma)
    return save_tma_form(request, form, 'lecturer/includes/partial_tma_update.html')


def tma_delete(request, pk):
    tma = get_object_or_404(Tma, pk=pk)
    data = dict()
    tmas = request.user.lecturer.tmas.select_related('course') \
        .annotate(tma_questions_count=Count('tma_questions', distinct=True)) \
        .annotate(taken_count=Count('taken_tmas', distinct=True))

    if request.method == 'POST':
        tma.delete()
        data['form_is_valid'] = True
        data['html_tma_list'] = render_to_string('lecturer/includes/partial_tma_list.html', {
            'tmas': tmas
        })
    else:
        data['html_form'] = render_to_string('lecturer/includes/partial_tma_delete.html', {'tma': tma}, request=request)
    return JsonResponse(data)


@method_decorator([login_required, lecturer_required], name='dispatch')
class TmaListView(ListView):
    model = Tma
    ordering = ('title',)
    context_object_name = 'tmas'
    template_name = 'lecturer/tma_index.html'

    def get_context_data(self, **kwargs):
        lecturer_courses = Course.objects.filter(lecturer=self.request.user.lecturer)
        extra_context = {
            'lecturer_courses': lecturer_courses.count()
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = self.request.user.lecturer.tmas \
            .select_related('course') \
            .annotate(tma_questions_count=Count('tma_questions', distinct=True)) \
            .annotate(taken_count=Count('taken_tmas', distinct=True))
        return queryset


@method_decorator([login_required, lecturer_required], name='dispatch')
class TmaQuestionView(PassRequestToFormMixin, UpdateView):
    model = Tma
    form_class = TmaForm
    context_object_name = 'tma'
    template_name = 'lecturer/tma_question.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().tma_questions.annotate(tma_answers_count=Count('tma_answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.lecturer.tmas.all()


@method_decorator([login_required, lecturer_required], name='dispatch')
class TmaResultsView(DetailView):
    model = Tma
    context_object_name = 'tma'
    template_name = 'lecturer/tma_results.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        tma = self.get_object()
        taken_tmas = tma.taken_tmas.select_related('student__user').order_by('-date')
        total_taken_tmas = taken_tmas.count()
        tma_score = tma.taken_tmas.aggregate(average_score=Avg('score'))
        extra_context = {
            'taken_tmas': taken_tmas,
            'total_taken_tmas': total_taken_tmas,
            'tma_score': tma_score
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)


@login_required
@lecturer_required
def question_add(request, pk):
    tma = get_object_or_404(Tma, pk=pk, admin=request.user.lecturer)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.tma = tma
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('lecturer:question_change', tma.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'lecturer/question_add_form.html', {'tma': tma, 'form': form})


@login_required
@lecturer_required
def question_change(request, tma_pk, question_pk):
    tma = get_object_or_404(Tma, pk=tma_pk, admin=request.user.lecturer)
    question = get_object_or_404(TmaQuestion, pk=question_pk, tma=tma)

    AnswerFormSet = inlineformset_factory(
        TmaQuestion,  # parent model
        TmaAnswer,  # base model
        formset=BaseAnswerInlineFormSet,
        fields=('text', 'is_correct'),
        min_num=4,
        validate_min=True,
        max_num=4,
        validate_max=True,
    )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, 'Question and answers saved with success!')
            return redirect('lecturer:tma_question', tma.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'lecturer/question_change_form.html', {
        'tma': tma,
        'question': question,
        'form': form,
        'formset': formset
    })


def question_delete(request, pk, question_pk):
    question = get_object_or_404(TmaQuestion, pk=question_pk, tma__pk=pk)

    data = dict()
    if request.method == 'POST':
        question.delete()
        data['form_is_valid'] = True
        data['html_tma_list'] = render_to_string('lecturer/includes/partial_tma_list.html', {
            'tmas': Tma.objects.all()
        })
    else:
        data['html_form'] = render_to_string('lecturer/includes/partial_tma_delete.html', {'question': question},
                                             request=request)
    return JsonResponse(data)


@method_decorator([login_required, lecturer_required], name='dispatch')
class ExamAddView(PassRequestToFormMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'lecturer/exam/index.html'

    def get_context_data(self, **kwargs):
        lecturer_courses = Course.objects.filter(lecturer=self.request.user.lecturer).count()
        exams_count = self.request.user.lecturer.exams.count()
        exams = Exam.objects.filter(admin=self.request.user.lecturer)
        student_count = Student.objects.filter(exams__in=exams).count()

        check = False
        if lecturer_courses == exams_count:
            check = True

        extra_context = {
            'courses': Course.objects.filter(lecturer=self.request.user.lecturer).count(),
            'exams': self.request.user.lecturer.exams \
                .select_related('course') \
                .annotate(questions_count=Count('exam_questions', distinct=True)) \
                .annotate(taken_count=Count('taken_exams', distinct=True)),
            'check': check,
            'student_count': student_count
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        exam = form.save(commit=False)
        exam.admin = self.request.user.lecturer
        exam.session = Session.objects.get(active=True)
        exam.save()
        messages.success(self.request, 'Exam added successfully.')
        return redirect('lecturer:exam_index')

    def form_invalid(self, form):
        messages.error(self.request, 'Check your Input And Try Again.')
        return super().form_invalid(form)


@method_decorator([login_required, lecturer_required], name='dispatch')
class ExamQuestionView(PassRequestToFormMixin, UpdateView):
    model = Exam
    form_class = TmaForm
    context_object_name = 'exam'
    template_name = 'lecturer/exam/question.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().exam_questions.annotate(exam_answers_count=Count('exam_answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.lecturer.exams.all()


@login_required
@lecturer_required
def exam_question_add(request, pk):
    exam = get_object_or_404(Exam, pk=pk, admin=request.user.lecturer)

    if request.method == 'POST':
        form = ExamQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('lecturer:exam_question_change', exam.pk, question.pk)
    else:
        form = ExamQuestionForm()

    return render(request, 'lecturer/exam/question_add_form.html', {'exam': exam, 'form': form})


@login_required
@lecturer_required
def exam_question_change(request, exam_pk, question_pk):
    exam = get_object_or_404(Exam, pk=exam_pk, admin=request.user.lecturer)
    question = get_object_or_404(ExamQuestion, pk=question_pk, exam=exam)

    SubjectiveAnswerFormSet = inlineformset_factory(
        ExamQuestion,  # parent model
        ExamAnswer,  # base model
        formset=BaseAnswerInlineFormSet,
        fields=('text', 'is_correct'),
        min_num=1,
        validate_min=True,
        max_num=1,
        validate_max=True,
    )

    ObjectiveAnswerFormSet = inlineformset_factory(
        ExamQuestion,  # parent model
        ExamAnswer,  # base model
        formset=BaseAnswerInlineFormSet,
        fields=('text', 'is_correct'),
        min_num=3,
        validate_min=True,
        max_num=4,
        validate_max=True,
    )

    if request.method == 'POST':
        if question.type == "MCQ":
            formset = ObjectiveAnswerFormSet(request.POST, instance=question)
        else:
            formset = SubjectiveAnswerFormSet(request.POST, instance=question)

        form = QuestionForm(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, 'Question and answers saved with success!')
            return redirect('lecturer:exam_questions', exam.pk)
    else:
        form = QuestionForm(instance=question)
        if question.type == "MCQ":
            formset = ObjectiveAnswerFormSet(instance=question)
        else:
            formset = SubjectiveAnswerFormSet(instance=question)

    return render(request, 'lecturer/exam/question_change_form.html', {
        'exam': exam,
        'question': question,
        'form': form,
        'formset': formset
    })


@method_decorator([login_required, lecturer_required], name='dispatch')
class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'lecturer/board/topics.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        lecturer_courses = Course.objects.filter(lecturer=self.request.user.lecturer)
        extra_context = {
            'lecturer_courses': lecturer_courses.count()
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = Topic.objects.filter(lecturer=self.request.user.lecturer).order_by('-last_updated').annotate(
            replies=Count('posts'))
        return queryset


@method_decorator([login_required, lecturer_required], name='dispatch')
class TopicCreateView(PassRequestToFormMixin, CreateView):
    model = Topic
    form_class = NewTopicForm
    template_name = 'lecturer/board/edit_topic.html'

    def form_valid(self, form):
        topic = form.save(commit=False)
        topic.lecturer = self.request.user.lecturer
        topic.save()
        messages.success(self.request, 'New Topic Created!')
        return redirect('lecturer:topic_list')


@method_decorator([login_required, lecturer_required], name='dispatch')
class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'lecturer/board/topic_posts.html'
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


@method_decorator([login_required, lecturer_required], name='dispatch')
class TopicUpdateView(UpdateView):
    model = Topic
    form_class = UpdateTopicForm
    template_name = 'lecturer/board/edit_topic.html'
    success_url = reverse_lazy('lecturer:topic_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(lecturer=self.request.user.lecturer)

    def form_valid(self, form):
        topic = form.save(commit=False)
        topic.updated_at = timezone.now()
        topic.save()
        messages.success(self.request, 'Topic Updated Successfully!')
        return redirect('lecturer:topic_list')
