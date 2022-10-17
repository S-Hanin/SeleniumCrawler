# -*- coding: utf8 -*-
"""
Core logic
"""
import logging
import types
from typing import Type, Optional


from pyquery import PyQuery
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

from spider.exceptions import StopSpiderException
from spider.providers import ProvidersChain
from spider.task import Task
from spider.transport import BrowserTransport

LOGGER = logging.getLogger(__name__)


class SeleniumSpider:
    """
    Template class, supports task processing logic
    """

    def __init__(self, driver_class: Type[WebDriver] = None, options=None):
        """
        :param driver_class: Driver to use (Chrome, Firefox, etc). Chrome is used by default
        :param options: Specific options objects for the chosen driver
        (selenium.webdriver.chrome.options.Options)
        """
        self.__transport = BrowserTransport(driver_class or webdriver.Chrome,
                                            options or Options())
        self.__task_providers_chain: ProvidersChain = ProvidersChain(self.task_generator())

    def prepare(self, driver: WebDriver) -> None:
        """
        Allows to set up driver. Is executed before spider launches
        :param driver: WebDriver
        """
        pass

    def task_generator(self) -> types.GeneratorType:
        """
        Initial point to create Task(s)
        :return: Generator
        """
        yield

    def run(self) -> None:
        """
        Run crawling process
        """
        with self.__transport as transport:
            self.prepare(transport.driver)
            self.__process_cycle()

    def __process_cycle(self) -> None:
        try:
            for task in self.__task_providers_chain.items():
                next_task_provider = self.__process_task(task)
                self.__handle_next_task_provider(next_task_provider)
        except StopSpiderException as ex:
            LOGGER.info("Spider stopped on StopSpiderException: %s", ex)
        except KeyboardInterrupt as ex:
            LOGGER.info("Spider stopped on KeyboardInterrupt: %s", ex)
        except Exception as ex:
            LOGGER.critical(ex)

    def __process_task(self, task: Task) -> Optional[types.GeneratorType]:
        if task:
            try:
                task_result = self.__transport.request(task)
                task_result_handler = getattr(self, f"task_{task.name}")
                return task_result_handler(self.__transport.driver, PyQuery(task_result), task)
            except NoSuchElementException as ex:
                LOGGER.warning(ex)
        return None

    def __handle_next_task_provider(self, task_provider: types.GeneratorType) -> None:
        # checking task_provider type because handler may return any type
        if isinstance(task_provider, types.GeneratorType):
            self.__task_providers_chain.add_provider(task_provider)
        else:
            self.__transport.close_active_tab()
