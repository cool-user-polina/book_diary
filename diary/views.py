from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import RegistrationForm, CustomLoginForm

# Регистрация
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            return redirect('home')  # Перенаправляем на главную
    else:
        form = RegistrationForm()
    return render(request, 'diary/register.html', {'form': form})

# Вход
def custom_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = CustomLoginForm()
    return render(request, 'diary/login.html', {'form': form})

# Выход
def custom_logout(request):
    logout(request)
    return redirect('home')

# Главная страница (только для авторизованных)
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Перенаправляем неавторизованных
    return render(request, 'diary/home.html')