from django import forms
from .models import *


class PostForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'input'}
    ), label='Название поста')
    text = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'textarea', 'size': '20'}
    ), label='Текст поста')

    image = forms.ImageField(label='Картинка для поста', required=False)
    comments_allowed = forms.CharField(
        widget=forms.CheckboxInput(),
        label='Комментирование разрешено',
        initial=True,
        required=False
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'image', 'comments_allowed']


class CommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'textarea',
        'size': '40',
        'placeholder': 'Оставьте свой комментарий...'
    }))

    class Meta:
        model = Comment
        fields = ['body', ]
