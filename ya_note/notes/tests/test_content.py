from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.notes = Note.objects.create(title='Заголовок', text='Текст')
        cls.author = User.objects.create(username="Автор")
        cls.reader = User.objects.create(username="Читатель")
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note_slug',
            author=cls.author
        )
        cls.form_data = {'text': "Text"}

    def test_author_have_form_on_add(self):
        "Проверка наличия формы на странице создания"
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('from', response.context)

    def test_author_have_form_on_edit(self):
        "Проверка наличия формы на странице редактированя"
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=self.notes.slug)
        response = self.client.get(url)
        self.assertIn('from', response.context)

    def test_note_in_context(self):
        "отдельная заметка передаётся на страницу со списком заметок в списке"
        users_statuses = (
            (self.author, True),
            (self.reader, False)
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            url = reverse('notes:list')
            response = self.client.get(url)
            object_list = response.context['object_list']
            self.assertIn(self.notes, object_list) is status

    def test_notes_by_one_author(self):
        url = reverse("notes:add")
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(new_note.text, self.form_data['text'])
