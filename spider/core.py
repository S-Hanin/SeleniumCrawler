# -*- coding: utf8 -*-
import gc
import logging
import time
import types
from typing import Union

from pyquery import PyQuery
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from spider.common import retry
from spider.exceptions import StopSpiderException
from spider.providers import ProvidersChain
from spider.task import Task

LOGGER = logging.getLogger(__name__)


class SeleniumSpider:

    def __init__(self, driver_class: WebDriver = None, options=None):
        """
        :param driver_class: Driver to use (Chrome, Firefox, etc). Chrome is used by default
        :param options: Specific options objects for the chosen driver (selenium.webdriver.chrome.options.Options)
        """
        self.__driver = driver_class or webdriver.Chrome
        self.__options = options or Options()
        self.__task_providers_chain: ProvidersChain = ProvidersChain(self.task_generator())

        # giving the possibility to define additional handlers for client class
        self.__target_handlers = [getattr(self, name) for name in dir(self)
                                  if "_target_handler" in name]

    def prepare(self, driver: WebDriver) -> None:
        pass

    @staticmethod
    def __configure_wait(driver: WebDriver) -> WebDriverWait:
        return WebDriverWait(driver, 30)

    def task_generator(self) -> types.GeneratorType:
        yield

    def run(self) -> None:
        with self.__driver(options=self.__options) as driver:
            self.prepare(driver)
            wait = self.__configure_wait(driver)
            self.__process_cycle(wait, driver)

    def __process_cycle(self, wait: WebDriverWait, driver: WebDriver) -> None:
        try:
            for task in self.__task_providers_chain.items():
                next_task_provider = self.__process_task(driver, wait, task)
                self.__handle_next_task_provider(driver, next_task_provider)
        except StopSpiderException as ex:
            LOGGER.info("Spider stopped on StopSpiderException")
        except KeyboardInterrupt as ex:
            LOGGER.info("Spider stopped on KeyboardInterrupt")

    def __handle_next_task_provider(self, driver: WebDriver, task_provider: types.GeneratorType) -> None:
        # checking task_provider type because handler may return any type
        if isinstance(task_provider, types.GeneratorType):
            self.__task_providers_chain.add_provider(task_provider)
        else:
            self.__close_tab(driver)

    def __process_task(self, driver: WebDriver, wait: WebDriverWait, task: Task) -> Union[types.GeneratorType, None]:
        if not task:
            return
        try:
            task_result = self.__request(driver, wait, task)
            task_result_handler = getattr(self, f"task_{task.name}")
            return task_result_handler(driver, PyQuery(task_result), task)
        except NoSuchElementException as ex:
            LOGGER.warning(ex)
        except Exception as ex:
            LOGGER.warning(ex)

    @staticmethod
    def __close_tab(driver: WebDriver) -> None:
        if len(driver.window_handles) > 1: driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        gc.collect()

    def __request(self, driver: WebDriver, wait: WebDriverWait, task: Task) -> str:
        self.__handle_sleep(driver, wait, task)
        self.__process_request(driver, wait, task)
        self.__handle_wait(driver, wait, task)
        return driver.page_source

    @staticmethod
    def __handle_sleep(driver: WebDriver, wait: WebDriverWait, task: Task) -> None:
        if task.sleep > 0:
            time.sleep(task.sleep)

    def __process_request(self, driver: WebDriver, wait: WebDriverWait, task: Task) -> None:
        for handler in self.__target_handlers:
            handler(driver, wait, task)

    @staticmethod
    def __url_target_handler(driver: WebDriver, wait: WebDriverWait, task: Task) -> None:
        if task.url:
            if getattr(task, "_new_tab"):
                driver.execute_script('''window.open("about:blank");''')
                driver.switch_to.window(driver.window_handles[-1])
            driver.get(task.url)

    @staticmethod
    def __xpath_target_handler(driver: WebDriver, wait: WebDriverWait, task: Task) -> None:
        if task.xpath:
            retry(3, SeleniumSpider.__click_by_xpath,
                  lambda: driver.refresh(),
                  driver, wait, task)

    @staticmethod
    def __click_by_xpath(driver: WebDriver, wait: WebDriverWait, task: Task) -> None:
        el = driver.find_element_by_xpath(task.xpath)
        ActionChains(driver).move_to_element(el).perform()
        wait.until(EC.visibility_of(el))
        el = wait.until(EC.element_to_be_clickable([By.XPATH, task.xpath]))
        time.sleep(0.5)
        el.click()
        driver.switch_to.window(driver.window_handles[-1])

    @staticmethod
    def __cssquery_target_handler(driver: WebDriver, wait: WebDriverWait, task: Task) -> None:
        if task.css:
            retry(3, SeleniumSpider.__click_by_css,
                  lambda: driver.refresh(),
                  driver, wait, task)

    @staticmethod
    def __click_by_css(driver: WebDriver, wait: WebDriverWait, task: Task) -> None:
        el = driver.find_element_by_css_selector(task.css)
        ActionChains(driver).move_to_element(el).perform()
        wait.until(EC.visibility_of(el))
        el = wait.until(EC.element_to_be_clickable([By.CSS_SELECTOR, task.css]))
        time.sleep(0.5)
        el.click()
        driver.switch_to.window(driver.window_handles[-1])

    @staticmethod
    def __handle_wait(driver: WebDriver, wait: WebDriverWait, task: Task) -> None:
        if task.wait:
            wait.until(task.wait)
