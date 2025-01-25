from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Book

admin.site.site_header = "Book Diary Admin"  # Заголовок админки
admin.site.index_title = "Управление данными"  # Заголовок на главной странице админки

# Регистрируем кастомную модель пользователя

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )

admin.site.register(User, CustomUserAdmin)

# Регистрируем модель Book
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'user', 'genre', 'year', 'created_at')  # Что отображать в списке
    list_filter = ('genre', 'year', 'created_at')  # Фильтры справа
    search_fields = ('name', 'author')  # Поиск по полям
    date_hierarchy = 'created_at' 

admin.site.register(Book, BookAdmin)
