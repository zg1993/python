from django.shortcuts import render
from django.contrib.auth.models import User
# Create your views here.

def home(request):
    print(request.get_full_path())
    users = User.objects.all()
    return render(request, 'test.html')


def found404(request):
    return render(request, '404.html')