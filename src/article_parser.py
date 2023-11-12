import bs4
import utils
from dataclasses import dataclass
from datetime import datetime
import asyncio

articles_urls = ["/ru/articles/772462/", "/ru/companies/chatapp/articles/772616/"]
article_filename = "article.html"
habr_url = "https://habr.com"

date_format = "%y-%m-%dt%h:%m:%s.%fz"


@dataclass
class Article:
    title: str
    body: str
    published_at: datetime
    author_url: str
    author_username: str
    article_url: str | None


def parse_article(content: str) -> Article:
    soup = bs4.BeautifulSoup(content, "html.parser")

    title = soup.find(class_="tm-title").text
    body = soup.find(id="post-content-body").text

    author = soup.find("a", class_="tm-user-info__username")
    username = author.text.strip()
    author_url = author.get("href")

    date_published = soup.find(class_="tm-article-datetime-published").time.get(
        "datetime"
    )

    article = Article(
        title=title,
        body=body,
        author_url=HABR_URL + author_url,
        author_username=username,
        published_at=datetime.strptime(date_published, DATE_FORMAT),
    )
    return article


async def parse_articles(urls: list[str]) -> list[Article]:
    tasks = []
    for url in urls:
        tasks.append(asyncio.create_task(utils.get_page(HABR_URL + url)))
        # content = utils.get_page(HABR_URL + url)
        # article = parse_article(content)
        # articles.append(article)

    contents = await asyncio.gather(*tasks)
    articles = []
    for content in contents:
        articles.append(parse_article(content))

    print(len(articles))
    print(articles)
    return articles


asyncio.run(parse_articles(ARTICLES_URLS))

# articles = parse_articles(ARTICLES_URLS)

# content = utils.get_page("https://habr.com" + ARTICLES_URLS[0])
# utils.save_page(content, ARTICLE_FILENAME)

# content = utils.load_page(ARTICLE_FILENAME)
# with open("articles.txt", "r", encoding="utf-8") as f:
#     articles = f.read()

# articles = articles.split()
# articles = ["https://habr.com" + url for url in articles]

# print(articles)

# for article in articles:
#     content = utils.get_page(article)
#     utils.save_page(content, ARTICLE_FILENAME)

#     content = utils.load_page(ARTICLE_FILENAME)

#     parse_article(content)
