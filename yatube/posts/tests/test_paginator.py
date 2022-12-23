
from django.test import TestCase, Client
from ..models import Post, Group, User
from django.urls import reverse
from ..views import POSTS_PER_PAGE


class PaginatorViewsTest(TestCase):
    """Проверка работы паджинатора"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create(
            [Post(author=cls.author,
             text='Тестовый пост' + '' + str(i),
             group=cls.group)
             for i in range(14)]
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.reverse_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'})
        ]

    def test_first_page_contains_ten_records(self):
        """Сколько постов передается на первые страницы паджинатора """
        for rev in PaginatorViewsTest.reverse_list:
            response = self.authorized_client.get(rev)
            self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE,
                             'Паджинатор страницы работает не верно')

    def test_second_page_contains_three_records(self):
        """Сколько постов передается на вторые страницы паджинатора """
        for rev in PaginatorViewsTest.reverse_list:
            response = self.authorized_client.get(rev + '?page=2')
            if Post.objects.count() < POSTS_PER_PAGE * 2:
                self.assertEqual(len(response.context['page_obj']),
                                 Post.objects.count() - POSTS_PER_PAGE,
                                 'Паджинатор страницы работает не верно')
            else:
                self.assertEqual(len(response.context['page_obj']),
                                 POSTS_PER_PAGE,
                                 'Паджинатор страницы работает не верно')
