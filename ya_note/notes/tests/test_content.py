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

    def test_author_have_form_on_add(self):
        "Проверка наличия формы на странице создания"
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('from', response.context)

    def test_author_have_form_on_edit(self):
        "Проверка наличия формы на странице редактированя"
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.notes.id,))
        response = self.client.get(url)
        self.assertIn('from', response.context)
