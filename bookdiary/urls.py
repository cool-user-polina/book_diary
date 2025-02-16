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
    path('books/<int:pk>/', diary_views.book_detail, name='book_detail'),
]              
