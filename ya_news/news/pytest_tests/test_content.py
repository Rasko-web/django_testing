import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_count_on_news_page(list_of_news, client):
    "Тест на колличество записей на странице"
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == 10


@pytest.mark.django_db
def test_news_order(list_of_news, client):
    "Порядок новостей"
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [list_of_news.date for list_of_news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(pk_for_args, client, comments_list):
    "Порядок комментариев"
    url = reverse('news:detail', args=(pk_for_args))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


def test_anonymous_client_has_no_form(client, pk_for_args):
    "Аноним не имеет формы отправки комментария"
    url = reverse('news:detail', args=(pk_for_args))
    response = client.get(url)
    assert 'form' not in response.context


def test_auth__client_have_form(admin_client, pk_for_args):
    "Авторизированныей пользователь имеет форму отправки комментария"
    url = reverse('news:detail', args=(pk_for_args))
    response = admin_client.get(url)
    assert 'form' in response.context
