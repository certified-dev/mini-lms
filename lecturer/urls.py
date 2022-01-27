from django.urls import path

from lecturer import views
from lecturer.views import (TmaListView, TmaResultsView, TmaQuestionView, ExamAddView)

app_name = 'lecturer'

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('photo/upload', views.PhotoUpdateView.as_view(), name='photo_upload'),
    path('course/students', views.StudentListView.as_view(), name='students'),

    path('tmas', TmaListView.as_view(), name='tma_index'),
    path('tma/create', views.tma_create, name='tma_create'),
    path('tma/<int:pk>/update', views.tma_update, name='tma_update'),
    path('tma/<int:pk>/delete', views.tma_delete, name='tma_delete'),
    path('tma/<int:pk>/results', TmaResultsView.as_view(), name='tma_results'),
    path('tma/<int:pk>/questions', TmaQuestionView.as_view(), name='tma_question'),
    path('tma/<int:pk>/question/add', views.question_add, name='question_add'),
    path('tma/<int:tma_pk>/question/<int:question_pk>', views.question_change, name='question_change'),
    path('tma/<int:tma_pk>/question/<int:question_pk>/delete', views.question_delete, name='question_delete'),

    path('exam/create', ExamAddView.as_view(), name='exam_index'),
    path('exam/<int:pk>/questions', views.ExamQuestionView.as_view(), name='exam_questions'),
    path('exam/<int:pk>/question/add', views.exam_question_add, name='exam_question_add'),
    path('exam/<int:exam_pk>/question/<int:question_pk>', views.exam_question_change, name='exam_question_change'),

    path('board/topics', views.TopicListView.as_view(), name='topic_list'),
    path('board/topic/new', views.TopicCreateView.as_view(), name='new_topic'),
    path('board/topic/<int:pk>', views.PostListView.as_view(), name='topic_posts'),
    path('board/topic/<int:pk>/update', views.TopicUpdateView.as_view(), name='edit_topic'),

]
