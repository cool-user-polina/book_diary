from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User

# Форма регистрации
class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']  # Поля для регистрации

# Форма входа (переопределяем стандартную)
class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')  # Меняем label на "Email"