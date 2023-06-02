from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    CreateView, DetailView, ListView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin
from django.db.models import Count
from django.contrib.auth.decorators import login_required

from .models import Post, Category, User, Comment
from .forms import PostForm, CommentForm, ProfileEditForm

DEFAULT_VALUE = 10


class PostMixin:
    """Мискин для публикации."""
    model = Post
    form_class = PostForm


class CommentMixin:
    """Миксин для комментариев."""
    model = Comment
    form_class = CommentForm


class PostListView(ListView):
    """Главная страница."""
    model = Post
    template_name = 'blog/index.html'
    paginate_by = DEFAULT_VALUE

    def get_queryset(self):
        return Post.new_objects.new_select_related().annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    """Создание публикации."""
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    """Редактирование публикации."""
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if post.author != self.request.user:
            return redirect('blog:post_detail', post.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['pk']}
        )


class PostDetailView(FormMixin, DetailView):
    """Страница публикации."""
    model = Post
    template_name = 'blog/detail.html'
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.select_related('author')
        return context


@login_required
def delete_post(request, pk):
    """Удаление публикации."""
    instance = get_object_or_404(
        Post,
        pk=pk,
        author=request.user
    )
    form = PostForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(request, 'blog/create.html', context)


class ProfileListView(ListView):
    """Страница профиля пользователя."""
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = DEFAULT_VALUE

    def get_context_data(self, **kwargs):
        user = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        if user == self.request.user:
            user_posts = user.posts.select_related(
                'location', 'category', 'author'
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
        else:
            user_posts = Post.new_objects.filter(author=user.id).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
        return super().get_context_data(
            object_list=user_posts,
            profile=user,
            **kwargs
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""
    model = User
    form_class = ProfileEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    """Добавление комментария."""
    one_post = None
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        self.one_post = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.author = self.request.user
        form.instance.post = self.one_post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.one_post.pk}
        )


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    """Редактирование комментария."""
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comment,
            pk=self.kwargs['post_id']
        )
        if comment.author != self.request.user:
            return redirect('blog:post_detail', comment.post.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление комментария."""
    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comment,
            pk=self.kwargs['post_id']
        )
        if comment.author != self.request.user:
            return redirect('blog:post_detail', comment.post.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CategoryListView(ListView):
    """Страница публикации постов по категории."""
    model = Post
    template_name = 'blog/category.html'
    paginate_by = DEFAULT_VALUE

    def get_context_data(self, **kwargs):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        post_list = category.categories.filter(
            category__slug=category.slug,
            is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
        return super().get_context_data(
            category=category,
            object_list=post_list,
            **kwargs
        )
