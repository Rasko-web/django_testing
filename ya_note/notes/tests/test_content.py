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

    def test_author_have_form_on_add_and_edit(self):
        "Проверка наличия формы на странице создания и редактирования"
        urls = (
            ('notes:add', None),
            ('notes:edit', self.notes.id)
        )
        for name, argument in urls:
            self.client.force_login(self.author)
            url = reverse(name, args=(argument,))
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
        url = reverse("notes:add")
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(new_note.text, self.form_data['text'])
