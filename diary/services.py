import requests
from fuzzywuzzy import fuzz  # Добавьте: pip install fuzzywuzzy python-Levenshtein

def search_books_google_api(query, page, api_books):
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
            print(data)
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

    return {'pagination' :pagination, 'api_books':api_books}

