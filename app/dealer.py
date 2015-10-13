#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging

import tornado.gen
from tornado.log import app_log
from tornado.options import define, options, parse_command_line

from components.storage import Storage
from components.queue import Q
from components.utils import log_mem, log_fds


define("debug", default=False, help="enable debug mode", type=bool)
define("dealer_sleep_period_sec", default=15, type=int)
define("dealer_fetch_task_sleep_period_sec", default=10, type=int)
define("dealer_domains_per_task", default=3000, type=int)


@tornado.gen.coroutine
def dealer_process():
    app_log.info('start dealer process')
    log_fds('start')
    log_mem('start')
    s = Storage()
    q = Q()

    while True:
        log_fds('start loop')
        log_mem('start loop')
        domains = yield s.fetch_domains_for_update(options.dealer_domains_per_task)
        if domains and len(domains) < options.dealer_domains_per_task:
            time.sleep(options.dealer_fetch_task_sleep_period_sec)
            domains = yield s.fetch_domains_for_update(options.dealer_domains_per_task)

        if not domains:
            app_log.info("not found domains")
            time.sleep(options.dealer_sleep_period_sec)
            continue

        app_log.info("fetch %d domains for new task" % len(domains))
        res = q.add_crawler_task(domains)
        yield s.update_domains_after_fetch(domains)
        app_log.info("add task %s" % res)
        del domains

    app_log.info('end dealer process')


if __name__ == '__main__':
    parse_command_line()

    if options.debug:
        from tornado.log import app_log
        app_log.setLevel(logging.DEBUG)

    ioloop = tornado.ioloop.IOLoop()
    ioloop.make_current()
    ioloop.run_sync(dealer_process)
