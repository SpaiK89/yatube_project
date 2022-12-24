from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment, Follow, Dislike, Like
from .decorators import post_author_only
from django.db.models import Q


POSTS_PER_PAGE = 10


def paginator_func(*args):
    paginator = Paginator(args[1], POSTS_PER_PAGE)
    page_number = args[0].GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.select_related('group', 'author').all()
    template = "posts/index.html"
    text = "Последние обновления на сайте:"
    page_obj = paginator_func(request, post_list)
    context = {'text': text, 'page_obj': page_obj, }
    return render(request, template, context)


def group_posts(request, slug):
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author').all()
    page_obj = paginator_func(request, post_list)
    context = {'group': group, 'page_obj': page_obj}
    return HttpResponse(render(request, template, context))


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = paginator_func(request, post_list)
    following = Follow.objects.filter(
        user__username=request.user, author=author
    )
    likes = 0
    dislikes = 0
    for post in post_list:
        likes += post.like.count()
        dislikes += post.dislike.count()
    context = {'author': author,
               'page_obj': page_obj,
               'following': following,
               'likes': likes,
               'dislikes': dislikes
    }
    return render(request, template, context, )


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), pk=post_id
    )
    comments = post.comments.select_related('author', 'comment_p').all()

    form = CommentForm(request.POST or None)
    template = 'posts/post_detail.html'
    context = {'post': post, 'comments': comments, 'form': form }
    return render(request, template, context)


@login_required
@post_author_only
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return redirect('posts:profile', post.author)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    context = {'form': form}
    return render(request, template, context)


@login_required
@post_author_only
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post
                    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {'form': form, 'is_edit': True}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment_to_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment_p = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.comment_p = comment_p
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def add_comment_with_quote(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, post=post_id, pk=comment_id)
    comments = post.comments.select_related('author').all()
    comment.text = f'<blockquote class="blockquote-2">' \
                   f'<p> {comment.text} </p> ' \
                   f'<cite> {comment.author}</cite></blockquote>'
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    template = 'posts/post_detail.html'
    context = {'form': form, 'post': post, 'comments': comments}
    return render(request, template, context)


@login_required
def comment_delete(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.delete()
    return redirect(request.META.get('HTTP_REFERER',
                                     'redirect_if_referer_not_found'))


@login_required
def follow_index(request):
    template = "posts/follow.html"
    post_list = Post.objects.select_related('group', 'author').filter(
        author__following__user=request.user
    )
    page_obj = paginator_func(request, post_list)
    context = {"page_obj": page_obj}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:profile", username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(Follow, user=request.user,
                      author__username=username).delete()
    return redirect("posts:profile", username)


def search(request):
    template = 'posts/search.html'
    if request.method == 'GET' and request.GET['q']:
        context = {}
        query = request.GET.get('q')
        post_list_text = Post.objects.select_related('group', 'author').filter(
            text__iregex=query
        )
        context['post_list_text'] = post_list_text
        group_list = Group.objects.select_related().filter(
            title__iregex=query
        )
        context['group_list'] = group_list
        author_list = User.objects.select_related().filter(
            Q(first_name__iregex=query) | Q(last_name__iregex=query)
            | Q(username__iregex=query)
        )
        context['author_list'] = author_list
        return render(request, template, context)
    return render(request, template)


@login_required
@login_required
def add_like(request, post_id):
    try:
        dislike = Dislike.objects.get(post_id=post_id, user=request.user)
        dislike.delete()
        Like.objects.create(user=request.user, post_id=post_id)
    except Dislike.DoesNotExist:
        try:
            like = Like.objects.get(post_id=post_id, user=request.user)
            like.delete()
        except Like.DoesNotExist:
            Like.objects.create(user=request.user, post_id=post_id)
    return redirect(request.META.get('HTTP_REFERER',
                                     'redirect_if_referer_not_found'))


@login_required
def add_dislike(request, post_id):
    try:
        like = Like.objects.get(post_id=post_id, user=request.user)
        like.delete()
        Dislike.objects.create(user=request.user, post_id=post_id)
    except Like.DoesNotExist:
        try:
            dislike = Dislike.objects.get(
                post_id=post_id, user=request.user
            )
            dislike.delete()
        except Dislike.DoesNotExist:
            Dislike.objects.create(user=request.user, post_id=post_id)
    return redirect(request.META.get('HTTP_REFERER',
                                     'redirect_if_referer_not_found'))