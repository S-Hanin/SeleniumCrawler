# -*- coding: utf8 -*-

class Task:
    def __init__(self, name):
        self.name = name

    def add_url(self, val):
        self.__dict__.setdefault("_url", val)
        return self

    def add_sleep(self, val):
        self.__dict__.setdefault("_sleep", val)
        return self

    def add_xpath(self, val):
        self.__dict__.setdefault("_xpath", val)
        return self

    def add_css(self, val):
        self.__dict__.setdefault("_css", val)
        return self

    def add_wait(self, val):
        self.__dict__.setdefault("_wait", val)
        return self

    def add_param(self, name, val):
        self.__dict__.setdefault(name, val)
        return self

    @property
    def url(self):
        return self.__dict__["_url"]

    @property
    def sleep(self):
        return self.__dict__["_sleep"]

    @property
    def xpath(self):
        return self.__dict__["_xpath"]

    @property
    def css(self):
        return self.__dict__["_css"]

    @property
    def wait(self):
        return self.__dict__["_wait"]
