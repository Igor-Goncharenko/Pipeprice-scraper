import aiocsv
import aiofiles

from logger import get_logger

logger = get_logger(f"main.{__name__}")


async def save_to_csv(filepath: str, data: list, headers: list = None) -> None:
    async with aiofiles.open(filepath, mode="w", newline="", encoding="utf-8") as acf:
        writer = aiocsv.AsyncWriter(acf, delimiter=";")
        # write header
        if headers is not None:
            await writer.writerow(headers)
        # write data
        await writer.writerows(data)
        logger.debug(f"Data saved to '{filepath}'. Total lines: {len(data)}")


async def load_from_csv(filepath: str) -> list[list[str]]:
    async with aiofiles.open(filepath, mode="r", encoding="utf-8") as acf:
        reader = aiocsv.AsyncReader(acf, delimiter=";")
        data = []
        async for line in reader:
            data.append(line)
        logger.debug(f"Data loaded from '{filepath}'. Total lines: {len(data)}")

        return data
