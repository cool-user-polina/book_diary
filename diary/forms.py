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
        fields = ['author', 'name', 'genre', 'year', 'impression','cover_url', 'file']
        widgets = {
            'year': forms.NumberInput(attrs={'min': 0, 'max': 2100}),
            'start_reading': forms.DateInput(attrs={'type': 'date'}),
            'end_reading': forms.DateInput(attrs={'type': 'date'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control-file'})
        }