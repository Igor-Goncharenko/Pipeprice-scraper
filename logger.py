import logging

from consts import LOGS_FILE

# set log level for asyncio, charset_normalizer
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("charset_normalizer").setLevel(logging.WARNING)
logging.raiseExceptions = False


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    # file logs
    file_h = logging.FileHandler(LOGS_FILE)
    file_h.setLevel(logging.DEBUG)
    # console logs
    console_h = logging.StreamHandler()
    console_h.setLevel(logging.DEBUG)
    # set formatter
    formatter_file = logging.Formatter(
        "%(levelname)s - %(asctime)s - %(name)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s"
    )
    file_h.setFormatter(formatter_file)
    formatter_console = logging.Formatter(
        "%(levelname)s - %(asctime)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s"
    )
    console_h.setFormatter(formatter_console)
    # add handler to root logger
    logger.addHandler(console_h)
    logger.addHandler(file_h)

    return logger
