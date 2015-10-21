#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from codecs import open

import tornado.gen
from tornado.log import app_log

from app.components.storage import Storage
from app.components.tld_extractor import Extractor


@tornado.gen.coroutine
def main():
    app_log.info('start domains init process')
    s = Storage()
    ext = Extractor()

    with open(os.path.join(os.path.dirname(__file__), 'domains_init.csv'), mode='r', encoding='utf-8') as f:
        domain_rows = f.read().split("\n")

    for row in domain_rows:
        try:
            _, domain = row.split(',')
        except ValueError:
            print 'not found domain'
            continue

        domain_filtered = ext.extract('http://%s' % domain)
        if not domain_filtered:
            print 'not parsed domain'
            continue

        try:
            yield s.add_domain(domain_filtered)
            print 'add domain'
        except Exception as e:
            print e, 'not add'
            pass

    app_log.info('end domains init process')


if __name__ == '__main__':
    ioloop = tornado.ioloop.IOLoop()
    ioloop.make_current()
    ioloop.run_sync(main)
