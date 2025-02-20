import time

import requests
from .log import logger


def get_2fa_code(key: str):
    logger.info(f"2fa key is {key}")
    url = f"https://2fa.zone/app/2fa.php?secret={key}"
    resp = requests.get(url)
    logger.info(resp.status_code)
    if resp.status_code == 200:
        data = resp.json()
        logger.info(f"2fa api response: {data}")
        return data.get("newCode", "")
    return ""


def log_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting {func.__name__}()")
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Finished {func.__name__}()")
        logger.info(f"Execution time: {execution_time:.2f} seconds")
        return result

    return wrapper
