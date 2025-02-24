from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User
from .models import Book

# Форма регистрации
class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']  # Поля для регистрации

# Форма входа (переопределяем стандартную)
class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')  # Меняем label на "Email"



class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'author', 'genre', 'year', 'impression', 'cover_image', 'rating']
        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'genre': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'impression': forms.Textarea(attrs={'class': 'form-control'}),
            'start_reading': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_reading': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'rating': forms.HiddenInput()  # Оставляем скрытое поле для рейтинга
        }