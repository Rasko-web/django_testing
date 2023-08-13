from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError
import pytest
from django.urls import reverse

from news.models import Comment
from news.forms import WARNING, BAD_WORDS


def test_user_can_create_note(author_client, author, form_data):
    "Авторизированный пользоваетль может оставить комментарий"
    url = reverse('news:edit')
    response = author_client.post(url, data=form_data)
    assertRedirects(response, reverse('notes:success'))
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data):
    "Анонимный пользоваетль не может оставить комментарий"
    url = reverse('news:edit')
    response = client.post(url, data=form_data)
    assertRedirects(response, url)
    assert Comment.objects.count() == 0


def test_warning_words(author_client, form_data):
    "Проверка на наличии запрещенных слов"
    bad_words_data = f'Text {BAD_WORDS[0]}'
    url = reverse('news:edit')
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_edit_comment(
        author_client,
        form_data,
        news,
        comment):
    "Автор может редактировать свой комментарий"
    url = reverse('news:edit', args=(news.id,))
    response = author_client.post(url, form_data)
    redirect = (reverse('news:detail', args=(news.id,))) + '#comments'
    assertRedirects(response, redirect)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_other_user_cant_edit_note(
        admin_client,
        form_data,
        pk_for_args,
        comment):
    "Пользователь не может редактировать чужой комментарий"
    url = reverse('news:edit', args=(pk_for_args,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    comment_from_db = Comment.objects.get(id=pk_for_args)
    assert comment.text == comment_from_db.text


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, pk_for_args):
    "Автор комментария может удалить свой комментарий"
    url = reverse('news:delete', args=pk_for_args)
    response = author_client.post(url)
    assertRedirects(response, reverse('notes:success'))
    commets_count = Comment.objects.count()
    assert commets_count == 0


@pytest.mark.django_db
def test_other_user_cant_delete_comment(admin_client, form_data, pk_for_args):
    "Пользователь не может удалить чужой комментарий"
    url = reverse('news:delete', args=pk_for_args)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    commets_count = Comment.objects.count()
    assert commets_count == 1
