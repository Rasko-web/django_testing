from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.notes = Note.objects.create(title='Заголовок', text='Текст')
        cls.author = User.objects.create(username="Автор")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username="Читатель")
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        cls.form_data = {'text': "Text"}

    def test_user_can_create_note(self):
        "Проверка наличия формы на странице создагния и редактирования"
        urls = (
            'notes:add',
            'notes:edit',
        )
        self.client.force_login(self.author)
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name, args=(self.notes.id,))
                response = self.client.get(url)
                self.assertIn('form', response.context)

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
