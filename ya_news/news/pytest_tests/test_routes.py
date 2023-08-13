from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects
import pytest


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('pk_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    )
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_availability_for_anonymous_user(author_client, name, args):
    # Главная, страница новости, регистрации,
    # логина и выхода из аккаунта доступны анонимному пользователю:
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
    # Проверка доступности страниц редактирования
    # и удаления комментария автором и другим пользователем
        parametrized_client, name, comment, expected_status
):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name'
    ('news:edit', 'news:delete'),
)
def test_redirects(admin_client, name, comment):
    # Тест на перенаправление анонимного пользователя на страницу логина
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = admin_client.get(url)
    assertRedirects(response, expected_url)
