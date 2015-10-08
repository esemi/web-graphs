#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time

import tornado.gen
from tornado.log import app_log
from tornado.options import define, options, parse_command_line

from components.storage import Storage
from components.queue import Q

define("crawler_sleep_period_sec", default=10, type=int)


@tornado.gen.coroutine
def crawler_process():
    app_log.info('start crawler process')
    db = Storage()
    q = Q()

    while True:
        task = q.get_crawler_task()
        if not task:
            app_log.info("not found task")
            time.sleep(options.crawler_sleep_period_sec)
            continue

        # todo crawling and save results
        print task

        q.complete_crawler_task(task[0])

    app_log.info('end crawler process')


if __name__ == '__main__':
    parse_command_line()
    ioloop = tornado.ioloop.IOLoop()
    ioloop.make_current()
    ioloop.run_sync(crawler_process)
