from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Автор")
        cls.reader = User.objects.create(username="Читатель")

        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note_slug',
            author=cls.author
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {'text': "Text"}

    def test_author_have_form_on_edit(self):
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = self.author_client.get(url)
        self.assertIn('form', response.context)

    def test_author_have_form_on_add(self):
        url = reverse('notes:add')
        response = self.author_client.get(url)
        self.assertIn('form', response.context)

    def test_note_in_context(self):
        "отдельная заметка передаётся на страницу со списком заметок в списке"
        url = reverse('notes:list')
        response = self.author_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.notes, object_list)

    def test_notes_by_one_author(self):
        "Нет заметок от другого пользователя"
        url = reverse("notes:list")
        response = self.reader_client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes, object_list)
