import asyncio
import itertools
from functools import reduce
from math import ceil

import aiohttp
from bs4 import BeautifulSoup

from classes import Category, ProductUrl
from connector import get_connection
from logger import get_logger

logger = get_logger(f"main.{__name__}")


async def get_pagination(session: aiohttp.ClientSession, url: str) -> tuple[int, int] | tuple[None, None]:
    """Find pagination block that contains amount if products."""
    resp = await get_connection(session, url)
    # can't get response
    if resp is None:
        return None, None

    soup = BeautifulSoup(await resp.text(), "lxml")
    total_pr_block = soup.find("div", class_="load-total")
    if total_pr_block is None:
        return 1, -1
    pr_total = filter(lambda x: x.isdigit(), total_pr_block.text)
    pr_total = int("".join(pr_total))
    pages = ceil(pr_total / 60)  # each page contains 60 products or fewer
    return pages, pr_total


async def scrap_one_page(session: aiohttp.ClientSession, url: str) -> list[str] | None:
    """"""
    resp = await get_connection(session, url)
    # can't get response
    if resp is None:
        return None

    soup = BeautifulSoup(await resp.text(), "lxml")
    products_cards = soup.find_all("div", class_="catalog-table__row")
    a_blocks = [product_card.find("a", class_="cartTitle") for product_card in products_cards]
    links = [a_block.get("href") for a_block in a_blocks]
    return links


async def scrap_category(session: aiohttp.ClientSession, cat: Category) -> list[ProductUrl] | Category:
    """Scraps category.
    Uses 'scrap_one_page' function to scrap single category page and 'get_pagination'
    function to get number of pages and products.
    If any response from other function is None, function returns 'Category' class
    ('cat' from params) to rescrap it later.
    """
    pages, products_expected = await get_pagination(session, cat.link)
    # can't get number of pages
    if pages is None:
        logger.warning(f"For category '{cat.subcategory}' returned None "
                       f"cause couldn't get number of pages.")
        return cat
    # scrap all pages of category (and get products)
    tasks = [
        scrap_one_page(session, f"{cat.link}?PAGEN_1={page}")
        for page in range(1, pages + 1)
    ]
    links_up = await asyncio.gather(*tasks)
    links = reduce(lambda x, y: x + y, links_up)
    # links list contains unscraped elements
    if any(map(lambda x: x is None, links)):
        logger.warning(f"For category '{cat.subcategory}' returned category from param "
                       f"cause list contains {links.count(None)} None.")
        return cat
    # gen products urls list
    product_urls = [
        ProductUrl(category=cat.category, subcategory=cat.subcategory, link=f"https://pipeprice.ru{link}")
        for link in links
    ]
    # info logs
    logger.debug(f"Category '{cat.subcategory}' scraped. Products "
                 f"{len(product_urls)} ({products_expected} expected)")
    if len(product_urls) != products_expected and products_expected != -1:
        logger.warning(f"Not all products got from '{cat.subcategory}' "
                       f"({len(product_urls)}/{products_expected}).")

    return product_urls


async def scrap_all_categories(session: aiohttp.ClientSession, cats: list[Category]) -> list[ProductUrl]:
    """"""
    tasks = [scrap_category(session, cat) for cat in cats]
    products_urls_p: list[list[ProductUrl] | Category] = await asyncio.gather(*tasks)

    products_urls: list[ProductUrl | Category] = []
    for item in products_urls_p:
        if isinstance(item, list):
            products_urls.extend(item)
        else:
            products_urls.append(item)

    logger.info(f"All categories scraped. Found: {len(products_urls)} products;"
                f" and {len(list(filter(lambda x: isinstance(x, Category), products_urls)))}"
                f" None (Not scraped categories)")
    return products_urls
