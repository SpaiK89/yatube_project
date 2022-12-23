from django.test import TestCase
from ..models import Group, Post, User


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post_group_dict = {
            PostModelTest.post: PostModelTest.post.text[:15],
            PostModelTest.group: PostModelTest.group.title
        }
        for key, expected_value in post_group_dict.items():
            with self.subTest(key=key):
                self.assertEqual(str(key), expected_value,
                                 'Метод __str__ модели '
                                 'работает не корректно')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).verbose_name,
                                 expected_value,
                                 'verbose_name не соответствует ожидаемому')

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).help_text,
                                 expected_value,
                                 'help_text не соответствует ожидаемому')
