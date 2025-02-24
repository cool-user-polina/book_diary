import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from .forms import RegistrationForm, CustomLoginForm, BookForm
from django.contrib.auth.decorators import login_required
from .models import Book
from datetime import datetime 
from fuzzywuzzy import fuzz  # Добавьте: pip install fuzzywuzzy python-Levenshtein
from urllib.parse import urlparse
from django.urls import reverse
from django.core.files.base import ContentFile

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
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
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
    query = request.GET.get('q', '').strip().lower()
    books = Book.objects.filter(user=request.user)

    if query:
        # Получаем все книги пользователя
        all_books = list(books)
        
        # Функция для подсчета схожести строк
        def calculate_similarity(book):
            # Считаем максимальную схожесть для названия и автора
            title_ratio = fuzz.partial_ratio(query, book.name.lower())
            author_ratio = fuzz.partial_ratio(query, book.author.lower())
            return max(title_ratio, author_ratio)

        # Фильтруем и сортируем книги
        filtered_books = []
        for book in all_books:
            similarity = calculate_similarity(book)
            if similarity > 60:  # Порог схожести
                filtered_books.append((book, similarity))
        
        # Сортируем по схожести
        filtered_books.sort(key=lambda x: x[1], reverse=True)
        
        # Извлекаем только книги, без значений схожести
        books = [book for book, _ in filtered_books]

    return render(request, 'diary/book_list.html', {
        'books': books,
        'query': query,
        'colors': ['#3E2723', '#5A7D5A', '#797444', '#643811', '#a46572']
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
    return redirect('book_list')

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
    query = request.GET.get('q', '').strip().lower()
    page = int(request.GET.get('page', 1))
    api_books = []

    if query:
        # Формируем запрос для Google Books API
        api_query = f'intitle:"{query}"+OR+inauthor:"{query}"'

        api_url = (
            f"https://www.googleapis.com/books/v1/volumes"
            f"?q={api_query}"
            f"&langRestrict=ru"
            f"&maxResults=40"
            f"&startIndex={(page-1)*20}"
            f"&orderBy=relevance"
        )

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                total_items = data.get('totalItems', 0)
                
                filtered_items = []
                for item in data.get('items', []):
                    volume_info = item.get('volumeInfo', {})
                    
                    # Базовые проверки
                    title = volume_info.get('title')
                    authors = volume_info.get('authors', [])
                    if not title or not authors:
                        continue

                    # Проверяем схожесть с помощью fuzz
                    title_ratio = fuzz.partial_ratio(query, title.lower())
                    author_ratio = max(
                        fuzz.partial_ratio(query, author.lower())
                        for author in authors
                    ) if authors else 0

                    # Если схожесть меньше 60%, пропускаем
                    if max(title_ratio, author_ratio) < 60:
                        continue

                    # Проверяем наличие обложки
                    image_links = volume_info.get('imageLinks', {})
                    cover_url = image_links.get('thumbnail')
                    if not cover_url:
                        continue
                    
                    # Заменяем http на https
                    if cover_url.startswith('http:'):
                        cover_url = 'https:' + cover_url[5:]

                    filtered_items.append({
                        'title': title,
                        'author': ', '.join(authors),
                        'cover': cover_url,
                        'year': volume_info.get('publishedDate', '')[:4],
                        'similarity': max(title_ratio, author_ratio)  # Сохраняем схожесть для сортировки
                    })

                # Сортируем по схожести
                filtered_items.sort(key=lambda x: x['similarity'], reverse=True)
                
                # Берем только 20 результатов
                api_books = filtered_items[:20]
                
                # Обновляем пагинацию
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
    else:
        pagination = None

    return render(request, 'diary/search_books.html', {
        'api_books': api_books,
        'query': query,
        'pagination': pagination
    })

@login_required
def edit_book_from_api(request):
    title = request.GET.get("title", "")
    author = request.GET.get("author", "")
    year = request.GET.get("year", "")
    cover_url = request.GET.get("cover", "")
    preview_link = request.GET.get("preview", "")
    search_query = request.GET.get("search_query", "")
    
    existing_book = Book.objects.filter(name=title, author=author).first()
    if existing_book:
        return redirect(f"{reverse('search_books')}?q={search_query}")

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            
            if not request.FILES.get('cover_image') and cover_url:
                try:
                    response = requests.get(cover_url)
                    if response.status_code == 200:
                        file_name = urlparse(cover_url).path.split('/')[-1]
                        extension = file_name.split('.')[-1] if '.' in file_name else 'jpg'
                        image_name = f"{title[:30]}_{author[:30]}.{extension}"
                        book.cover_image.save(
                            image_name,
                            ContentFile(response.content),
                            save=False
                        )
                except Exception as e:
                    print(f"Ошибка при загрузке обложки: {e}")
            elif 'cover_image' in request.FILES:
                book.cover_image = request.FILES['cover_image']

            book.save()
            return redirect(f"{reverse('search_books')}?q={search_query}")
    else:
        form = BookForm(initial={
            "name": title,
            "author": author,
            "year": year if year else None,
        })

    return render(request, "diary/edit_book.html", {
        "form": form, 
        "cover": cover_url,
        "preview_link": preview_link,
        "search_query": search_query
    })