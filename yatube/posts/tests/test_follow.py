import tempfile
from django.conf import settings
from ..models import Post, User, Follow
from django.test import Client, TestCase, override_settings
from django.urls import reverse


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='NoName')
        cls.another_author = User.objects.create_user(username='Another')
        cls.post = Post.objects.create(author=cls.author, text='Тестовый пост')
        cls.authorized_client = Client()
        cls.authorized_author = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_author.force_login(cls.author)
        cls.reverse = reverse(
            'posts:profile_follow',
            kwargs={'username': CreateFormTests.author.username}
        )
        cls.reverse_unfollow = reverse(
            'posts:profile_unfollow',
            kwargs={'username': CreateFormTests.author.username}
        )

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_client.force_login(CreateFormTests.user)

    def test_following_user(self):
        """Авторизованный пользователь создает запись в Follow."""
        follow_count = Follow.objects.count()
        response = self.authorized_client.get(CreateFormTests.reverse)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={
                'username': CreateFormTests.author.username}))
        self.assertEqual(Follow.objects.count(), follow_count + 1,
                         "Количество подписок не совпадает с ожидаемым")
        self.assertTrue(Follow.objects.filter(
            user=CreateFormTests.user,
            author=CreateFormTests.author
        ).exists()
        )

    def test_unfollowing_user(self):
        """Авторизованный пользователь удаляет запись в Follow."""
        self.authorized_client.get(CreateFormTests.reverse)
        follow_count = Follow.objects.count()
        response = self.authorized_client.get(CreateFormTests.reverse_unfollow)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={
                'username': CreateFormTests.author.username}))
        self.assertEqual(Follow.objects.count(), follow_count - 1,
                         "Количество подписок не совпадает с ожидаемым")

    def test_following_not_authorized_client(self):
        """Не авторизованный пользователь не может создать запись в Follow."""
        self.authorized_client.logout()
        follow_count = Follow.objects.count()
        self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={
                'username': CreateFormTests.author.username}))
        self.assertEqual(
            Follow.objects.count(), follow_count,
            "Количество подписок не совпадает с ожидаемым"
        )

    def test_follow_user(self):
        """Правильное отобраение ленты в 'follow_index'."""
        self.authorized_client.get(CreateFormTests.reverse)
        Post.objects.create(
            author=CreateFormTests.another_author,
            text='Тестовый текст 2',
        )
        response = self.authorized_client.get(reverse(
            'posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 1,
                         'Количество подписок не соответствует ожиданиям')
        first_object = response.context.get('page_obj')[0]
        dict = {
            first_object.pk: CreateFormTests.post.pk,
            first_object.text: CreateFormTests.post.text,
            first_object.author: CreateFormTests.post.author
        }
        for key, expected in dict.items():
            with self.subTest(key=key):
                self.assertEqual(key, expected)
