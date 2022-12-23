from django.test import TestCase
from http import HTTPStatus


class ViewTestClass(TestCase):
    def test_error_page(self):
        """Статус ответа сервера - 404.
        URL-адрес использует соответствующий шаблон."""
        response = self.client.get('/nonexist-page/')
        template = 'core/404.html'
        self.assertEqual(
            response.status_code, HTTPStatus.NOT_FOUND,
            'Статус ответа сервера при обращении к несуществующей странице'
            'не соответствует ожиданиям'
        )
        self.assertTemplateUsed(response, template)
