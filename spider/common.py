# -*- coding: utf8 -*-
import logging

from selenium.common.exceptions import ElementClickInterceptedException

from spider.exceptions import StopSpiderException

logger = logging.getLogger(__name__)


def retry(count, function, callback, *args, **kwargs):
    for _ in range(count):
        try:
            function(*args, **kwargs)
            return
        except ElementClickInterceptedException as err:
            logger.warning(f"Attemp {_} of {count} failed: {err}")
            callback()
    else:
        logger.critical("Retry failed")
        raise StopSpiderException("Element click was intercepted")
