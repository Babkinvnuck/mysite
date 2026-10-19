from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView, View,
)

from .models import Blog, Post, Comment, Like
from .forms import BlogForm, PostForm, CommentForm
from accounts.forms import ProfileForm
from accounts.models import Profile


class BlogListView(ListView):
    model = Blog
    template_name = "blogs/blog_list.html"
    context_object_name = "blogs"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        region = self.request.GET.get("region")
        if region:
            queryset = queryset.filter(region=region)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_region"] = self.request.GET.get("region", "")
        return context

class PostListView(ListView):
    model = Post
    template_name = "blogs/blog_list.html"
    context_object_name = "posts"
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


class BlogDetailView(DetailView):
    """Страница одного блога со списком записей."""
    model = Blog
    template_name = "blogs/blog_detail.html"
    context_object_name = "blog"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = self.object.posts.all()[:20]
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blogs/post_detail.html"
    context_object_name = "post"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views += 1
        obj.save(update_fields=["views"])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["liked"] = user.is_authenticated and self.object.likes.filter(user=user).exists()
        return context


class UserBlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    form_class = BlogForm
    template_name = "blogs/blog_form.html"
    success_url = reverse_lazy("blogs:blog_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blogs/post_form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["blog"].queryset = Blog.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blogs/post_form.html"

    def test_func(self):
        post = self.get_object()
        return post.blog.owner == self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["blog"].queryset = Blog.objects.filter(owner=self.request.user)
        return form

    def get_success_url(self):
        return reverse_lazy("blogs:post_detail", kwargs={"pk": self.object.pk})
        
from .models import Blog, Post, Comment

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blogs/post_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = get_object_or_404(Post, pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs["pk"])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("blogs:post_detail", kwargs={"pk": self.kwargs["pk"]})
        

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blogs/post_confirm_delete.html"
    success_url = reverse_lazy("blogs:blog_list")

    def test_func(self):
        post = self.get_object()
        return post.blog.owner == self.request.user
        

class BlogUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Blog
    form_class = BlogForm
    template_name = "blogs/blog_form.html"

    def test_func(self):
        blog = self.get_object()
        return blog.owner == self.request.user

    def get_success_url(self):
        return reverse_lazy("blogs:blog_detail", kwargs={"slug": self.object.slug})
        
        
class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blogs/comment_form.html"

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_success_url(self):
        return reverse_lazy("blogs:post_detail", kwargs={"pk": self.object.post.pk})
        
        
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "blogs/comment_confirm_delete.html"

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_success_url(self):
        return reverse_lazy("blogs:post_detail", kwargs={"pk": self.object.post.pk})
        
        
class LikeToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
        return redirect("blogs:post_detail", pk=pk)
        
        
class BlogDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Blog
    template_name = "blogs/blog_confirm_delete.html"
    success_url = reverse_lazy("blogs:blog_list")

    def test_func(self):
        blog = self.get_object()
        return blog.owner == self.request.user
        
        
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "blogs/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        context["my_blogs"] = Blog.objects.filter(owner=self.request.user)
        context["profile_form"] = ProfileForm(instance=profile)
        context["profile"] = profile
        return context

    def post(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
        return redirect("blogs:profile")
        
        
class MyBlogsView(LoginRequiredMixin, ListView):
    model = Blog
    template_name = "blogs/my_blogs.html"
    context_object_name = "my_blogs"

    def get_queryset(self):
        return Blog.objects.filter(owner=self.request.user)