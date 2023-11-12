import bs4
import re
from utils import get_page, save_page, load_page


URL = "https://habr.com/ru/flows/develop/articles/"
FILENAME = "habr.html"


def get_article_links(content: str) -> list[str]:
    soup = bs4.BeautifulSoup(content, "html.parser")
    links = soup.find_all(
        "a", href=re.compile("\d+"), attrs={"data-article-link": "true"}
    )
    print(f"Found {len(links)} article links")
    for i, link in enumerate(links):
        # print(f"{i+1}/{len(links)}", link.get("href"))
        print(link.get("href"))
    return [link.get("href") for link in links]


# content = get_page(URL)
# save_page(content, FILENAME)
content = load_page(FILENAME)
get_article_links(content)
