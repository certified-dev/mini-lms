from django.urls import path

from student import views

app_name = 'student'

urlpatterns = [
    # path('slip/id_card', views.identity_card, name='id_card'),
    # path('slip/semester', views.semester_slip, name='semester_slip'),
    # path('slip/courses', views.courses_slip, name='courses_slip'),
    # path('slip/examination', views.exams_slip, name='exams_slip'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('wallet', views.wallet, name='wallet'),
    path('semester/registration', views.SemesterRegisterView.as_view(), name='sem_reg'),
    path('semester/payment', views.semester_payment, name='sem_pay'),
    path('courses/registration', views.CourseRegistrationView.as_view(), name='reg_course'),
    path('courses/payment', views.course_payment, name='course_pay'),
    path('courses', views.StudentCoursesView.as_view(), name='student_courses'),
    path('project', views.StudentProjectsView.as_view(), name='project'),

    path('tma/all', views.TmaListView.as_view(), name='tma_list'),
    path('tma/<int:pk>/attempt', views.take_tma, name='take_tma'),
    path('tma/taken/<int:pk>/result', views.TmaResultsView.as_view(), name='tma_result'),
    path('taken_tma/<int:pk>', views.ajax_taken_tma, name='ajax_tma_result'),

    path('exam/registration', views.ExamRegistrationView.as_view(), name='exam_reg'),
    path('exam/payment', views.exam_payment, name='exam_pay'),
    path('exam/all', views.ExamListView.as_view(), name='exam_list'),
    path('exam/<int:pk>/attempt', views.take_exam, name='take_exam'),
    path('exam/taken/<int:pk>/result', views.ExamResultView.as_view(), name='exam_result'),

    path('boards/topics', views.TopicListView.as_view(), name='board'),
    path('boards/topic/<int:pk>/posts', views.PostListView.as_view(), name='topic_posts'),
    path('boards/topic/<int:pk>/reply', views.reply_topic, name='reply_topic'),
    path('boards/topic/<int:pk>/post/<int:post_pk>/edit', views.PostUpdateView.as_view(), name='edit_post'),

]
