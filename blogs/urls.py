from django.urls import path
from . import views

app_name = "blogs"

urlpatterns = [
    path("", views.BlogListView.as_view(), name="blog_list"),
    path("my/create/", views.UserBlogCreateView.as_view(), name="blog_create"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("my/blogs/", views.MyBlogsView.as_view(), name="my_blogs"),
    path("comments/<int:pk>/edit/", views.CommentUpdateView.as_view(), name="comment_update"),
    path("comments/<int:pk>/delete/", views.CommentDeleteView.as_view(), name="comment_delete"),
    path("<slug:slug>/edit/", views.BlogUpdateView.as_view(), name="blog_edit"),
    path("<slug:slug>/delete/", views.BlogDeleteView.as_view(), name="blog_delete"),
    path("<slug:slug>/comment/", views.CommentCreateView.as_view(), name="blog_comment"),
    path("<slug:slug>/like/", views.LikeToggleView.as_view(), name="blog_like"),
    path("<slug:slug>/", views.BlogDetailView.as_view(), name="blog_detail"),
]