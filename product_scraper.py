import asyncio
from math import ceil

import aiohttp
from bs4 import BeautifulSoup

from classes import ProductUrl, Product
from connector import get_connection
from logger import get_logger

logger = get_logger(f"main.{__name__}")


async def scrap_product(session: aiohttp.ClientSession, pr_url: ProductUrl) -> Product | ProductUrl:
    """"""
    resp = await get_connection(session, pr_url.link)
    if resp is None:
        return pr_url

    soup = BeautifulSoup(await resp.text(), "lxml")
    # get main info
    try:
        name = soup.find("h1", class_="cartTitle").text
        # print(pr_url)
        price = soup.find("span", class_="price__value").text.replace(" ", "")
        in_stock = soup.find("span", class_="availability-details__text").text.strip() == "В наличии"
        gallery = soup.find("div", class_="gallery")
        # get photos
        photos = gallery.find_all("div", class_="gallery__main")
        photos_urls = list(map(lambda x: f"https://pipeprice.ru{x.find('img').get('src')})", photos))

        return Product(
            name=name,
            price=price.strip(),
            link=pr_url.link,
            category=pr_url.category,
            subcategory=pr_url.subcategory,
            image_urls=photos_urls,
            in_stock=in_stock,
        )
    except Exception as e:
        logger.warning(f"Can't get {pr_url.link}. {e.__class__.__name__}:{e.__traceback__.tb_lineno}")

    return pr_url


async def scrap_products(
        session: aiohttp.ClientSession, pr_urls: list[ProductUrl], chunk_size: int = 200
) -> list[Product | ProductUrl]:
    """Scraps all given products."""
    total_amount = len(pr_urls)
    products = []
    for chunk_low in range(0, ceil(total_amount / chunk_size) * chunk_size, chunk_size):
        chunk_up = min(chunk_low + chunk_size, total_amount)
        pr_url_to_scrap = pr_urls[chunk_low: chunk_up]
        tasks = [scrap_product(session, pr_url) for pr_url in pr_url_to_scrap]
        products_chunk = await asyncio.gather(*tasks)
        products.extend(products_chunk)
        logger.debug(f"Products got: {chunk_up}/{total_amount} ({chunk_up / total_amount * 100:.1f}%)")

    return products

