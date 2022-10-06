# -*- coding: utf8 -*-
import typing
from collections import deque
from typing import Deque


class ProvidersChain:
    def __init__(self, initial_provider):
        self.__stack: Deque[typing.Generator] = deque()
        self.__stack.append(initial_provider)
        self.__next = None

    def has_next(self):
        return bool(self.__stack) or bool(self.__next)

    def get_next_task(self):
        try:
            provider = self.__stack.pop()
            task = self.__next or next(provider)
            self.__next = next(provider, None)
            if self.__next:
                self.__stack.append(provider)
            return task
        except IndexError as ex:
            pass

    def add_provider(self, provider: typing.Generator):
        self.__stack.append(provider)

    def items(self) -> typing.Iterable:
        while self.has_next():
            yield self.get_next_task()
