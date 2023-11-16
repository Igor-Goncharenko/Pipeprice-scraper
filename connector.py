import asyncio

import aiohttp

from logger import get_logger
from consts import HEADERS, PROXY

logger = get_logger(f"main.{__name__}")


def request_counter(func):
    """Decorator-counter."""
    def wrapper(*args, **kwargs):
        wrapper.count += 1
        res = func(*args, **kwargs)
        if res is not None:
            wrapper.successful_requests += 1
        return res

    wrapper.count = 0
    wrapper.successful_requests = 0
    return wrapper


@request_counter
async def get_connection(
        session: aiohttp.ClientSession,
        url: str,
        retries_left: int = 3
) -> aiohttp.ClientResponse | None:
    """Connection function."""
    try:
        resp = await session.get(url=url, headers=HEADERS, proxy=PROXY)
        return resp
    except aiohttp.ClientConnectionError:
        if retries_left > 0:
            await asyncio.sleep(2)
            logger.debug(f"Can't connect to {url}. Retries left: {retries_left}")
            return await get_connection(session=session, url=url, retries_left=retries_left - 1)

        logger.error(f"Can't connect to {url}. No more retries")
        return None
