"""
URL configuration for bookdiary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from diary import views as diary_views  # Импортируем наши view-функции
# from diary.views import add_book_from_api
from diary.views import (
    register, custom_login, custom_logout, home,
    book_list, book_create, book_delete, book_detail,
    book_edit, search_books, edit_book_from_api
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', register, name='register'),  # Регистрация
    path('login/', custom_login, name='login'),    # Вход
    path('logout/', custom_logout, name='logout'), # Выход
    path('', home, name='home'),    
    path('books/', book_list, name='book_list'),
    path('books/create/', book_create, name='book_create'),
    path('books/<int:pk>/delete/', book_delete, name='book_delete'),
    path('books/<int:book_id>/', book_detail, name='book_detail'),  # Страница просмотра книги
    path('books/<int:pk>/edit/', book_edit, name='book_edit'),
    path('search/', search_books, name='search_books'),
    path('edit-from-api/', edit_book_from_api, name='edit_book_from_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)   
