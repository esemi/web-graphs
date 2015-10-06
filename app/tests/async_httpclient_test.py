#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'esemi'

import logging
import timeit
import pycurl
from collections import deque
import cStringIO

import yieldpoints
from tornado.httpclient import AsyncHTTPClient
import tornado.ioloop
import tornado.gen


NUM_URLS = 10000
NUM_CONN = 500
URL = "http://google.ru/"
CURL_TIMEOUT = 10
NUM_TEST_TRY = 1


def multi_get(urls, num_conn, timeout, err_callback, succ_callback):
    queue = deque(urls)
    if not queue:
        return

    num_urls = len(queue)
    num_conn = min(num_conn, num_urls)

    assert 1 <= num_conn <= 10000, "invalid number of concurrent connections"

    logging.debug("PycURL %s (compiled against 0x%x)" % (pycurl.version, pycurl.COMPILE_LIBCURL_VERSION_NUM))
    logging.debug("call curl multi %d %d" % (num_urls, num_conn))

    m = pycurl.CurlMulti()
    m.handles = []
    for i in xrange(num_conn):
        c = pycurl.Curl()
        c.fp = None
        c.setopt(pycurl.CONNECTTIMEOUT, timeout)
        c.setopt(pycurl.TIMEOUT, timeout)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 5)
        c.setopt(pycurl.NOSIGNAL, 1)
        c.setopt(pycurl.FAILONERROR, 1)

        m.handles.append(c)

    freelist = m.handles[:]
    num_processed = 0
    bailout = 0
    while num_processed < num_urls:
        if bailout:
            break

        while queue and freelist:
            c = freelist.pop()
            c.domain = queue.pop()
            if type(c.domain) == type(u''):
                c.domain = c.domain.encode('utf8', 'replace')

            c.setopt(pycurl.URL, c.domain)

            c.source = cStringIO.StringIO()
            c.header = cStringIO.StringIO()

            c.setopt(pycurl.HEADERFUNCTION, c.header.write)
            c.setopt(pycurl.WRITEFUNCTION, c.source.write)

            m.add_handle(c)

        while 1:
            ret, num_handles = m.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break

        while 1:
            num_q, ok_list, err_list = m.info_read()

            for c in ok_list:
                c.fp = None
                m.remove_handle(c)
                logging.debug("[ ok] %s" % c.domain)
                succ_callback(
                    c.domain,
                    unicode(c.header.getvalue(), errors='ignore'),
                    unicode(c.source.getvalue(), errors='ignore'))
                freelist.append(c)

            for c, errno, errmsg in err_list:
                c.fp = None
                m.remove_handle(c)
                logging.debug("[err] %s %s" % (c.domain, errmsg))
                err_callback(
                    c.domain,
                    errno,
                    errmsg)
                freelist.append(c)

            num_processed = num_processed + len(ok_list) + len(err_list)

            if num_processed >= num_urls:
                bailout = 1
                break

            if num_q == 0:
                break

        m.select(1.0)
    m.close()


def handle_request(*args):
    # logging.info('handle %s' % response.code)
    pass


def test_tornado():

    @tornado.gen.coroutine
    def _tornado_crawler():
        logging.info('start %d %d %s %d' % (NUM_URLS, NUM_CONN, URL, CURL_TIMEOUT))

        tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=NUM_CONN)
        http_client = tornado.httpclient.AsyncHTTPClient(io_loop=tornado.ioloop.IOLoop.instance())
        request = tornado.httpclient.HTTPRequest(URL, connect_timeout=CURL_TIMEOUT, request_timeout=CURL_TIMEOUT,
                                                 follow_redirects=True, max_redirects=5)
        keys = set(range(NUM_URLS))
        for i in keys:
            http_client.fetch(request, callback=(yield tornado.gen.Callback(i)))
        while keys:
            key, res = yield yieldpoints.WaitAny(keys)
            handle_request(res)
            keys.remove(key)

        logging.info('end')

    tornado.ioloop.IOLoop.current().run_sync(_tornado_crawler)


def test_curl_multi():
    urls = [URL for i in xrange(NUM_URLS)]
    logging.info('start %d %d %s %d' % (len(urls), NUM_CONN, URL, CURL_TIMEOUT))
    multi_get(
        urls,
        NUM_CONN,
        CURL_TIMEOUT,
        handle_request,
        handle_request
    )
    logging.info('end')

if __name__ == '__main__':

    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        level=logging.INFO)

    par = timeit.timeit('test_tornado()', 'from __main__ import test_tornado', number=NUM_TEST_TRY) / NUM_TEST_TRY
    logging.info('tornado test %.2f sec (%d urls/sec)' % (par, NUM_URLS / par))

    bar = timeit.timeit('test_curl_multi()', 'from __main__ import test_curl_multi', number=NUM_TEST_TRY) / NUM_TEST_TRY
    logging.info('curl multi test %.2f sec (%d urls/sec)' % (bar, NUM_URLS / bar))




