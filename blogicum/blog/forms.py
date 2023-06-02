from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        ),
        initial=timezone.now,
        label='Дата публикации',
        help_text=('Если установить дату и время в будущем - '
                   'можно делать отложенные публикации')
    )

    class Meta:
        model = Post
        fields = (
            'pub_date',
            'title',
            'text',
            'category',
            'location',
            'image'
        )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = (
            'text',
        )


class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )
