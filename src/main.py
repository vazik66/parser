import asyncpg
import aiohttp
import bs4
import asyncio
import re
from datetime import datetime
from dataclasses import dataclass
import logging
import signal
import os

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

HABR_URL = "https://habr.com"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"


@dataclass
class Article:
    title: str
    body: str
    published_at: datetime
    author_url: str
    author_username: str
    article_url: str | None
    hub: str | None


class HubRepository:
    def __init__(self, db: asyncpg.Connection) -> None:
        self.db = db

    async def get_hubs(self) -> list[str]:
        result = await self.db.fetch("SELECT hub_url from hubs;")
        if len(result) == 0:
            return []
        return [r.get("hub_url") for r in result]


class ArticleRepository:
    def __init__(self, db: asyncpg.Connection) -> None:
        self.db = db

    async def save(self, articles: list[Article]) -> None:
        q = """
        INSERT INTO articles (
            article_url,
            title,
            body,
            author_url,
            author_username,
            published_at,
            hub
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT DO NOTHING
        ;"""

        args = [
            (
                a.article_url,
                a.title,
                a.body,
                a.author_url,
                a.author_username,
                a.published_at,
                a.hub,
            )
            for a in articles
        ]
        try:
            await self.db.executemany(q, args)
        except Exception as e:
            print(e)


class Scraper:
    def __init__(self, repo: ArticleRepository):
        self.repo = repo

    async def run(self, hubs: list[str]):
        self.session = aiohttp.ClientSession(headers={"User-Agent": USER_AGENT})

        for hub in hubs:
            log.info("Starting: %s hub", hub.removesuffix(HABR_URL))
            articles_tasks = []
            article_urls = await self._run_hub_parsing(hub)
            log.info("Found %s articles", len(article_urls))

            articles_tasks.extend(
                asyncio.create_task(self._run_article_parsing(url, hub))
                for url in article_urls
            )

            # ~ 20 req
            articles = await asyncio.gather(*articles_tasks)
            await self.repo.save(articles)

        await self.session.close()

    async def _get_page_data(self, url: str) -> str:
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def _get_article_data(self, content: str) -> Article:
        soup = bs4.BeautifulSoup(content, "html.parser")

        title = soup.find(class_="tm-title").text
        body = soup.find(id="post-content-body").text

        author = soup.find("a", class_="tm-user-info__username")
        username = ""
        author_url = ""

        if author:
            username = author.text.strip()
            author_url = author.get("href")

        date_published = soup.find(class_="tm-article-datetime-published").time.get(
            "datetime"
        )

        return Article(
            title=title,
            body=body,
            author_url=author_url,
            author_username=username,
            published_at=datetime.strptime(date_published, DATE_FORMAT),
            article_url="",
            hub="",
        )

    async def _get_article_urls(self, content: str) -> list[str]:
        soup = bs4.BeautifulSoup(content, "html.parser")
        links = soup.find_all(
            "a", href=re.compile("\d+"), attrs={"data-article-link": "true"}
        )
        return [link.get("href") for link in links]

    async def _run_hub_parsing(self, flow: str) -> list[str]:
        hub_content = await self._get_page_data(flow)
        return await self._get_article_urls(hub_content)

    async def _run_article_parsing(self, article_url: str, hub: str) -> Article:
        article_content = await self._get_page_data(HABR_URL + article_url)
        article_data = await self._get_article_data(article_content)

        article_data.hub = hub.removeprefix(HABR_URL)
        article_data.article_url = article_url

        return article_data


async def run_sheduled(hub_repo: HubRepository, func, interval_seconds: int = 10 * 60):
    log.info("Scraper is started")
    while True:
        hubs = await hub_repo.get_hubs()
        log.info("Scraping %s hubs", len(hubs))

        await asyncio.gather(
            asyncio.sleep(interval_seconds),
            func(hubs),
        )


async def main():
    db_uri = os.environ.get("DB_URI")
    if not db_uri:
        raise ValueError("no db uri env")

    db = await asyncpg.connect(db_uri)

    article_repo = ArticleRepository(db)
    hubs_repo = HubRepository(db)
    scraper = Scraper(article_repo)

    try:
        await run_sheduled(hubs_repo, scraper.run, 60)
    finally:
        await db.close()


async def shutdown(loop: asyncio.AbstractEventLoop):
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


if __name__ == "__main__":
    _loop = asyncio.get_event_loop()
    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        _loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(_loop)))

    try:
        _loop.run_until_complete(main())
    finally:
        log.info("Stopping")
        _loop.close()
