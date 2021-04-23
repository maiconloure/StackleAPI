from django.urls import path
from .views import CategoryView, TagView, PostView, CommentView


urlpatterns = [
    path('categories/', CategoryView.as_view()),
    path('tags/', TagView.as_view()),
    path('posts/', PostView.as_view()),
    path('posts/<int:post_id>/', PostView.as_view()),
    path('posts/comments/', CommentView.as_view()),
    path('posts/comments/<int:id>/', CommentView.as_view()),
]