from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse


class URLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_unexisting_page_all_users(self):
        """Несуществующая страница не доступна пользователям."""
        response = self.guest_client.get('/about/unexisting_page/')
        self.assertEqual(
            response.status_code, HTTPStatus.NOT_FOUND,
            'Несуществующая страница доступна'
            'пользователям'
        )

    def test_list_url_exists_at_desired_location(self):
        """Страницы доступны любому пользователю."""
        response_list = [
            self.guest_client.get('/about/author/'),
            self.guest_client.get('/about/tech/'),
        ]
        for response in response_list:
            with self.subTest(response=response):
                self.assertEqual(response.status_code,
                                 HTTPStatus.OK,
                                 'Страница не доступна любому пользователю')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        url_templates_names = {
            '/about/author/': 'about/about_author.html',
            '/about/tech/': 'about/about_tech.html',
        }
        for url, template in url_templates_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)


class StaticViewsTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемые при помощи имени namespace:name, доступны."""
        response_list = [self.guest_client.get(reverse('about:author')),
                         self.guest_client.get(reverse('about:tech'))]
        for response in response_list:
            with self.subTest(response=response):
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 'URL не доступен')

    def test_about_page_uses_correct_template(self):
        """При запросе к 'namespace:name' применяются шаблоны
        about/name.html."""
        pages_templates_names = {
            reverse('about:author'): 'about/about_author.html',
            reverse('about:tech'): 'about/about_tech.html',
        }
        for reverse_name, template in pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertTemplateUsed(
                    self.guest_client.get(reverse_name), template)
