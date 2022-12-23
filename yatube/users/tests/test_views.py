from http import HTTPStatus
from posts.models import User
from django import forms
from django.test import TestCase, Client
from ..forms import CreationForm
from django.urls import reverse


class UserPagesTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user(
            username='auth',
            first_name='Vasya',
            last_name='Pupkin'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.guest_client = Client()
        self.pages_templates_names = {
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:pass_change_done'):
                'users/password_change_done.html',
            reverse('users:logout'):
                'users/logged_out.html',
            reverse('users:login'):
                'users/login.html',
            reverse('users:password_reset'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('password_reset_complete'):
                'users/password_reset_complete.html'
        }

    def test_posts_page_accessible_by_name(self):
        """URL, генерируемые при помощи имени namespace:name, доступны."""
        for rev in self.pages_templates_names.keys():
            response = self.authorized_client.get(rev)
            with self.subTest(response=response):
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 'URL не доступен')

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        response = self.guest_client.get(reverse('users:signup'))
        self.assertTemplateUsed(response, 'users/signup.html')
        for reverse_name, template in self.pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_signup_correct_context(self):
        """Шаблон 'signup' сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('users:signup'))
        context_dict = {'form': CreationForm}
        for expected_key, expected_value in context_dict.items():
            with self.subTest(expected_key=expected_key):
                self.assertIn(expected_key, response.context.keys(),
                              f'Элемент контекста "{expected_key}" '
                              'отсутствует в результирующем контексте')
                self.assertIsInstance(
                    response.context.get(expected_key), expected_value,
                    f'Тип элемента контекста "{expected_key}" '
                    'не соответвтвует ожидаемому'
                )

    def test_page_signup_show_form_correct_in_context(self):
        """Шаблон формы 'signup' сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected,
                                      f'Тип поля "{value}" не соответствует'
                                      'ожиданиям')
