from django.urls import path

from . import views

app_name = "blogs"

urlpatterns = [
    path("", views.BlogListView.as_view(), name="blog_list"),
    path("my/create/", views.UserBlogCreateView.as_view(), name="blog_create"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("my/blogs/", views.MyBlogsView.as_view(), name="my_blogs"),
    path("posts/new/", views.PostCreateView.as_view(), name="post_create"),
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("posts/<int:pk>/edit/", views.PostUpdateView.as_view(), name="post_update"),
    path("posts/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("posts/<int:pk>/comment/", views.CommentCreateView.as_view(), name="post_comment"),
    path("posts/<int:pk>/like/", views.LikeToggleView.as_view(), name="post_like"),
    path("comments/<int:pk>/edit/", views.CommentUpdateView.as_view(), name="comment_update"),
    path("comments/<int:pk>/delete/", views.CommentDeleteView.as_view(), name="comment_delete"),
    path("<slug:slug>/edit/", views.BlogUpdateView.as_view(), name="blog_edit"),
    path("<slug:slug>/delete/", views.BlogDeleteView.as_view(), name="blog_delete"),
    path("<slug:slug>/", views.BlogDetailView.as_view(), name="blog_detail"),
]