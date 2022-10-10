# -*- coding: utf8 -*-
import logging
import types

from pyquery import PyQuery
from selenium.webdriver.remote.webdriver import WebDriver

from spider.core import SeleniumSpider
from spider.exceptions import StopSpiderException
from spider.task import Task

logging.basicConfig(level=logging.INFO)


class SimpleSpider(SeleniumSpider):

    def task_generator(self) -> types.GeneratorType:
        yield Task(name="articles") \
            .add_url("https://habr.com/ru/all/") \
            .add_wait(lambda d: d.find_element_by_xpath("//div[@data-test-id='page-top']"))

    def task_articles(self, driver: WebDriver, pq: PyQuery, task: Task):
        pq.make_links_absolute("https://habr.com/ru/all/")
        for it in pq.items('article'):
            print(it.children('div>h2').text(), end="")
            href = it.children('div>h2>a').attr('href')
            yield Task(name="article") \
                .add_url(href, new_tab=True) \
                .add_wait(lambda d: d.find_element_by_xpath("//*[@class='tm-article-snippet__datetime-published']")) \
                .add_sleep(1)

        page_number = int(pq.find("span[data-test-id='pagination-current-page']").text())
        if page_number == 1: raise StopSpiderException("We reached the end")

        yield Task(name="articles") \
            .add_xpath("//a[@id='pagination-next-page']") \
            .add_wait(lambda d: d.find_element_by_xpath("//article")) \
            .add_sleep(2)

    def task_article(self, driver: WebDriver, pq: PyQuery, task: Task):
        for item in pq.items(".tm-article-snippet__datetime-published"):
            print(f"\t{item.text()}")


if __name__ == '__main__':
    worker = SimpleSpider()
    worker.run()
