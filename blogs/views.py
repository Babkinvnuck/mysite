from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView, View,
)

from .models import Blog, Comment, Like
from .forms import BlogForm, CommentForm
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


class BlogDetailView(DetailView):
    model = Blog
    template_name = "blogs/blog_detail.html"
    context_object_name = "blog"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views += 1
        obj.save(update_fields=["views"])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["liked"] = user.is_authenticated and self.object.likes.filter(user=user).exists()
        context["form"] = CommentForm()
        return context


class UserBlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    form_class = BlogForm
    template_name = "blogs/blog_form.html"
    success_url = reverse_lazy("blogs:blog_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class BlogUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Blog
    form_class = BlogForm
    template_name = "blogs/blog_form.html"

    def test_func(self):
        blog = self.get_object()
        return blog.owner == self.request.user

    def get_success_url(self):
        return reverse_lazy("blogs:blog_detail", kwargs={"slug": self.object.slug})


class BlogDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Blog
    template_name = "blogs/blog_confirm_delete.html"
    success_url = reverse_lazy("blogs:blog_list")

    def test_func(self):
        blog = self.get_object()
        return blog.owner == self.request.user


class MyBlogsView(LoginRequiredMixin, ListView):
    model = Blog
    template_name = "blogs/my_blogs.html"
    context_object_name = "my_blogs"

    def get_queryset(self):
        return Blog.objects.filter(owner=self.request.user)


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


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blogs/blog_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["blog"] = get_object_or_404(Blog, slug=self.kwargs["slug"])
        return context

    def form_valid(self, form):
        blog = get_object_or_404(Blog, slug=self.kwargs["slug"])
        form.instance.blog = blog
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("blogs:blog_detail", kwargs={"slug": self.kwargs["slug"]})


class LikeToggleView(LoginRequiredMixin, View):
    def post(self, request, slug):
        blog = get_object_or_404(Blog, slug=slug)
        like, created = Like.objects.get_or_create(blog=blog, user=request.user)
        if not created:
            like.delete()
        return redirect("blogs:blog_detail", slug=slug)


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blogs/comment_form.html"

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_success_url(self):
        return reverse_lazy("blogs:blog_detail", kwargs={"slug": self.object.blog.slug})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "blogs/comment_confirm_delete.html"

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_success_url(self):
        return reverse_lazy("blogs:blog_detail", kwargs={"slug": self.object.blog.slug})