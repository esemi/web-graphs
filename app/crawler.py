#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
import multiprocessing as mp
import logging

import yieldpoints
import tornado.gen
import tornado.httpclient
from tornado.log import app_log
from tornado.options import define, options, parse_command_line

from components.storage import Storage
from components.queue import Q


define("crawler_sleep_period_sec", default=10, type=int)
define("crawler_curl_conn", default=500, help="number of curl connections", type=int)
define("crawler_curl_timeout", default=25, help="curl timeout", type=int)
define("crawler_curl_max_redirects", default=5, help="curl max redirects", type=int)


PROCESS_NAME = '%d-%s' % (mp.current_process().pid, mp.current_process().name)


def app_log_process(message, level=logging.INFO):
    app_log.log(level, '(%s) %s' % (PROCESS_NAME, message))


def return_by_raise(val=None):
    raise tornado.gen.Return(val)


class Crawler(object):
    def __init__(self, domains):
        self.storage = Storage()
        self.q = Q()
        self.domains = domains

    @staticmethod
    def handle_response(domain, response):
        app_log_process('handle response %s' % domain)

        error = None
        effective_url = unicode(response.effective_url)
        body = response.body

        if response.error:
            error = unicode(response.error)

        return error, effective_url, body

    @tornado.gen.coroutine
    def run(self):
        # todo check c-ares enable
        num_conn = min(len(self.domains), options.crawler_curl_conn)
        app_log_process('start crawling process %d domains, %d conn, %d timeout' % (len(self.domains), num_conn,
                                                                                    options.crawler_curl_timeout))
        tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                                     max_clients=num_conn)
        http_client = tornado.httpclient.AsyncHTTPClient()

        keys = set()
        for i, url in enumerate(self.domains):
            request = tornado.httpclient.HTTPRequest(url, connect_timeout=options.crawler_curl_timeout,
                                                     request_timeout=options.crawler_curl_timeout,
                                                     follow_redirects=True,
                                                     max_redirects=options.crawler_curl_max_redirects)
            http_client.fetch(request, callback=(yield tornado.gen.Callback(i)))
            keys.add(i)

        while keys:
            key, response = yield yieldpoints.WaitAny(keys)
            domain = self.domains[key]
            error, effective_url, body = self.handle_response(self.domains[key], response)
            keys.remove(key)
            self.storage.save_crawling_result(domain[0], domain[1], error, effective_url, body)
            self.q.add_parser_task(domain[0])

        app_log_process('end crawling process')


@tornado.gen.coroutine
def crawler_process():
    app_log_process('start crawler process')
    q = Q()

    while True:
        task = q.get_crawler_task()
        if not task:
            app_log_process("not found task")
            time.sleep(options.crawler_sleep_period_sec)
            continue

        crawler = Crawler(task[2])
        yield crawler.run()

        q.complete_crawler_task(task[0])

    app_log_process('end crawler process')


if __name__ == '__main__':
    parse_command_line()
    ioloop = tornado.ioloop.IOLoop()
    ioloop.make_current()
    ioloop.run_sync(crawler_process)
