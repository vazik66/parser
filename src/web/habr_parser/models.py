from django.db import models


class Hub(models.Model):
    hub_url = models.TextField(unique=True)

    class Meta:
        db_table = "hubs"

    def __str__(self) -> str:
        return self.hub_url.removeprefix("https://habr.com/ru/")


class Article(models.Model):
    article_url = models.TextField(unique=True)
    title = models.TextField()
    body = models.TextField()
    author_url = models.TextField()
    author_username = models.TextField()
    published_at = models.DateTimeField()
    hub = models.TextField()

    class Meta:
        db_table = "articles"

    def __str__(self) -> str:
        return self.title
