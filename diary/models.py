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
    GENRE_CHOICES = [
        ('FANTASY', 'Фэнтези'),
        ('SCIFI', 'Научная фантастика'),
        ('DETECTIVE', 'Детектив'),
    ]
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    year = models.IntegerField()
    impression = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} by {self.author}"