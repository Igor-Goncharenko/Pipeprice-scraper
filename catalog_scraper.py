from functools import reduce

import aiohttp
from bs4 import BeautifulSoup

from classes import Category
from connector import get_connection
from logger import get_logger

logger = get_logger(f"main.{__name__}")


async def scrap_cat_block(soup: BeautifulSoup) -> list[Category]:
    """Finds name of category and names of subcategories and their links.
    Return list of Category.
    """
    cat_name = soup.find("div", class_="block-heading").text.strip()
    sub_cats = soup.find_all("a")
    cats = [
        Category(
            category=cat_name,
            subcategory=a.text.strip(),
            link=f"https://pipeprice.ru{a.get('href')}"
        )
        for a in sub_cats
    ]
    return cats


async def scrap_catalog(session: aiohttp.ClientSession) -> list[Category]:
    """Scraps categories from 'https://pipeprice.ru/'.
    Returns list of items that contains category name, subcategory name and link.
    """
    url = "https://pipeprice.ru/"
    resp = await get_connection(session, url)
    soup = BeautifulSoup(await resp.text(), "lxml")
    short_catalog_blocks = soup.find_all("div", class_="short-catalog-block")
    cats_up = [await scrap_cat_block(short_catalog_block)
               for short_catalog_block in short_catalog_blocks]
    cats = reduce(lambda x, y: x + y, cats_up)
    logger.info(f"Categories found: {len(cats)}.")
    return cats
