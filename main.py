import asyncio
from time import perf_counter

import aiohttp

from catalog_scraper import scrap_catalog
from category_scraper import scrap_all_categories
from classes import Category, ProductUrl
from connector import get_connection
from consts import CATS_SAVE_PATH, PR_URL_SAVE_PATH, PR_SAVE_PATH, PR_URL_SAVE_PATH_EXTRA, CATS_SAVE_PATH_EXTRA
from logger import get_logger
from product_scraper import scrap_products
from utils import load_from_csv, save_to_csv

logger = get_logger("main")

# USE_PRE_GOT_INF <-> "use previously got information"
USE_PRE_GOT_INF: bool = True


async def main() -> None:
    logger.debug("Scraper started work.")
    start_time = perf_counter()
    rewrite_data_cats = rewrite_data_pr_urls = None
    try:
        timeout = aiohttp.ClientTimeout(total=60 * 60 * 10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            if not USE_PRE_GOT_INF:
                # scrap catalog/get categories
                # 1 request that's why we don't need to save/load
                categories = await scrap_catalog(session=session)
                # save categories to extra file
                categories = [Category(*line) for line in categories]
                await save_to_csv(CATS_SAVE_PATH_EXTRA, categories)

                logger.debug(f"Categories got. Now worktime: {perf_counter() - start_time:.2f}s")
            else:
                # load data
                data = await load_from_csv(CATS_SAVE_PATH)
                categories = [Category(*line) for line in data]
            # scrap product urls
            products_urls = await scrap_all_categories(session, categories)
            # filter categories from products urls list
            not_scraped_cats = list(filter(lambda x: isinstance(x, Category), products_urls))
            products_urls = list(filter(lambda x: not isinstance(x, Category), products_urls))
            # write new categories data
            rewrite_data_cats = [[cat.category, cat.subcategory, cat.link] for cat in not_scraped_cats]
            await save_to_csv(CATS_SAVE_PATH, rewrite_data_cats)

            # write new product urls data to extra file
            if not USE_PRE_GOT_INF:
                pr_urls_formatted = [[pr_url.category, pr_url.subcategory, pr_url.link]
                                     for pr_url in products_urls]
                await save_to_csv(PR_URL_SAVE_PATH_EXTRA, pr_urls_formatted)

            logger.debug(f"Product urls got. Now worktime: {perf_counter() - start_time:.2f}s")

            if USE_PRE_GOT_INF:
                # load data
                data = await load_from_csv(PR_URL_SAVE_PATH)
                products_urls.extend([ProductUrl(*line) for line in data])

            products = await scrap_products(session, products_urls)
            # filter products urls from products list
            not_scraped_pr_urls = list(filter(lambda x: isinstance(x, ProductUrl), products))
            products = list(filter(lambda x: not isinstance(x, ProductUrl), products))

            logger.debug(f"Products got. Now worktime: {perf_counter() - start_time:.2f}s")

            # write new product urls data
            rewrite_data_pr_urls = [[pr_url.category, pr_url.subcategory, pr_url.link]
                                    for pr_url in not_scraped_pr_urls]
            await save_to_csv(PR_URL_SAVE_PATH, rewrite_data_pr_urls)

            # write products data
            # TODO: create empty file if it does not exist (does not work without that)
            old_data = (await load_from_csv(PR_SAVE_PATH))[1:]  # load old products data (and remove header)
            data: list[list] = [product.list_view() for product in products]
            pr_headers = ["name", "price", "link", "category", "subcategory", "image_urls", "in_stock"]
            await save_to_csv(PR_SAVE_PATH, old_data + data, pr_headers)

    except KeyboardInterrupt:
        logger.debug("Program ended work with 'KeyboardInterrupt'.")

    finally:
        logger.info(f"Scraper ended work. "
                    f"Worktime: {perf_counter() - start_time:.2f}s; "
                    f"Connection function calls: {get_connection.count};"
                    f"Successful requests: {get_connection.successful_requests}.")


if __name__ == '__main__':
    asyncio.run(main())
