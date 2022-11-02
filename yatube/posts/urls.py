from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('posts/<slug:slug>/', views.group_posts),
    ]
