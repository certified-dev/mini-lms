from django.urls import path

from student import views

app_name = 'student'

urlpatterns = [
    path('slip/id_card/', views.identity_card, name='id_card'),
    path('slip/semester_registration/', views.semester_slip, name='semester_slip'),
    path('slip/courses_registration/', views.courses_slip, name='courses_slip'),
    path('slip/exams_registration/', views.exams_slip, name='exams_slip'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('wallet/', views.wallet, name='wallet'),
    path('semester/register/', views.SemesterRegisterView.as_view(), name='sem_reg'),
    path('semester/pay/', views.semester_payment, name='sem_pay'),
    path('courses/register/', views.CourseRegistrationView.as_view(), name='reg_course'),
    path('courses/pay/', views.course_payment, name='course_pay'),
    path('courses/', views.StudentCoursesView.as_view(), name='student_courses'),
    path('project/', views.StudentProjectsView.as_view(), name='project'),
    path('tma/', views.TmaListView.as_view(), name='tma_list'),
    path('tma/<int:pk>/', views.take_tma, name='take_tma'),
    path('tma/taken/<int:pk>/result/', views.TmaResultsView.as_view(), name='tma_result'),
    path('taken_tma/<int:pk>/', views.ajax_taken_tma, name='ajax_tma_result'),
    path('exam/register/', views.ExamRegistrationView.as_view(), name='exam_reg'),
    path('exam/pay/', views.exam_payment, name='exam_pay'),
    path('board/topics/', views.TopicListView.as_view(), name='board'),
    path('board/topics/<int:pk>/', views.PostListView.as_view(), name='topic_posts'),
    path('board/topics/<int:pk>/reply/', views.reply_topic, name='reply_topic'),
    path('board/topics/<int:pk>/posts/<int:post_pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),

]
