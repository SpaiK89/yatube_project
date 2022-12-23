import shutil
import tempfile
from django.conf import settings
from ..models import Post, User, Group, Comment
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth',
                                              first_name='Vasya',
                                              last_name='Pupkin')
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.new_group = Group.objects.create(
            title='Новая группа',
            slug='test-slug-2',
            description='Новое тестовое описание',
        )
        Post.objects.create(
            author=cls.author, text='Тестовый пост', group=cls.group)
        cls.authorized_not_author = Client()
        cls.authorized_not_author.force_login(CreateFormTests.user)
        cls.image_gif_list = (
            (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'),
            (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')
        )
        cls.uploaded = SimpleUploadedFile(
            name='image.gif',
            content=cls.image_gif_list[0],
            content_type='image/gif'
        )
        cls.uploaded_2 = SimpleUploadedFile(
            name='image_2.gif',
            content=cls.image_gif_list[1],
            content_type='image/gif'
        )
        cls.form_data = {
            'text': 'Новый тестовый текст',
            'author': 'auth',
            'group': 1,
            'image': CreateFormTests.uploaded,
        }
        cls.form_data_new = {
            'text': 'Совершенно новый тестовый текст',
            'group': 2,
            'image': CreateFormTests.uploaded_2
        }
        cls.reverse_list = [
            reverse('posts:post_create'),
            (reverse('posts:post_edit', kwargs={'post_id': 1})),
            (reverse('posts:add_comment', kwargs={'post_id': 1})),
        ]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(CreateFormTests.author)

    def test_create_post(self):
        """Валидная форма создает запись в Pos0t."""
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            CreateFormTests.reverse_list[0],
            data=CreateFormTests.form_data, follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'auth'})
        )
        self.assertEqual(
            Post.objects.count(), posts_count + 1,
            'Количество записей в БД не соответствует ожидаемому'
        )
        self.assertTrue(
            Post.objects.filter(
                text='Новый тестовый текст',
                author=1,
                group=1,
                image='posts/image.gif'
            ).exists()
        )

    def test_create_post_not_authorized_client(self):
        """Не авторизованный пользователь не может создать запись в Post."""
        self.authorized_client.logout()
        posts_count = Post.objects.count()
        self.authorized_client.post(
            CreateFormTests.reverse_list[0],
            data=CreateFormTests.form_data, follow=True)
        self.assertEqual(
            Post.objects.count(), posts_count,
            'Количество записей в БД не соответствует ожидаемому'
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            CreateFormTests.reverse_list[1],
            data=CreateFormTests.form_data_new, follow=True
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        self.assertEqual(
            Post.objects.count(), posts_count,
            'Количество записей в БД не соответствует ожидаемому'
        )
        self.assertTrue(
            Post.objects.filter(
                text='Совершенно новый тестовый текст',
                author=1,
                group=2,
                image='posts/image_2.gif'
            ).exists()
        )

    def test_edit_post_not_authorized_client(self):
        """Не авторизованный пользователь не может редактировать
         запись в Post."""
        self.authorized_client.logout()
        posts_count = Post.objects.count()
        self.authorized_client.post(
            CreateFormTests.reverse_list[1],
            data=CreateFormTests.form_data_new, follow=True
        )
        self.assertEqual(
            Post.objects.count(), posts_count,
            'Количество записей в БД не соответствует ожидаемому'
        )
        self.assertFalse(
            Post.objects.filter(
                text='Совершенно новый тестовый текст',
                author=1
            ).exists()
        )

    def test_edit_post_not_author_client(self):
        """Не автор не может редактировать
         запись в Post."""
        posts_count = Post.objects.count()
        self.authorized_not_author.post(
            CreateFormTests.reverse_list[1],
            data=CreateFormTests.form_data_new, follow=True
        )
        self.assertEqual(
            Post.objects.count(), posts_count,
            'Количество записей в БД не соответствует ожидаемому'
        )
        self.assertFalse(
            Post.objects.filter(
                text='Совершенно новый тестовый текст',
                author=1
            ).exists()
        )

    def test_del_post(self):
        """Автор удаляет запись в Post."""
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_delete', kwargs={'post_id': 1}), follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(
            Post.objects.count(), posts_count - 1,
            'Количество записей в БД не соответствует ожидаемому'
        )

    def test_del_post_not_author(self):
        """Не автор не может удалить запись в Post."""
        posts_count = Post.objects.count()
        response = CreateFormTests.authorized_not_author.post(
            reverse('posts:post_delete', kwargs={'post_id': 1}), follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(
            Post.objects.count(), posts_count,
            'Количество записей в БД не соответствует ожидаемому'
        )

    def test_del_post_not_authorized_client(self):
        """Не авторизованный пользователь не может удалить запись в Post."""
        self.authorized_client.logout()
        posts_count = Post.objects.count()
        self.authorized_client.post(
            reverse('posts:post_delete', kwargs={'post_id': 1}), follow=True
        )
        self.assertEqual(
            Post.objects.count(), posts_count,
            'Количество записей в БД не соответствует ожидаемому'
        )

    def test_add_comment(self):
        """Валидная форма создает запись в Comment."""
        comment_count = Comment.objects.count()
        response = self.authorized_client.post(
            CreateFormTests.reverse_list[2],
            data={'text': 'Комментарий'}, follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': 1})
        )
        self.assertEqual(
            Comment.objects.count(), comment_count + 1,
            'Количество записей в БД не соответствует ожидаемому'
        )
        self.assertTrue(
            Comment.objects.filter(
                text='Комментарий',
                author=1,
            ).exists()
        )

    def test_add_comment_not_authorized_client(self):
        """Не авторизованный пользователь не может создать запись в Comment."""
        self.authorized_client.logout()
        comment_count = Comment.objects.count()
        self.authorized_client.post(
            CreateFormTests.reverse_list[2],
            data={'text': 'Комментарий'}, follow=True)
        self.assertEqual(
            Comment.objects.count(), comment_count,
            'Количество записей в БД не соответствует ожидаемому'
        )

    def test_add_comment_not_authorized_client(self):
        """Не авторизованный пользователь не может создать запись в Comment."""
        self.authorized_client.logout()
        comment_count = Comment.objects.count()
        self.authorized_client.post(
            CreateFormTests.reverse_list[2],
            data={'text': 'Комментарий'}, follow=True)
        self.assertEqual(
            Comment.objects.count(), comment_count,
            'Количество записей в БД не соответствует ожидаемому'
        )
