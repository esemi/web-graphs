# -*- coding: utf-8 -*-

import os
import urlparse

import tldextract


class Extractor:
    def __init__(self):
        input_path = 'file://%s' % os.path.join(os.path.dirname(__file__), '../data', 'publicsuffix.txt')
        self._extractor = tldextract.TLDExtract(suffix_list_url=input_path)

    def extract(self, source_url):
        url = source_url.strip().lower()

        # TODO valid parse punycode ? example: xn--61aaa.xn--80aa1ab0e.xn--p1ai

        try:
            hostname = urlparse.urlparse(url).hostname
        except (AttributeError, IndexError):
            return None

        if not hostname:
            return None

        res = self._extractor(hostname)

        if not res.suffix or not res.domain:
            return None

        return '%s.%s' % (res.domain, res.suffix)