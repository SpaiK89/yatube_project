from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm


class SignUp(AccessMixin, CreateView):
    form_class = CreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('posts:index')

    def form_valid(self, form):
        """функция автоматического залогинивания при регистрации
        нового юзера"""
        form.save()
        username = self.request.POST['username']
        password = self.request.POST['password1']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return redirect('posts:index')

    def dispatch(self, request, *args, **kwargs):
        """функция перенаправляет авторизованного пользователя при попытке
        регистрации"""
        if request.user.is_authenticated:
            return redirect('posts:index')
        return super().dispatch(request, *args, **kwargs)
