from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError
import pytest
from django.urls import reverse
from random import choice
from news.models import Comment
from news.forms import WARNING, BAD_WORDS


def test_user_can_create_comment(
        author_client,
        author,
        form_data,
        news,):
    """Авторизированный пользоваетль может оставить комментарий"""
    comments_count_before = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    """Анонимный пользоваетль не может оставить комментарий"""
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_warning_words(author_client, form_data, news):
    """Проверка на наличии запрещенных слов"""
    url = reverse('news:detail', args=(news.id,))
    form_data['text'] = f'Text {choice(BAD_WORDS)}'
    response = author_client.post(url, data=form_data)
    assertFormError(
        response,
        'form',
        'text',
        WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_edit_comment(
        author_client,
        form_data,
        news,
        comment):
    """Автор может редактировать свой комментарий"""
    url = reverse('news:edit', args=(news.id,))
    response = author_client.post(url, form_data)
    redirect = (reverse('news:detail', args=(news.id,))) + '#comments'
    assertRedirects(response, redirect)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, news, comment):
    """Автор комментария может удалить свой комментарий"""
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    redirect = (reverse('news:detail', args=(news.id,))) + '#comments'
    assertRedirects(response, redirect)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_other_user_cant_edit_note(
        admin_client,
        form_data,
        news,
        comment):
    """Пользователь не может редактировать чужой комментарий"""
    url = reverse('news:edit', args=(news.id,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    comment_from_db = Comment.objects.get(id=news.id)
    assert comment.text == comment_from_db.text


@pytest.mark.django_db
def test_other_user_cant_delete_comment(admin_client, form_data, comment):
    """Пользователь не может удалить чужой комментарий"""
    url = reverse('news:delete', args=(comment.id,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
