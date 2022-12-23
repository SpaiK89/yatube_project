import shutil
import tempfile
from http import HTTPStatus
from django.conf import settings
from django.core.paginator import Page
from django import forms
from django.db.models import QuerySet
from django.test import TestCase, Client, override_settings
from ..forms import PostForm, CommentForm
from ..models import Post, Group, User, Comment
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth',
                                              first_name='Vasya',
                                              last_name='Pupkin')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.image_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='image.gif',
            content=cls.image_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            author=cls.author,
            text='Комментарий',
            post=cls.post
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.response_list = (
            cls.authorized_client.get(reverse('posts:index')),
            cls.authorized_client.get(reverse('posts:group_list',
                                      kwargs={'slug': 'test-slug'})),
            cls.authorized_client.get(reverse('posts:profile',
                                      kwargs={'username': 'auth'})),
            cls.authorized_client.get(reverse('posts:post_detail',
                                      kwargs={'post_id': 1})),
            cls.authorized_client.get(reverse('posts:post_create')),
            cls.authorized_client.get(reverse('posts:post_edit',
                                      kwargs={'post_id': 1})),
            cls.authorized_client.get(reverse('posts:add_comment',
                                              kwargs={'post_id': 1})),
            cls.authorized_client.get(reverse('posts:follow_index')),
        )
        cls.reverse_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
            reverse('posts:post_detail', kwargs={'post_id': 1}),
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': 1})
        ]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_page_accessible_by_name(self):
        """URL, генерируемые при помощи имени namespace:name, доступны."""
        for response in PostPagesTests.response_list[:3]:
            with self.subTest(response=response):
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 'URL не доступен')

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'auth'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
            'posts/post_detail.html',
            reverse('posts:post_create'):
            'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
            'posts/create_post.html',
            reverse('posts:follow_index'):
                'posts/follow.html',
        }
        for reverse_name, template in pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        # Задаем список элементов контекста и их типы для всех views-функций
        context_dict_list = (
            {'text': str, 'page_obj': Page},
            {'group': Group, 'page_obj': Page},
            {'author': User, 'page_obj': Page, 'following': QuerySet},
            {'post': Post, 'comments': QuerySet, 'form': CommentForm},
            {'form': PostForm},
            {'form': PostForm, 'is_edit': bool},
            {},
            {'page_obj': Page},
        )
        for i, response in enumerate(PostPagesTests.response_list):
            for expected_key, expected_value in context_dict_list[i].items():
                with self.subTest(expected_key=expected_key):
                    self.assertIn(expected_key, response.context.keys(),
                                  f'Элемент контекста "{expected_key}" '
                                  'отсутствует в результирующем контексте')
                    self.assertIsInstance(
                        response.context.get(expected_key), expected_value,
                        f'Тип элемента контекста "{expected_key}" '
                        'не соответвтвует ожидаемому'
                    )

    def test_page_objects_show_values_correct(self):
        """Содержание элемента 'page_obj' в шаблонах
         совпадает с правильными значениями."""
        for rev in PostPagesTests.reverse_list[0:3]:
            response = self.authorized_client.get(rev)
            first_object = response.context['page_obj'][0]
            elements_dict = {'auth': first_object.author.username,
                             'Тестовый пост': first_object.text,
                             'Тестовая группа': first_object.group.title,
                             'posts/image.gif': first_object.image.name
                             }
            for expected, field in elements_dict.items():
                with self.subTest(field=field):
                    self.assertEqual(field, expected,
                                     'Содержание поля не соответствует'
                                     'ожиданиям')

    def test_page_profile_object_author_in_context_correct(self):
        """Содержание элемента 'author' в шаблоне 'profile' совпадает с
        правильными значениями."""
        response = self.authorized_client.get(
            PostPagesTests.reverse_list[2])
        author = response.context['author']
        author_dict = {
            'Vasya': author.first_name, 'Pupkin': author.last_name,
            'auth': author.username, 1: author.posts.count()
        }
        for expected, field in author_dict.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected,
                                 'Содержание поля не соответствует ожиданиям')

    def test_page_post_detail_object_post_in_context_correct(self):
        """Содержание элемента 'post' в шаблоне 'post_detail'
         совпадает с правильными значениями."""
        response = self.authorized_client.get(PostPagesTests.reverse_list[3])
        first_post = response.context['post']
        post_dict = {'Тестовый пост': first_post.text,
                     'Vasya Pupkin': first_post.author.get_full_name(),
                     'Тестовая группа': first_post.group.title,
                     'posts/image.gif': first_post.image.name,
                     1: first_post.author.posts.count()}
        for expected, field in post_dict.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected,
                                 'Содержание поля не соответствует ожиданиям'
                                 )

    def test_page_post_detail_object_comment_in_context_correct(self):
        """Содержание элемента 'post' в шаблоне 'post_detail'
         совпадает с правильными значениями."""
        response = self.authorized_client.get(PostPagesTests.reverse_list[3])
        first_comment = response.context['comments'][0]
        comment_dict = {'Комментарий': first_comment.text,
                        'Vasya Pupkin': first_comment.author.get_full_name(),
                        }
        for expected, field in comment_dict.items():
            with self.subTest(field=field):
                self.assertEqual(
                    field, expected,
                    'Содержание поля не соответствует ожиданиям'
                )

    def test_create_edit_post_page_show_form_correct_in_context(self):
        """Шаблоны 'post_create' и 'post_edit' сформированы с
        правильным контекстом."""
        reverse_list = PostPagesTests.reverse_list[4:]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for rev in reverse_list:
            response = self.authorized_client.get(rev)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(
                        form_field, expected,
                        f'Тип поля "{value}" не соответствует ожиданиям')
