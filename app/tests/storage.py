# -*- coding: utf-8 -*-

import os
import unittest
from codecs import open

from app.components.storage import Storage, SOURCE_STORAGE_PATH, DATA_STORAGE_PATH, DATA_STORAGE_SEPARATOR


class StorageTest(unittest.TestCase):
    def setUp(self):
        self.s = Storage()

    def test_save_crawling_result(self):
        data = [
            ('1', 'atata.com', 'undefined error', 'http://sdsdsd.com', '<html>sdsd <b>sdsd</b></html>'),
            (1, 'atata.com', 'undefined error', 'http://sdsdsd.com', '<html>sdsd <b>sdsd</b></html>'),
        ]

        for domain_id, domain_name, error, effective_url, body in data:
            f_data = os.path.join(DATA_STORAGE_PATH, '%s.data' % domain_id)
            f_source = os.path.join(SOURCE_STORAGE_PATH, '%s.html' % domain_id)

            res = self.s.save_crawling_result(domain_id, domain_name, error, effective_url, body)

            self.assertEqual(res, (f_data, f_source))

            self.assertTrue(os.path.exists(SOURCE_STORAGE_PATH))
            self.assertTrue(os.path.exists(DATA_STORAGE_PATH))

            self.assertTrue(os.path.exists(f_data))
            self.assertTrue(os.path.exists(f_source))

            with open(f_data, encoding='utf-8') as f:
                data = f.read().split(DATA_STORAGE_SEPARATOR)
                self.assertEqual([unicode(domain_id), unicode(domain_name), unicode(error), unicode(effective_url)],
                                 data)
            with open(f_source, encoding='utf-8') as f:
                source = f.read()
                self.assertEqual(body, source)

if __name__ == '__main__':
    unittest.main()
