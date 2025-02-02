from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import RegistrationForm, CustomLoginForm,BookForm
from django.contrib.auth.decorators import login_required
from .models import Book
from django.shortcuts import redirect  # Добавьте этот импорт

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
        return redirect('login') 
    else: 
        return redirect('book_list')


@login_required
def book_list(request):
    books = Book.objects.filter(user=request.user)
    return render(request, 'diary/book_list.html', {'books': books})

@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user  # Привязываем книгу к пользователю
            book.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'diary/book_form.html', {'form': form})

from django.shortcuts import get_object_or_404

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk, user=request.user)  # Только свои книги
    return render(request, 'diary/book_detail.html', {'book': book})

@login_required
def book_edit(request, pk):
    book = Book.objects.get(pk=pk, user=request.user)  # Только свои книги
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'diary/book_form.html', {'form': form})

@login_required
def book_delete(request, pk):
    book = Book.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'diary/book_confirm_delete.html', {'book': book})