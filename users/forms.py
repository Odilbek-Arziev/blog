from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'input', 'placeholder': 'Example123'
    }), label='Никнейм')
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'input'}), label='Пароль')
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'input'}), label='Пароль повторно')

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'input', 'placeholder': 'Example123'
    }), label='Введите никнейм')
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'input'}), label='Введите пароль')

    class Meta:
        model = User
        fields = ['username',  'password']
