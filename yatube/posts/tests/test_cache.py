from ..models import Post, User
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

REVERSE_URL = reverse('posts:index')


class CacheTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.post = Post.objects.create(
            author=cls.author, text='Тестовый пост')

    def test_cache_for_index(self):
        """Тестирование праильной работы кеширования шаблона 'index'"""
        content = self.authorized_client.get(REVERSE_URL).content
        CacheTests.post.delete()
        new_content = self.authorized_client.get(REVERSE_URL).content
        self.assertEqual(content, new_content)
        cache.clear()
        newest_content = self.authorized_client.get(REVERSE_URL).content
        self.assertNotEqual(new_content, newest_content)
