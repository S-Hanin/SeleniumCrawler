# -*- coding: utf8 -*-
import gc
import time
from typing import Optional, Type

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from spider.task import Task
from spider.common import retry


class BaseTransport:

    @property
    def driver(self):
        raise NotImplementedError

    def close_active_tab(self):
        raise NotImplementedError

    def request(self, task: Task):
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class BrowserTransport(BaseTransport):

    def __init__(self, driver: Type[WebDriver], options):
        self._driver_class: Type[WebDriver] = driver
        self._driver: Optional[WebDriver] = None
        self._options = options
        self._wait = None
        self._wait_timeout = 30
        self.__target_handlers = [getattr(self, name) for name in dir(self)
                                  if "_target_handler" in name]

    @property
    def driver(self):
        return self._driver

    def __enter__(self):
        self._driver = self._driver_class(options=self._options)
        self._wait = WebDriverWait(self.driver, self._wait_timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def close_active_tab(self) -> None:
        if len(self.driver.window_handles) > 1:
            self.driver.close()
            self.__set_last_tab_active()
        gc.collect()

    def request(self, task: Task) -> str:
        self.__handle_sleep(task)
        self.__process_request(task)
        self.__handle_wait(task)
        return self.driver.page_source

    def __handle_sleep(self, task: Task) -> None:
        if task.sleep > 0:
            time.sleep(task.sleep)

    def __process_request(self, task: Task) -> None:
        for handler in self.__target_handlers:
            handler(task)

    def __url_target_handler(self, task: Task) -> None:
        if task.url:
            if getattr(task, "_new_tab"):
                self.driver.execute_script('''window.open("about:blank");''')
                self.__set_last_tab_active()
            self.driver.get(task.url)

    def __xpath_target_handler(self, task: Task) -> None:
        if task.xpath:
            retry(3, self.__click_by_xpath,
                  lambda: self.driver.refresh(),
                  task)

    def __click_by_xpath(self, task: Task) -> None:
        element = self.driver.find_element_by_xpath(task.xpath)
        ActionChains(self.driver).move_to_element(element).perform()
        self._wait.until(EC.visibility_of(element))
        element = self._wait.until(EC.element_to_be_clickable([By.XPATH, task.xpath]))
        time.sleep(0.5)
        element.click()
        self.__set_last_tab_active()

    def __cssquery_target_handler(self, task: Task) -> None:
        if task.css:
            retry(3, self.__click_by_css,
                  lambda: self.driver.refresh(),
                  task)

    def __click_by_css(self, task: Task) -> None:
        element = self.driver.find_element_by_css_selector(task.css)
        ActionChains(self.driver).move_to_element(element).perform()
        self._wait.until(EC.visibility_of(element))
        element = self._wait.until(EC.element_to_be_clickable([By.CSS_SELECTOR, task.css]))
        time.sleep(0.5)
        element.click()
        self.__set_last_tab_active()

    def __set_last_tab_active(self):
        last_tab = self.driver.window_handles[-1]
        self.driver.switch_to.window(last_tab)

    def __handle_wait(self, task: Task) -> None:
        if task.wait:
            self._wait.until(task.wait)
