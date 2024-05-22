"""
URL configuration for fake_cassino project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.urls import path, include
from django.shortcuts import render

import re, traceback
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

def log_out(request):
    logout(request)
    return HttpResponse()

class SignInError:
    def __init__(self, mssg) -> None:
        self.mssg = mssg

def sign_in(request):
    error = None
    new_user = None
    has_error = False
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        has_error = re.match('^[a-zA-Z][a-zA-Z0-9_-]*$', username) is None
        if has_error:
            error = SignInError("Nome de usuário inválido: Deve começar com uma letra e apenas conter letras, números, underscores ou hifens")
        else:
            try:
                User.objects.create_user(username=username, password=password)
                new_user = {"username": username}
            except IntegrityError as e:
                traceback.print_exception(e)
                error = SignInError(f"O usuário '{username}' já existe.")
            except Exception as e:
                traceback.print_exception(e)
                error = SignInError(f"Não foi possível criar o usuário.")

    return render(request, "roulette/signin.html", {"error": error, "new_user": new_user})

def redirect_home(request):
    return HttpResponseRedirect("/home/")

def is_logged(request):
    return JsonResponse({"is_logged": request.user.is_authenticated})

urlpatterns = [
    path('', redirect_home, name="redirect_home"),
    path('home/', include("roulette.urls"), name="home"),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name="roulette/login.html", next_page="/home/"), name='login'),
    path('signin/', sign_in, name='signin'),
    path('logout/', log_out, name='logout'),
    path('is_logged/', is_logged, name='is_logged'),
]
