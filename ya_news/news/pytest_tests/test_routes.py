from http import HTTPStatus
from django.urls import reverse
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
        parametrized_client, name, news, expected_status
):
    url = reverse(name, args=(news.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('pk_for_args')),
        ('news:delete', pytest.lazy_fixture('pk_for_args')),
    ),
)
def test_redirects(client, name, args, pk_for_args):
    # Тест на перенаправление анонимного пользователя на страницу логина
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response == expected_url
