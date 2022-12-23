from posts.models import User
from django.test import Client, TestCase
from django.urls import reverse


class SignUpFormTests(TestCase):

    def test_create_user(self):
        """Валидная форма создает нового пользвателя в User."""
        self.guest_client = Client()
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Vasya',
            'last_name': 'Pupkin',
            'username': 'auth',
            'email': 'test@test.ru',
            'password1': 'qqpp12345',
            'password2': 'qqpp12345'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data, follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1,
                         'Количество зарегистрированных пользователей в БД '
                         'не соответствует ожидаемому')
        self.assertTrue(User.objects.filter(
            username='auth').exists()
        )
