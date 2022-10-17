# -*- coding: utf8 -*-
"""
Common functions not related to main functionality
"""
import logging

from selenium.common.exceptions import ElementClickInterceptedException

from .exceptions import StopSpiderException

logger = logging.getLogger(__name__)


def retry(count, function, callback, *args, **kwargs) -> None:
    """
    Run action and repeat if it fails
    :param count: try to execute action 'count' of times
    :param function: action to run
    :param callback: action that potentially can correct the situation
    :param args: args that function accepts
    :param kwargs: kwargs that function accepts
    :return:
    """
    for _ in range(count):
        try:
            function(*args, **kwargs)
            break
        except ElementClickInterceptedException as err:
            logger.warning("Attemp %s of %s failed: %s", _, count, err)
            callback()
    else:
        logger.critical("Retry failed")
        raise StopSpiderException("Element click was intercepted")
