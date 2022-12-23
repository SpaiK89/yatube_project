from http import HTTPStatus
from django.test import TestCase, Client
from ..models import Post, Group, User


class URLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group
        )
        # список всех доступных url приложения
        cls.urls_list = [
            '/',
            '/group/test-slug/',
            '/profile/auth/',
            '/posts/1/',
            '/create/',
            '/posts/1/edit/',
            '/posts/1/del/',
            '/follow/',
            '/profile/auth/follow/',
            '/profile/auth/unfollow/',
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        URLTests.authorized_author = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client.force_login(self.user)
        URLTests.authorized_author.force_login(URLTests.author)

    def test_unexisting_page_all_users(self):
        """Несуществующая страница не доступна пользователям."""
        response_list = [
            self.guest_client.get('/unexisting_page/'),
            self.authorized_client.get('/unexisting_page/'),
            URLTests.authorized_author.get('/unexisting_page/'),
        ]
        for response in response_list:
            with self.subTest(response=response):
                self.assertEqual(response.status_code,
                                 HTTPStatus.NOT_FOUND,
                                 'Несуществующая страница доступна'
                                 'пользователям')

    def test_list_url_exists_at_desired_location(self):
        """Страницы доступны любому пользователю."""
        urls_list = URLTests.urls_list[:4]
        for url in urls_list:
            with self.subTest(url=url):
                self.assertEqual(self.guest_client.get(url).status_code,
                                 HTTPStatus.OK,
                                 'Страница не доступна любому пользователю')

    def test_list_url_exists_at_desired_location_authorized(self):
        """Страница 'create' доступна авторизованному пользователю."""
        response = self.authorized_client.get(URLTests.urls_list[4])
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Страница не доступна авторизованному пользователю')

    def test_list_url_redirect_anonymous(self):
        """Страницы перенаправляют анонимного пользователя."""
        urls_list = URLTests.urls_list[4:]
        for url in urls_list:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.guest_client.get(url, follow=True),
                    (f'/auth/login/?next={url}'))

    def test_list_url_exists_at_desired_location_author(self):
        """Страницы доступны автору поста."""
        url = URLTests.urls_list[5]
        self.assertEqual(
            URLTests.authorized_author.get(url).status_code,
            HTTPStatus.OK, 'Cтраницы не доступны автору поста.'
        )

    def test_list_url_redirect_at_desired_location_author(self):
        """Страницы перенаправляют автора поста."""
        url = URLTests.urls_list[6]
        self.assertRedirects(
            URLTests.authorized_author.get(url, follow=True),
            '/profile/auth/'
        )

    def test_list_url_redirect_not_author_post(self):
        """Страницы перенаправляют пользователя - не автора поста"""
        urls_list = URLTests.urls_list[5:7]
        for url in urls_list:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.authorized_client.get(url, follow=True),
                    ('/profile/auth/')
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        url_templates_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html'
        }
        for url, template in url_templates_names.items():
            with self.subTest(template=template):
                response = self.authorized_author.get(url)
                self.assertTemplateUsed(response, template)
