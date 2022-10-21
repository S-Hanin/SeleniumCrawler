# -*- coding: utf8 -*-
import gc
import typing
from collections import deque
from typing import Deque


class ProvidersChain:
    def __init__(self, initial_provider):
        self.__stack: Deque[typing.Generator] = deque()
        self.__stack.append(initial_provider)

    def has_next(self):
        return bool(self.__stack)

    def get_next_task(self):
        try:
            provider = self.__stack.pop()
            if task := next(provider, None):
                self.__stack.append(provider)
            else:
                gc.collect()
            return task
        except IndexError as ex:
            pass

    def add_provider(self, provider: typing.Generator):
        self.__stack.append(provider)

    def items(self) -> typing.Iterable:
        while self.has_next():
            yield self.get_next_task()
