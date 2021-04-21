from django import forms
from django.contrib.auth import get_user_model
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from core.models import Department
from mini_lms.decorators import anonymous_required

User = get_user_model()


class UploadPhotoForm(forms.Form):
    class Meta:
        fields = ('photo',)


@method_decorator([anonymous_required], name='dispatch')
class SignUpView(TemplateView):
    template_name = 'signup.html'


def home(request):
    if request.user.is_authenticated:
        if request.user.is_student:
            return redirect('student:dashboard')
        else:
            return redirect('lecturer:dashboard')
    return render(request, 'home.html')


def load_departments(request):
    faculty_id = request.GET.get('faculty')
    departments = Department.objects.filter(faculty_id=faculty_id).order_by('name')
    return render(request, 'includes/department_dropdown_list_options.html', {'departments': departments})


def upload_photo(request):
    if request.method == 'POST':
        item = request.FILES.get('photo')
        if item:
            user = request.user
            user.photo = item
            user.passport_uploaded = True
            user.save()
            return JsonResponse({'message': 'Uploaded Success!!!'})

        return JsonResponse({'message': 'Upload Failed!!!'})
