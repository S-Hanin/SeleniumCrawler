## SeleniumCrawler

### Aim

That's a wrapper for selenium web driver which aims to simplify getting information  
from web resources in case they use javascript to build the page or block using  
simple http libs like 'requests'.

There's no such things like multiprocessing or multithreading, just one browser instance,  
all works synchronously, that's not so trendy though.

### Precautions

Although I use this lib quite a long time it's still a homemade thing, so use it at your own risk.
- There's no good exception handling yet
- There's no good logging yet
- There's no unit tests yet

### Using

For sure the 'must have' knowledge is how selenium works, at least this knowledge will be helpful.

#### Simpliest case:

```python
import types
from pyquery import PyQuery
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options


from spider.core import SeleniumSpider
from spider.task import Task


class SimpleSpider(SeleniumSpider):

    def prepare(self, driver: WebDriver) -> None:
        pass

    def task_generator(self) -> types.GeneratorType:
        yield Task(name="articles")
        .add_url("https://habr.com/ru/all/")
        .add_wait(lambda d: d.find_element_by_xpath("//div[@data-test-id='page-top']"))

    def task_articles(self, driver: WebDriver, pq: PyQuery, task: Task):
       pq.make_links_absolute("https://habr.com/ru/all/")
       for it in pq.items("article"):
           print(it.children("div>h2").text(), end="")


if __name__ == "main":
    options = Options()
    options.headless = True
    worker = SimpleSpider(options=options)
    worker.run()
```

`def prepare(self, driver)` - this method is executed before the process begins.  
It gets driver object so it's possible to set up something before spider gets crawling

`def task_generator(self)` - that's the beginning of the crawler's jorney.  
Task generator should produce Task object(s).  
In this example I say that I want to open "https://habr.com/ru/all/" and wait while the certain element is displayed.

`task_articles(self, driver: WebDriver, pq: PyQuery, task: Task)` - that's how look like all request handlers.
After spider gets a response from browser, it calls a handler for task and passes instances of
`driver`, `pq` (which is a PyQuery object containing html) and `task` that triggered the call of this handler.

***There's a fully working example in 'examples/simple_spider.py'***

#### Task

`Task(name="articles")` - an object who tells the spider where it should go and what to do.
Parameter `name` tells to spider a name of the handler for this task.  
Note that handler's name is `task_articles` and name of the task is `articles`, that's a task naming convention.

It's possible to set up `Task` different ways:
* use url - selenium opens specified address
* use xpath selector - selenium finds element on the page and clicks it
* use css selector - selenium finds element on the page and clicks it
* use js script - selenium executes given javascript

examples:

```python
Task(name="articles") \
    .add_url("https://habr.com/ru/all/", new_tab=True) \  # open link in new tab
    .add_wait(lambda d: d.find_element_by_xpath("//div[@data-test-id='page-top']")) \  # wait until specified element will be found
    .add_sleep(2) \  # wait for 2 second before request
    .add_param("my_param", value) \ #  it's passible to pass params with the task to the handler and then get it by task.my_param    


Task(name="articles") \
    .add_xpath("//a[@id='pagination-next-page']")  # find element by xpath and click it

Task(name="article") \
    .add_css("div[id='some_id']>h2>a")  # find element by css query and click it

Task(name="articles") \
    .add_script("document.getElementById('pagination-next-page').click()")  # using js to operate the page
```

### Conditions of work

1. Having Chrome or Firefox or any other browser supported by selenuim
2. Having the driver for browser in the path  
   - [Crhome driver] https://chromedriver.chromium.org/downloads
   - [Firefox driver] https://github.com/mozilla/geckodriver/releases
3. Having Python > 3.6


### Aditional resources

[Selenuim] https://www.selenium.dev/  
[PyQuery] https://pyquery.readthedocs.io/en/latest/api.html  
[CSS selectors] https://www.w3schools.com/cssref/css_selectors.asp  
[XPath] https://www.w3schools.com/xml/xpath_intro.asp