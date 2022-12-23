from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    path('', views.index, name="index"),
    path('group/<slug:slug>/', views.group_posts, name="group_list"),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/del/', views.post_delete, name='post_delete'),
    path('search/', views.search, name='search'),
    path('posts/<int:post_id>/add_like/', views.add_like, name='like'),
    path('posts/<int:post_id>/add_dislike/', views.add_dislike, name='dislike'),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/<int:comment_id>/add/',
        views.add_comment_with_quote,
        name='add_comment_with_quote'
    ),
    path(
        'posts/<int:post_id>/<int:comment_id>/add_comment/',
        views.add_comment_to_comment,
        name='add_comment_to_comment'
    ),
    path(
        'posts/<int:post_id>/<int:comment_id>/del/',
        views.comment_delete,
        name='comment_del'
    ),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]
