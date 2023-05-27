from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post, Category, User, Comment
from .forms import PostForm, CommentForm, ProfileEditForm


class PostListView(ListView):
    model = Post
    queryset = Post.new_objects.new_select_related()
    template_name = 'blog/index.html'
    paginate_by = 10


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:profile')

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.instance.pub_date > timezone.now():
            form.instance.is_published = False
        else:
            form.instance.is_published = True
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        comments = Comment.objects.filter(post=self.object)
        context['comments'] = comments
        return context


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm


class ProfileDetailView(DetailView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = Post.objects.all()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = 'blog/user.html'
    paginate_by = 10

    def get_object(self, queryset=None):
        return self.request.user


class CommentCreateView(LoginRequiredMixin, CreateView):
    posts = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.posts = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.posts = self.posts
        return super().form_valid(form)


class CommentUpdateView(UpdateView):
    pass


class CommentDeleteView(DeleteView):
    pass


class CategoryListView(ListView):
    pass


def category_posts(request, category_slug):
    current_time = timezone.now()
    template = 'blog/category.html'

    post_list = Post.objects.select_related(
        'category',
        'location',
        'author'
    ).filter(
        Q(category__slug=category_slug)
        & Q(is_published=True)
        & Q(pub_date__lte=current_time)
    )

    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )

    context = {
        'category': category,
        'post_list': post_list
    }
    return render(request, template, context)
