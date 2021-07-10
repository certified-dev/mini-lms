from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from mini_lms.views import home, SignUpView, load_departments, load_programmes, upload_photo
from lecturer.views import LecturerSignUpView
from student.views import StudentSignUpView

urlpatterns = [
    path('', home, name='home'),
    path('ajax/load-departments/', load_departments, name='ajax_load_departments'),
    path('ajax/load-programmes/', load_programmes, name='ajax_load_programmes'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path('accounts/signup/student/', StudentSignUpView.as_view(), name='student_signup'),
    path('accounts/signup/lecturer/', LecturerSignUpView.as_view(), name='lecturer_signup'),
    path('student/', include('student.urls')),
    path('lecturer/', include('lecturer.urls')),
    path('accounts/upload/photo/', upload_photo, name="upload_photo"),
    path('admin_tools/', include('admin_tools.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
