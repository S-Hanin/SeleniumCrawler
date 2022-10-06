# -*- coding: utf8 -*-

class Task:
    def __init__(self, name):
        self.name = name

    def add_url(self, val, new_tab=False):
        self.__dict__["_url"] = val
        self.__dict__["_new_tab"] = new_tab
        return self

    def add_sleep(self, val):
        self.__dict__["_sleep"] = val
        return self

    def add_xpath(self, val):
        self.__dict__["_xpath"] = val
        return self

    def add_css(self, val):
        self.__dict__["_css"] = val
        return self

    def add_wait(self, val):
        self.__dict__["_wait"] = val
        return self

    def add_param(self, name, val):
        self.__dict__[name] = val
        return self

    @property
    def url(self):
        return self.__dict__.get("_url")

    @property
    def sleep(self):
        return self.__dict__.get("_sleep", 0)

    @property
    def xpath(self):
        return self.__dict__.get("_xpath")

    @property
    def css(self):
        return self.__dict__.get("_css")

    @property
    def wait(self):
        return self.__dict__.get("_wait")
