from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

from app.models import Participant


def signin_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next", "/")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("room_list" if next_url == "" else next_url)
        else:
            messages.error(request, "Kullanıcı adı veya şifre hatalı.")

    return render(request, "account/signin.html")


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Şifreler eşleşmiyor.")
            return render(request, "account/signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu kullanıcı adı zaten kullanılıyor.")
            return render(request, "account/signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Bu e-posta adresi zaten kullanılıyor.")
            return render(request, "account/signup.html")

        try:
            user = User.objects.create_user(
                username=username, email=email, password=password1
            )
            login(request, user)
            messages.success(request, "Hesabınız başarıyla oluşturuldu!")
            return redirect("room_list")
        except Exception as e:
            messages.error(
                request, "Kayıt olurken bir hata oluştu. Lütfen tekrar deneyin."
            )

    return render(request, "account/signup.html")


# Alternatif olarak daha basit bir view kullanabilirsiniz:
@login_required
def logout_view(request):
    """Basit çıkış view'i"""
    # Aktif katılımcı ise, odadan çıkar
    try:
        participant = Participant.objects.get(user=request.user)
        participant.delete()
    except Participant.DoesNotExist:
        pass

    logout(request)
    return redirect("room_list")
