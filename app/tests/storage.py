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
            ('0', 'atata.com', 'error message', 'http://sdsdsd.com', '<html>sdsd <b>sdsd</b></html>'),
            ('0', '', '', '', ''),
            ('0', 'atata.com', 'error message', 'http://sdsdsd.com', u'<html>sdsd атата<b>sdsd</b></html>'),
        ]

        for domain_id, domain_name, error, effective_url, body in data:
            f_data = os.path.join(DATA_STORAGE_PATH, '%s.data' % domain_id)
            f_source = os.path.join(SOURCE_STORAGE_PATH, '%s.html' % domain_id)

            self.s.save_crawling_result(domain_id, domain_name, error, effective_url, body)

            self.assertTrue(os.path.exists(SOURCE_STORAGE_PATH))
            self.assertTrue(os.path.exists(DATA_STORAGE_PATH))

            self.assertTrue(os.path.exists(f_data))
            self.assertTrue(os.path.exists(f_source))

            res_valid = self.s.get_crawling_result(domain_id)
            self.assertEqual((domain_name, error, effective_url, body), res_valid)

    def test_get_crawling_result(self):
        with self.assertRaises(IOError):
            res_not_found = self.s.get_crawling_result(-1)

        res_valid = self.s.get_crawling_result(0)
        self.assertEqual(4, len(res_valid))


if __name__ == '__main__':
    unittest.main()
