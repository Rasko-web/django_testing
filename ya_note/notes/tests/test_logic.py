from http import HTTPStatus
from pytils.translit import slugify
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = "Текст Заметки"
    NEW_NOTE_TEXT = "Обновленная заметка"

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="Простой Человек")
        cls.user_client = Client()
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {
            'title': 'Title',
            'text': 'Text',
            'slug': 'new_slug',
        }

    def test_auth_user_can_create_note(self):
        "Авторизированный пользователь оставляет заметку"
        url = reverse('notes:add')
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))

    def test_anonymous_user_cant_create_note(self):
        "Анонимный пользователь не может оставить заметку"
        url = reverse('notes:add')
        response = self.user_client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)

    def test_avialability_for_show_edit_delete(self):
        user_statues = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statues:
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_empty_slug(self):
        "Тест на пустой Slug"
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.form_data.pop('slug')
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_not_unique_slug(self):
        "Тест на неуникальный Slug"
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.form_data['slug'] = self.notes.slug
        response = self.author_client.post(url, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            self.notes.slug + WARNING
        )
