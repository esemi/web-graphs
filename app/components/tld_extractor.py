# -*- coding: utf-8 -*-

import os
import urlparse

import tldextract
from utils import to_unicode


class Extractor:
    def __init__(self):
        input_path = 'file://%s' % os.path.join(os.path.dirname(__file__), '../data', 'publicsuffix.dat')
        self._extractor = tldextract.TLDExtract(suffix_list_url=input_path, include_psl_private_domains=False)

    def extract(self, source_url):
        url = to_unicode(source_url).strip().lower()

        try:
            hostname = urlparse.urlparse(url).hostname
        except (AttributeError, IndexError, ValueError):
            return None

        if not hostname:
            return None
        res = self._extractor(hostname)

        if not res.suffix or not res.domain:
            return None

        out = u'%s.%s' % (res.domain, res.suffix)
        return out
