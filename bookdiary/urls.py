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
from diary.views import add_book_from_api
from diary.views import edit_book_from_api, edit_book, book_list, book_detail
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', diary_views.register, name='register'),  # Регистрация
    path('login/', diary_views.custom_login, name='login'),    # Вход
    path('logout/', diary_views.custom_logout, name='logout'), # Выход
    path('', diary_views.home, name='home'),    
    path('books/', diary_views.book_list, name='book_list'),
    path('books/create/', diary_views.book_create, name='book_create'),
    path('books/<int:pk>/edit/', diary_views.book_edit, name='book_edit'),
    path('books/<int:pk>/delete/', diary_views.book_delete, name='book_delete'),
    path('books/<int:pk>/delete/confirm/', diary_views.book_delete_confirm, name='book_delete_confirm'),
    path('add_book_from_api/', add_book_from_api, name='add_book_from_api'),
    path('edit-book/', edit_book_from_api, name='edit_book_from_api'),
    path('books/', book_list, name='book_list'),
    path('books/<int:book_id>/', book_detail, name='book_detail'),  # Страница просмотра книги
    path('books/edit/<int:book_id>/', edit_book, name='edit_book'),
    path('search/', diary_views.search_openlibrary, name='search_openlibrary'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)   
