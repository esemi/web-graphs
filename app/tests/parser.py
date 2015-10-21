# -*- coding: utf-8 -*-

import unittest

from app.parser import Parser
from app.components.storage import Storage


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.p = Parser(None)

    def test_links_compact(self):
        data = [
            (['http://ya.ru', 'https://ya.ru'], ['ya.ru'], ''),
            (['http://www.ya.ru', 'https://ololo.ya.ru'], ['ya.ru'], ''),
            (['http://www.ya.ru', 'https://ololo.ya.com'], ['ya.com', 'ya.ru'], ''),
            (['http://www.ya.ru', 'https://ololo.ya.com'], ['ya.com'], 'ya.ru'),
        ]

        for links, success, ignore_domain in data:
            res = self.p._links_domain_filter(links, ignore_domain)
            self.assertEqual(success, res)

if __name__ == '__main__':
    unittest.main()
