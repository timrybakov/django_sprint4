from django.http import Http404
from django.urls import reverse_lazy
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
    model = Post
    form_class = PostForm


class CommentMixin:
    model = Comment
    form_class = CommentForm


class PostListView(ListView):
    model = Post
    queryset = Post.new_objects.new_select_related().annotate(
        comment_count=Count('comments')
        ).order_by('-pub_date')
    template_name = 'blog/index.html'
    paginate_by = DEFAULT_VALUE


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.instance.pub_date > timezone.now():
            form.instance.is_published = False
        else:
            form.instance.is_published = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Post, pk=self.kwargs['pk'])
        if self.instance.author != self.request.user:
            return redirect('blog:post_detail', self.instance.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['pk']}
        )


class PostDetailView(FormMixin, DetailView):
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
    instance = get_object_or_404(Post, pk=pk)
    form = PostForm(instance=instance)
    context = {'form': form}
    if request.user != instance.author:
        raise Http404
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(request, 'blog/create.html', context)


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = DEFAULT_VALUE

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.username == self.kwargs['username']:
            return Post.objects.select_related('author').filter(
                author__username=self.kwargs['username']
            ).order_by('-pub_date')
        else:
            return Post.objects.select_related('author').filter(
                author__username=self.kwargs['username'],
                pub_date__lte=timezone.now()
            ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = 'blog/user.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    posts = None
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.posts = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.posts
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.posts.pk}
        )


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):

        if not self.request.user.is_authenticated:
            raise Http404

        get_object_or_404(
            Comment,
            pk=self.kwargs['pk'],
            author=self.request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment.objects
            .select_related('post')
            .filter(post__id=self.kwargs['post_id']),
            pk=self.kwargs['pk']
        )

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):

        if not self.request.user.is_authenticated:
            raise Http404

        get_object_or_404(
            Comment,
            pk=self.kwargs['pk'],
            author=self.request.user
        )

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = DEFAULT_VALUE

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug']
        )
        return Post.objects.select_related('category').filter(
            category__slug=self.category.slug,
            is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
