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
        cls.url = reverse('notes:detail', args=(cls.notes.id,))
        cls.author = User.objects.create(username="Автор")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username="Читатель")
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.notes = Note.objects.create(
            author=cls.author,
            text=cls.NOTE_TEXT
        )
        cls.edit_url = reverse('notes:edit', args=(cls.notes.id,))
        cls.url_to_success = reverse('notes:success')
        cls.delete_url = reverse('delete:edit', args=(cls.notes.id,))
        cls.form_data = {'text': cls.NEW_NOTE_TEXT}

    def test_author_can_delete_note(self):
        "Автор может удалить заметку"
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_to_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_reader_cant_delete_note(self):
        "Читатель не может удалить заметку"
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        "Автор может редактировать заметку"
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_success)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.text, self.NEW_NOTE_TEXT)

    def test_reader_cant_edit_note(self):
        "Читатель может не редактировать заметку"
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.text, self.NOTE_TEXT)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_data.pop('slug')
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
        self.form_data['slug'] = self.notes.id
        response = self.author_client.get(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:add'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
