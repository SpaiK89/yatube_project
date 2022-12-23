from django.shortcuts import redirect
from .models import Post


def post_author_only(func):
    def check_user(request, post_id):
        post = Post.objects.select_related('group', 'author').get(pk=post_id)
        if post.author.username == request.user.username or \
                request.user.is_superuser:
            return func(request, post_id=post_id)
        return redirect('posts:profile', post.author)
    return check_user
