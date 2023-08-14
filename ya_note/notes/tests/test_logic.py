from http import HTTPStatus
from pytils.translit import slugify
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = "Текст Заметки"

    @classmethod
    def setUpTestData(cls):
        cls.notes = Note.objects.create(title='Заголовок', text='Текст')
        cls.user = User.objects.create(username="Простой Человек")
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'text': cls.NOTE_TEXT}

    def test_anonymous_user_cant_create_note(self):
        "Анонимный пользователь не может оставить заметку"
        url = reverse('notes:detail', args=(self.notes.id,))
        self.client.post(url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_can_create_note(self):
        "Пользователь может оставить заметку"
        url = reverse('notes:detail', args=(self.notes.id,))
        response = self.auth_client.post(url, data=self.form_data)
        self.assertRedirects(response, f'{url}#list')
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.user)


class TestNoteEditDelite(TestCase):

    NOTE_TEXT = "Текст заметки"
    NEW_NOTE_TEXT = "Обновленная заметка"

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        cls.form_data = {'text': cls.NOTE_TEXT}
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_avialability_for_show_edit_delete(self):
        user_statues = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statues:
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_empty_slug(self):
        "Тест на пустой Slug"
        url = reverse('notes:add')
        self.form_data.pop(self.note.slug)
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        self.new_note = Note.objects.get()
        self.expected_slug = slugify(self.form_data['title'])
        self.assertEqual(self.new_note.slug, self.expected_slug)

    def test_not_unique_slug(self):
        "Тест на неуникальный Slug"
        url = reverse('notes:add')
        self.form_data[self.note.slug] = self.note.id
        response = self.author_client.get(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:add'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
