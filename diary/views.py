import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from .forms import RegistrationForm, CustomLoginForm, BookForm
from django.contrib.auth.decorators import login_required
from .models import Book
from django.shortcuts import redirect  # Добавьте этот импорт
from random import choice
import requests
from django.db.models import Q
from datetime import datetime 
from django.db.models.functions import Lower

# Регистрация
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
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

# Главная страница
def home(request):
    if not request.user.is_authenticated:
        return redirect('login') 
    else: 
        return redirect('book_list')

@login_required
def book_list(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(user=request.user)
    colors = ['#5A7D5A', '#797444', '#a46572']

    if query:
        books = books.filter(
            Q(name__icontains=query) |
            Q(author__icontains=query)
        ).distinct()

    return render(request, 'diary/book_list.html', {
        'books': books,
        'query': query,
        'colors': colors
    })

@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            
            if 'cover_image' in request.FILES:
                book.cover_image = request.FILES['cover_image']
            
            book.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'diary/book_form.html', {'form': form})

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk, user=request.user)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'diary/book_confirm_delete.html', {'book': book})

@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)
    return render(request, "diary/book_detail.html", {"book": book})

@login_required
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save(commit=False)
            
            if 'cover_image' in request.FILES:
                book.cover_image = request.FILES['cover_image']
            
            book.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'diary/book_form.html', {'form': form})

@login_required
def search_books(request):
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    api_books = []
    colors = ['#3E2723', '#5A7D5A', '#797444', '#643811', '#a46572']

    if query:
        # Проверяем, похож ли запрос на имя автора
        if ' ' in query and not any(char in query for char in [':', '"', "'", '+', '-']):
            # Поиск по автору
            api_query = f'inauthor:"{query}"'
        else:
            # Поиск по названию и автору
            api_query = f'intitle:"{query}"+OR+inauthor:"{query}"'

        api_url = (
            f"https://www.googleapis.com/books/v1/volumes"
            f"?q={api_query}"
            f"&langRestrict=ru"
            f"&maxResults=40"
            f"&startIndex={(page-1)*20}"
            f"&orderBy=relevance"
            f"&fields=items(volumeInfo(title,authors,publishedDate,imageLinks,categories,previewLink)),totalItems"  # Ограничиваем поля ответа
        )

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                total_items = data.get('totalItems', 0)
                
                filtered_items = []
                for item in data.get('items', []):
                    volume_info = item.get('volumeInfo', {})
                    
                    # Проверяем наличие автора
                    authors = volume_info.get('authors', [])
                    if not authors or authors == ['Неизвестный автор']:
                        continue
                        
                    # Если это поиск по автору, проверяем точное совпадение
                    if ' ' in query:
                        author_match = False
                        query_lower = query.lower()
                        for author in authors:
                            if query_lower in author.lower():
                                author_match = True
                                break
                        if not author_match:
                            continue
                    
                    # Проверяем наличие обложки
                    image_links = volume_info.get('imageLinks', {})
                    if not image_links:
                        continue
                        
                    cover_url = image_links.get('thumbnail')
                    if not cover_url:
                        continue

                    # Проверяем наличие названия
                    title = volume_info.get('title')
                    if not title:
                        continue
                    
                    # Заменяем http на https
                    if cover_url.startswith('http:'):
                        cover_url = 'https:' + cover_url[5:]

                    filtered_items.append({
                        'title': title,
                        'author': ', '.join(authors),
                        'cover': cover_url,
                        'year': volume_info.get('publishedDate', '')[:4],
                        'categories': volume_info.get('categories', []),
                        'preview_link': volume_info.get('previewLink', '')
                    })

                # Берем только 20 отфильтрованных результатов
                api_books = filtered_items[:20]
                
                # Обновляем общее количество страниц с учетом фильтрации
                total_pages = min((total_items + 19) // 20, 50)

                pagination = {
                    'current_page': page,
                    'total_pages': total_pages,
                    'has_previous': page > 1,
                    'has_next': page < total_pages and len(api_books) == 20,
                    'previous_page': page - 1,
                    'next_page': page + 1,
                    'page_range': range(max(1, page-2), min(total_pages+1, page+3))
                }
                
                if not api_books and page > 1:
                    return redirect(f"{request.path}?q={query}&page={page-1}")
                    
        except requests.RequestException:
            pagination = None
            pass
    else:
        pagination = None

    return render(request, 'diary/search_books.html', {
        'api_books': api_books,
        'query': query,
        'colors': colors,
        'pagination': pagination
    })

@login_required
def edit_book_from_api(request):
    title = request.GET.get("title", "")
    author = request.GET.get("author", "")
    year = request.GET.get("year", "")
    cover_url = request.GET.get("cover", "")

    existing_book = Book.objects.filter(name=title, author=author).first()
    if existing_book:
        return redirect('book_list')

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user

            if 'cover_image' in request.FILES:
                book.cover_image = request.FILES['cover_image']

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
        form = BookForm(initial={
            "name": title,
            "author": author,
            "year": year if year else None,
        })

    return render(request, "diary/edit_book.html", {
        "form": form, 
        "cover": cover_url
    })