# -*- coding: utf-8 -*-

import os
import urlparse

import tldextract


class Extractor:
    def __init__(self):
        input_path = 'file://%s' % os.path.join(os.path.dirname(__file__), '../data', 'publicsuffix.dat')
        self._extractor = tldextract.TLDExtract(suffix_list_url=input_path, include_psl_private_domains=True)

    def extract(self, source_url):
        url = source_url.strip().lower()

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
