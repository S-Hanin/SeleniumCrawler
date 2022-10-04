# -*- coding: utf8 -*-
import gc
import logging
import time
import types

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
from spider.task import Task

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGGER = logging.getLogger(__name__)


class SeleniumSpider:

    def __init__(self, driver_class=webdriver.Chrome, options=None):
        self.__driver = driver_class
        self.__options = options or Options
        self.__stack = []

    def prepare(self, driver):
        pass

    @staticmethod
    def __configure_wait(driver: WebDriver):
        return WebDriverWait(driver, 30)

    def task_generator(self):
        yield

    def run(self):
        with self.__driver(options=self.__options) as driver:
            self.prepare(driver)
            wait = self.__configure_wait(driver)
            self.__process_cycle(wait, driver)

    def __process_cycle(self, wait: WebDriverWait, driver: WebDriver):
        try:
            for task in self.task_generator():
                next_task_generator = self.__process_task(driver, wait, task)
                self.__stack.append(next_task_generator)
                self.__process_subtasks(wait, driver)
        except StopSpiderException as ex:
            LOGGER.info("Spider stopped on StopSpiderException")
        except KeyboardInterrupt as ex:
            LOGGER.info("Spider stopped on KeyboardInterrupt")

    def __process_task(self, driver: WebDriver, wait: WebDriverWait, task: Task):
        try:
            task_result = self.__request(driver, wait, task)
            task_result_handler = getattr(self, f"task_{task.name}")
            return task_result_handler(driver, PyQuery(task_result), task)
        except NoSuchElementException as ex:
            LOGGER.warning(ex)
        except Exception as ex:
            LOGGER.warning(ex)

    def __process_subtasks(self, wait: WebDriverWait, driver: WebDriver):
        def default_generator():
            yield None

        while len(self.__stack) > 0:
            current_generator = self.__stack[-1] or default_generator()
            try:
                if not (task := next(current_generator, False)):
                    raise Exception
            except Exception as ex:
                LOGGER.warning(ex)
                self.__close_tab(driver)
                self.__stack.pop()
                gc.collect()
                continue

            following = self.__process_task(driver, wait, task)
            if isinstance(following, types.GeneratorType):
                self.__stack.append(following)
                self.__clean_stack(driver)
            else:
                self.__close_tab(driver)

    def __clean_stack(self, driver: WebDriver):
        if len(driver.window_handles) < len(self.__stack):
            del self.__stack[0]
            gc.collect()

    @staticmethod
    def __close_tab(driver: WebDriver):
        if len(driver.window_handles) > 1: driver.close()
        driver.switch_to.window(driver.window_handles[-1])

    @staticmethod
    def __request(driver: WebDriver, wait: WebDriverWait, task: Task):
        SeleniumSpider.__sleep_handler(driver, wait, task)
        SeleniumSpider.__target_handler(driver, wait, task)
        SeleniumSpider.__wait_handler(driver, wait, task)
        return driver.page_source

    @staticmethod
    def __sleep_handler(driver: WebDriver, wait: WebDriverWait, task: Task):
        if hasattr(task, "sleep"):
            time.sleep(getattr(task, "sleep", 0))

    @staticmethod
    def __target_handler(driver: WebDriver, wait: WebDriverWait, task: Task):
        if hasattr(task, "url"):
            if getattr(task, "new_tab", False):
                driver.execute_script('''window.open("about:blank");''')
                driver.switch_to.window(driver.window_handles[-1])
            driver.get(task.url)
        elif hasattr(task, "xpath"):
            retry(3, SeleniumSpider.__click_by_xpath,
                  lambda: driver.refresh(),
                  driver, wait, task)
        elif hasattr(task, "css"):
            retry(3, SeleniumSpider.__click_by_css,
                  lambda: driver.refresh(),
                  driver, wait, task)

    @staticmethod
    def __click_by_xpath(driver: WebDriver, wait: WebDriverWait, task: Task):
        el = driver.find_element_by_xpath(task.xpath)
        ActionChains(driver).move_to_element(el).perform()
        wait.until(EC.visibility_of(el))
        el = wait.until(EC.element_to_be_clickable([By.XPATH, task.xpath]))
        time.sleep(0.5)
        el.click()
        driver.switch_to.window(driver.window_handles[-1])

    @staticmethod
    def __click_by_css(driver: WebDriver, wait: WebDriverWait, task: Task):
        el = driver.find_element_by_css_selector(task.css)
        ActionChains(driver).move_to_element(el).perform()
        wait.until(EC.visibility_of(el))
        el = wait.until(EC.element_to_be_clickable([By.CSS_SELECTOR, task.css]))
        time.sleep(0.5)
        el.click()
        driver.switch_to.window(driver.window_handles[-1])

    @staticmethod
    def __wait_handler(driver: WebDriver, wait: WebDriverWait, task: Task):
        if hasattr(task, "wait"):
            wait.until(task.wait)
