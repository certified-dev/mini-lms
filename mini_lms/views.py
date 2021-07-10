import sys
from PIL import Image
from io import BytesIO

from django import forms
from django.contrib.auth import get_user_model
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.core.files.uploadedfile import InMemoryUploadedFile

from core.models import Department, Programme
from mini_lms.decorators import anonymous_required


User = get_user_model()


def compress(file):
    temp_image = Image.open(file)
    outputIoStream = BytesIO()
    resized_temp_image = temp_image.resize((1100, 1000))
    resized_temp_image.save(outputIoStream, format='JPEG', quality=60)
    outputIoStream.seek(0)
    final_image = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % file.name.split('.')[0],
                                       'image/jpeg', sys.getsizeof(outputIoStream), None)
    return final_image


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
    return render(request, 'includes/dropdown_list_options.html', {'departments': departments})


def load_programmes(request):
    department_id = request.GET.get('department')
    programmes = Programme.objects.filter(department_id=department_id).order_by('name')
    return render(request, 'includes/dropdown_list_options.html', {'programmes': programmes})


def upload_photo(request):
    if request.method == 'POST':
        item = request.FILES.get('photo')
        if item:
            user = request.user
            user.photo = compress(item)
            user.passport_uploaded = True
            user.save()
            return JsonResponse({'message': 'Uploaded Success!!!'})

        return JsonResponse({'message': 'Upload Failed!!!'})
