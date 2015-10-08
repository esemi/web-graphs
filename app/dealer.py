#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time

import tornado.gen
from tornado.log import app_log
from tornado.options import define, options, parse_command_line

from components.storage import Storage
from components.queue import Q


define("dealer_work_period_minutes", default=5, type=int)
define("dealer_domains_per_task", default=10, type=int)


@tornado.gen.coroutine
def dealer_process():
    app_log.info('start dealer process')
    db = Storage()
    q = Q()

    while True:
        domains = yield db.fetch_domains_for_update(options.dealer_domains_per_task)
        if domains:
            app_log.info("fetch %d domains for new task" % len(domains))
            res = q.add_crawler_task(domains)
            app_log.info("add crawler task %s" % res)
            del domains
        else:
            app_log.info("not found domains")

        time.sleep(options.dealer_work_period_minutes * 60)

    app_log.info('end dealer process')


if __name__ == '__main__':
    parse_command_line()
    ioloop = tornado.ioloop.IOLoop()
    ioloop.make_current()
    ioloop.run_sync(dealer_process)
