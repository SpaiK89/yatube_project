from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import SET_NULL

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название группы")
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    description = models.TextField(verbose_name="Описание группы")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
        ordering = ['pk', ]


class Post(models.Model):
    text = models.TextField(verbose_name="Текст",
                            help_text='Введите текст поста'
                            )
    pub_date = models.DateTimeField(default=datetime.now,
                                    verbose_name="Дата публикации"
                                    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор публикации"
    )
    group = models.ForeignKey(
        Group,
        on_delete=SET_NULL,
        related_name="posts",
        blank=True,
        null=True,
        verbose_name="Группа",
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )


    def __str__(self):
        return self.text[:15]

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['-pub_date', 'pk']


class Comment(models.Model):
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        default=datetime.now,
        verbose_name="Дата комментария"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост",
        help_text='Пост, к которому будет относиться комментарий'
    )
    comment_p = models.ForeignKey(
        'self',
        on_delete=SET_NULL,
        default=None,
        blank=True,
        null=True,
        related_name="comments",
        verbose_name="Комментарий",
        help_text='Комментарий, к которому будет относиться комментарий'
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created', 'pk']


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Автор"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name="Подписчик",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ['pk']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow')
        ]


class Like(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="like"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="author_like"
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('post', 'user',),
                name='unique_like'
            ),
        )


class Dislike(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="dislike"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="author_dislike"
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('post', 'user',),
                name='unique_dislike'
            ),
        )
