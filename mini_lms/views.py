from django import forms
from django.contrib.auth import get_user_model
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from core.models import Department
from mini_lms.decorators import anonymous_required

User = get_user_model()


class UploadPhotoForm(forms.ModelForm):
    class Meta:
        model = User
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
        form = UploadPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # request.user.photo = request.FILES['photo']
            # request.user.save()
            return JsonResponse({'error': False, 'message': 'Uploaded Successfully!!!'})
        else:
            return JsonResponse({'error': True, 'message': 'Upload Failed!!!'})
