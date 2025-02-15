from django.db import models
from django.contrib.auth.models import AbstractUser

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
    cover_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} by {self.author}"