from django.db import models
from django.contrib.auth.models import AbstractUser
import os
import fitz  # PyMuPDF для работы с PDF
from ebooklib import epub  # Для EPUB
from PIL import Image
from pdf2image import convert_from_path
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import User

# Модель пользователя
class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'  # Логин по email
    REQUIRED_FIELDS = ['username']  # Для создания суперпользователя

# Модель книги
class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    start_reading = models.DateField(null=True,  blank=True)
    end_reading = models.DateField(null=True,  blank=True)
    GENRE_CHOICES = [
        ('FANTASY', 'Фэнтези'),
        ('SCIFI', 'Научная фантастика'),
        ('DETECTIVE', 'Детектив'),
        ('ROMANCE', 'Романтика'),
        ('HORROR', 'Ужасы'),
        ('THRILLER', 'Триллер'),
        ('HISTORICAL', 'Исторический роман'),
        ('BIOGRAPHY', 'Биография'),
        ('ADVENTURE', 'Приключения'),
        ('MYSTERY', 'Мистика'),
        ('DRAMA', 'Драма'),
        ('POETRY', 'Поэзия'),
        ('PHILOSOPHY', 'Философия'),
        ('SCIENCE', 'Наука'),
        ('SELFHELP', 'Саморазвитие'),
        ('BUSINESS', 'Бизнес-литература'),
        ('COMICS', 'Комиксы и графические романы'),
        ('CHILDREN', 'Детская литература'),
        ('YOUNGADULT', 'Подростковая литература'),
        ('CLASSIC', 'Классика'),
        ('RELIGION', 'Религиозная литература'),
        ('PSYCHOLOGY', 'Психология'),
        ('COOKING', 'Кулинария'),
        ('TRAVEL', 'Путешествия'),
        ('FANTASTICREALISM', 'Фантастический реализм'),
        ('CYBERPUNK', 'Киберпанк'),
        ('DYSTOPIA', 'Антиутопия'),
        ('MAGICREALISM', 'Магический реализм'),
]
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    year = models.IntegerField(null=True, blank=True)
    impression = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    isbn = models.CharField(max_length=13, unique=True, null=True, blank=True)
    file = models.FileField(upload_to='book_files/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} by {self.author}"

    def extract_cover(self):
        """Извлекает обложку из загруженной книги"""
        if self.file:
            file_path = self.file.path
            ext = os.path.splitext(file_path)[1].lower()

            if ext == '.pdf':
                self._extract_pdf_cover(file_path)
            elif ext == '.epub':
                self._extract_epub_cover(file_path)


    def save(self, *args, **kwargs):
        if not self.pk and self.cover_image:
            super().save(*args, **kwargs)
            
            img = Image.open(self.cover_image.path)
            
            max_size = (800, 1200)
            img.thumbnail(max_size, Image.LANCZOS)
            img.save(self.cover_image.path)
        else:
            super().save(*args, **kwargs)