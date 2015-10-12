# -*- coding: utf-8 -*-

import unittest

from app.components.tld_extractor import Extractor


class ExtractorTest(unittest.TestCase):
    _parser = None

    def setUp(self):
        self._parser = Extractor()

    def test_tld_parse(self):
        urls = [
            (u'', None),
            (u'/sdsdsd/sdsd?', None),
            (u'sdasdasdasdasdas dasd asdas dasd asd', None),
            (u'yandex.uuuuururu', None),
            (u'yandex.ru.sussss.commm', None),
            (u'127.0.0.1', None),
            (u'test', None),
            (u'test.test', None),
            (u'качай.рф', u'качай.рф'),
            (u'ёёё.качай.рф', u'качай.рф'),
            (u'www.yandex.ru', u'yandex.ru'),
            (u'yandex.co.uk:8080', u'yandex.co.uk'),
            (u'YANdex.co.UK', u'yandex.co.uk'),
            (u'blogspot.com.ar', u'blogspot.com.ar'),
            (u'www.blogspot.com.ar', u'blogspot.com.ar'),
            (u'ololo.blogspot.com.ar', u'blogspot.com.ar'),
            (u'ddd.ololo.blogspot.com.ar', u'blogspot.com.ar'),
        ]

        for url, success in urls:
            # simple case - always None (schema not exist)
            res = self._parser.extract(url)
            self.assertEqual(res, None)

            # + http:// case
            res = self._parser.extract(u'http://%s' % url)
            self.assertEqual(res, success)

            # + // case
            res = self._parser.extract(u'//%s' % url)
            self.assertEqual(res, success)

            # + https:// case
            res = self._parser.extract(u'https://%s' % url)
            self.assertEqual(res, success)

            # + http:// and query string case
            res = self._parser.extract(u'http://%s/?q=dssds&s=ebay.com' % url)
            self.assertEqual(res, success)

if __name__ == '__main__':
    unittest.main()
