import os

from django.conf import settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.contrib.messages import constants as messages

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'isxfc9$^alplud*ktp)x#dek0msfp8h5w^d#ny$bip3trd!cl@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'core.User'

PROG_MODEL = 'core.Programme'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# Application definition


INSTALLED_APPS = [
    'fluent_dashboard',

    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',

    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'core',
    'student',
    'lecturer',

    'crispy_forms',
    'widget_tweaks',
    'floppyforms'

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'mini_lms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'admin_tools.template_loaders.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

]

WSGI_APPLICATION = 'mini_lms.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Lagos'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (Images, Videos)
MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SITE_ID = 1

# Django Auth Settings
LOGIN_URL = 'login'

LOGOUT_URL = 'logout'

LOGIN_REDIRECT_URL = 'home'

LOGOUT_REDIRECT_URL = 'login'


# Messages built-in framework
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Crispy Forms Settings

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Test Email Service
DEFAULT_FROM_EMAIL = 'info@studyware.edu'

EMAIL_USE_TLS = False

EMAIL_HOST = 'localhost'

EMAIL_PORT = 1025

# Celery
CELERY_BROKER_URL = 'redis://localhost:6379'

CELERY_RESULT_BACKEND = 'redis://localhost:6379'

CELERY_ACCEPT_CONTENT = ['application/json']

CELERY_TASK_SERIALIZER = 'json'

CELERY_RESULT_SERIALIZER = 'json'

CELERY_TIMEZONE = 'Africa/Lagos'

# Dashboard
ADMIN_TOOLS_INDEX_DASHBOARD = 'fluent_dashboard.dashboard.FluentIndexDashboard'

ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'fluent_dashboard.dashboard.FluentAppIndexDashboard'

ADMIN_TOOLS_MENU = 'fluent_dashboard.menu.FluentMenu'

FLUENT_DASHBOARD_ICON_THEME = 'oxygen'

FLUENT_DASHBOARD_DEFAULT_MODULE = 'admin_tools.dashboard.modules.AppList'

FLUENT_DASHBOARD_APP_ICONS = {
    'core/user': 'meeting-participant.png',
    'core/topic': 'newspaper1.png',
    'core/post': 'chat-1.png',
    'lecturer/lecturer': 'users7.png',
    'student/student': 'network60.png',
    'core/study_centre': 'main-page.png',
}

FLUENT_DASHBOARD_APP_GROUPS = (

    ('Administration', {
        'models': (
            'django.contrib.sites.*',
            'core.models.User'
        ),
    }),
    ('School', {
        'models': (
            'core.models.Session',
            'core.models.Faculty',
            'core.models.Department',
            'core.models.Level',
            'core.models.Programme',
            'core.models.Course',
            'core.models.Semester'
        ),
    }),
    ('T.M.A', {
        'models': (
            'student.models.Tma',
            'student.models.TmaQuestion',
            'student.models.TmaAnswer',
            'student.models.TakenTma'
        ),

    }),
    ('Examination', {
        'models': (
            'student.models.Exam',
            'student.models.ExamQuestion',
            'student.models.ExamAnswer',
            'student.models.TakenExam'
        ),

    }),
    ('Users', {
        'models': (
            'lecturer.models.Lecturer',
            'student.models.Student',

        ),
    }),
    ('Boards', {
        'models': (
            'core.models.Topic',
            'core.models.Post',
        ),
    }),
    ('Others', {
        'models': (
            'core.models.Expense',
            'student.models.DebitTransaction',
            'student.models.CreditTransaction',
            'core.models.Studycentre',
        ),
    }),
)
