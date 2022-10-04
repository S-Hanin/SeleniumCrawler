# -*- coding: utf8 -*-
from selenium.common.exceptions import ElementClickInterceptedException

from spider.exceptions import StopSpiderException
from spider.spider import LOGGER


def retry(count, function, callback, *args, **kwargs):
    for _ in range(count):
        try:
            function(*args, **kwargs)
            return
        except ElementClickInterceptedException as err:
            LOGGER.warning(f"Attemp {_} of {count} failed: {err}")
            callback()
    else:
        LOGGER.critical("Retry failed")
        raise StopSpiderException("Element click was intercepted")
