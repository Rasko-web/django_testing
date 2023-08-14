from django.test import TestCase
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
        cls.form_data = {'text': "Text"}

    def test_author_have_form_on_edit(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = self.client.get(url)
        self.assertIn('form', response.context)

    def test_author_have_form_on_add(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)

    def test_note_in_context(self):
        "отдельная заметка передаётся на страницу со списком заметок в списке"
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.notes, object_list)

    def test_notes_by_one_author(self):
        "Нет заметок от другого пользователя"
        url = reverse("notes:list")
        self.client.force_login(self.reader)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes, object_list)
