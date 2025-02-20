from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import RegistrationForm, CustomLoginForm,BookForm
from django.contrib.auth.decorators import login_required
from .models import Book
from django.shortcuts import redirect  # Добавьте этот импорт
from random import choice
import requests
from django.db.models import Q
from django.shortcuts import get_object_or_404
from datetime import datetime 

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
    
def search_books(query):
    url = f"https://openlibrary.org/search.json?q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        books = data.get("docs", [])
        return books
    return []


@login_required
def book_list(request):
    query = request.GET.get('q', '')  # Получаем поисковый запрос
    books = Book.objects.filter(user=request.user)  # Книги пользователя
    api_books = []  # Книги из Open Library API

    if query:
        # Фильтр по базе данных
        books = books.filter(Q(name__icontains=query) | Q(author__icontains=query))

        # Запрос в Open Library API
        api_url = f"https://openlibrary.org/search.json?q={query}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            for doc in data.get('docs', [])[:20]:  # Берем первые 5 книг из результата
                api_books.append({
                    'title': doc.get('title', 'Без названия'),
                    'author': ', '.join(doc.get('author_name', ['Неизвестный автор'])),
                    'cover': f"https://covers.openlibrary.org/b/olid/{doc.get('cover_edition_key', '')}-M.jpg" if doc.get('cover_edition_key') else "https://via.placeholder.com/150"
                })

    colors = ['#3E2723', '#5A7D5A', '#797444', '#643811', '#a46572']
    
    return render(request, 'diary/book_list.html', {
        'books': books,
        'api_books': api_books,
        'query': query,
        'colors': colors
    })

@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        print('before validation')
        for field in form:
            print(f"Field {field.name}  Error: {field.errors}")
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user  # Привязываем книгу к пользователю
            book.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'diary/book_form.html', {'form': form})

@login_required
def book_delete_confirm(request, pk):
    book = Book.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        # Удаляем книгу
        book.delete()
        return redirect('book_list')  # После удаления редиректим на список книг
    return render(request, 'diary/book_confirm_delete.html', {'book': book})



@login_required
def book_detail(request, book_id):
    """Отображает страницу книги с кнопкой редактирования."""
    book = get_object_or_404(Book, id=book_id, user=request.user)
    return render(request, "diary/book_detail.html", {"book": book})

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


@login_required
def add_book_from_api(request):
    if request.method == "POST":
        title = request.POST.get("title")
        author = request.POST.get("author")
        cover_url = request.POST.get("cover")
        year = request.POST.get("year")  # Добавляем получение года

        # Если год не передан, задаем значение по умолчанию (например, 0 или None)
        year = int(year) if year else None  


        # Создаем объект книги
        book = Book.objects.create(name=title, author=author, cover_url=cover_url, year=year, user=request.user)

        return redirect("book_list")
        

    return redirect("book_list")

@login_required
def edit_book(request, book_id):
    """Редактирование уже добавленной книги."""
    book = get_object_or_404(Book, id=book_id, user=request.user)

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save(commit=False)

            # Обрабатываем даты, если они пустые
            start_reading = request.POST.get("start_reading")
            end_reading = request.POST.get("end_reading")

            try:
                book.start_reading = datetime.strptime(start_reading, "%Y-%m-%d") if start_reading else None
                book.end_reading = datetime.strptime(end_reading, "%Y-%m-%d") if end_reading else None
            except ValueError:
                book.start_reading = None
                book.end_reading = None

            book.save()
            return redirect("book_list")
    else:
        form = BookForm(instance=book)

    return render(request, "diary/edit_book.html", {"form": form, "cover": book.cover_url, "book": book})


@login_required
def edit_book_from_api(request):
    """Позволяет редактировать книгу перед добавлением из Open Library API."""
    title = request.GET.get("title", "")
    author = request.GET.get("author", "")
    year = request.GET.get("year", "")
    cover = request.GET.get("cover", "")  # Обложка передаётся, но не запрашивается у пользователя

    # Проверка на существование книги с таким названием и автором
    existing_book = Book.objects.filter(name=title, author=author).first()
    if existing_book:
        # Если книга уже существует в базе данных
        return redirect('book_list')

    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            book.cover_url = cover  # Автоматически сохраняем обложку

            # Обрабатываем даты, если они пустые
            start_reading = request.POST.get("start_reading")
            end_reading = request.POST.get("end_reading")

            try:
                book.start_reading = datetime.strptime(start_reading, "%Y-%m-%d") if start_reading else None
                book.end_reading = datetime.strptime(end_reading, "%Y-%m-%d") if end_reading else None
            except ValueError:
                book.start_reading = None
                book.end_reading = None

            # Сохраняем книгу
            book.save()
            return redirect("book_list")
        else:
            print("Ошибки в форме:", form.errors)  # Выводим ошибки

    else:
        form = BookForm(initial={
            "name": title,
            "author": author,
            "year": year if year else None,  # Если year пустой, ставим None
        })

    return render(request, "diary/edit_book.html", {"form": form, "cover": cover})