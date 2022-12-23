from http import HTTPStatus
from posts.models import User
from django.test import TestCase, Client


class URLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client.force_login(self.user)
        self.urls_list = [
            '/auth/logout/',
            '/auth/login/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/done/',
            '/auth/signup/',
            '/auth/password_change/done/',
            '/auth/password_change/',
        ]

    def test_unexisting_page_all_users(self):
        """Несуществующая страница не доступна пользователям."""
        response = self.guest_client.get('/auth/unexisting_page/')
        self.assertEqual(response.status_code,
                         HTTPStatus.NOT_FOUND,
                         'Несуществующая страница доступна'
                         'пользователям')

    def test_list_url_exists_at_desired_location(self):
        """Страницы доступны не авторизованному пользователю."""
        urls_list = self.urls_list[:5]
        for url in urls_list:
            response = self.guest_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code,
                                 HTTPStatus.OK,
                                 'Страница не доступна не авторизованному '
                                 'пользователю')

    def test_list_url_exists_not_authorized_user(self):
        """Страница 'signup' доступна не авторизованному пользователю."""
        response = self.guest_client.get(self.urls_list[5])
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Страница не доступна не авторизованному '
                         'пользователю')

    def test_list_url_redirect_anonymous_user(self):
        """Страницы перенаправляют анонимного пользователя."""
        urls_list = self.urls_list[6:]
        for url in urls_list:
            with self.subTest(url=url):
                self.assertRedirects(self.guest_client.get(url, follow=True),
                                     (f'/auth/login/?next={url}'))

    def test_list_urls_exists_authorized_user(self):
        """Страницы доступны авторизованному пользователю."""
        urls_list = self.urls_list[6:]
        for url in urls_list:
            response = self.authorized_client.get(url, follow=True)
            with self.subTest(url=url):
                self.assertEqual(response.status_code,
                                 HTTPStatus.OK,
                                 'Страница не доступна авторизованному '
                                 'пользователю')

    def test_list_urls_redirect_authorized_user(self):
        """Страницы перенаправляет авторизованного пользователя."""
        response = self.authorized_client.get(self.urls_list[5])
        self.assertRedirects(response, ('/'))

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон
        (анонимный пользователь)."""

        url_templates_names = {
            '/auth/logout/': 'users/logged_out.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for url, template in url_templates_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_autorized_client(self):
        """URL-адрес использует соответствующий шаблон
        (авторизованный пользователь)."""
        url_templates_names = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html'
        }
        for url, template in url_templates_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
