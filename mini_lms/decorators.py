import functools

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.conf import settings

def student_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    """
    Decorator for views that checks that the logged in user is a student,
    redirects to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_student,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def lecturer_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    """
    Decorator for views that checks that the logged in user is a lecturer,
    redirects to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_lecturer,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def anonymous_required(function=None, redirect_url=None):
    """
    """
    if not redirect_url:
        redirect_url = settings.LOGIN_REDIRECT_URL

    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

