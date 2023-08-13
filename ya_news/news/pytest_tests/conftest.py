import pytest
from django.utils import timezone
from datetime import datetime, timedelta
from news.models import News, Comment
from django.conf import settings


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
        pk='news-pk',
        author=author,
    )
    return news


@pytest.fixture
def list_of_news():
    today = datetime.today()
    news_list = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость{index}',
            text='Text',
            date=today - timedelta(days=index)
        )
        news_list.append(news)
    News.objects.bulk_create(news_list)
    return news_list


@pytest.fixture
def pk_for_args(news):
    return news.pk,


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text="text",
        author=author
    )
    return comment


@pytest.fixture
def id_for_comment(comment):
    return comment.id


@pytest.fixture
def comments_list(author, news):
    today = timezone.now()
    comments_list = []
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f"text {index}"
        )
        comment.created = today + timedelta(days=index)
        comments_list.append(comment)
        comment.save()
    return comments_list
