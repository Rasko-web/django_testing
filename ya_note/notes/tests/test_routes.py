from http import HTTPStatus
from django.contrib.auth import get_user_model

from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_pages_aviability(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_availability_for_author(self):
        "Доступность страниц отдельной заметки,"
        "удаления и редактирования для автора"
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:delete', 'notes:edit'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_fro_aninymos_client(self):
        "Тест на редирект анонимного пользователя"
        urls = (
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', self.notes.slug),
            ('notes:edit', self.notes.slug),
            ('notes:delete', self.notes.slug),
        )
        login_url = reverse('users:login')
        for name, slug in urls:
            with self.subTest(name=name, slug=slug):
                if slug is None:
                    url = reverse(name)
                    redirect_url = f'{login_url}?next={url}'
                    response = self.client.get(url)
                    self.assertRedirects(response, redirect_url)
                else:
                    url = reverse(name, args=(slug,))
                    redirect_url = f'{login_url}?next={url}'
                    response = self.client.get(url)
                    self.assertRedirects(response, redirect_url)

    def test_note_availability_for_auth_user(self):
        "Доступность списка заметок, добавление новой заметки"
        "и успешного добавления заметки Аутентифицированному пользователю"
        users_statuses = (
            (self.author, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:delete', 'notes:edit'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
