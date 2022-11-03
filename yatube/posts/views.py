from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from .models import Post, Group


def index(request):
    posts = Post.objects.order_by('-pub_date')[:10]
    template = 'posts/index.html'
    text = 'Это главная страница проекта Yatube'
    context = {'text': text, 'posts': posts,}
    return HttpResponse(render(request, template, context))


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context = {'group': group, 'posts': posts}
    return HttpResponse(render(request, template, context))
