# -*- coding: utf8 -*-
from unittest import TestCase

from spider.providers import ProvidersChain


class TestProvidersChain(TestCase):

    def test_has_next(self):
        gen = (it for it in 'a')
        chain = ProvidersChain(gen)
        self.assertTrue(chain.has_next())

        chain.get_next_task()
        self.assertFalse(chain.has_next())

    def test_get_next_task(self):
        gen = (it for it in 'ab')
        chain = ProvidersChain(gen)

        task = chain.get_next_task()
        self.assertEqual(task, 'a')

        task = chain.get_next_task()
        self.assertEqual(task, 'b')

        task = chain.get_next_task()
        self.assertIsNone(task)

    def test_add_provider(self):
        gen1 = (it for it in 'a')
        gen2 = (it for it in 'b')

        chain = ProvidersChain(gen1)
        task = chain.get_next_task()
        self.assertEqual(task, 'a')

        chain.add_provider(gen2)
        task = chain.get_next_task()
        self.assertEqual(task, 'b')

    def test_items(self):
        gen1 = (it for it in 'a')
        gen2 = (it for it in 'b')

        chain = ProvidersChain(gen1)
        chain.add_provider(gen2)

        result = []
        for it in chain.items():
            result.append(it)

        self.assertListEqual(result, ['b', 'a'])
