#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging

import lxml.html
import lxml.etree
import tornado.gen
import tornado.httpclient
from tornado.options import define, options, parse_command_line

from components.storage import Storage
from components.queue import Q
from components.utils import app_log_process, return_by_raise, log_fds, log_mem
from components.tld_extractor import Extractor


define("parser_sleep_period_sec", default=10, type=int)
define("debug", default=False, help="enable debug mode", type=bool)


RESULT_ERROR = 'FAIL'
RESULT_FULL_REDIRECT = 'FULL_REDIR'
RESULT_LINKS = 'LINKS'


class Parser(object):
    def __init__(self, s):
        self.storage = s
        self.e = Extractor()

    def _links_domain_filter(self, links, ignore_domain_name=None):
        domains = list(set([self.e.extract(i) for i in links]))
        return filter(lambda x: x is not None and x != ignore_domain_name, domains)

    @staticmethod
    def create_html_doc(source):
        return lxml.html.fromstring(source)

    def parse_result(self, domain_name, error, effective_url, source):
        if error:
            app_log_process('parse unknown error %s' % error, logging.DEBUG)
            return RESULT_ERROR, error

        final_domain = self.e.extract(unicode(effective_url))
        if not final_domain:
            app_log_process('parse redirect error %s' % effective_url, logging.DEBUG)
            return RESULT_ERROR, 'invalid redirect to %s' % effective_url

        if final_domain != domain_name:
            app_log_process('parse full redirect %s -> %s' % (domain_name, final_domain), logging.DEBUG)
            return RESULT_FULL_REDIRECT, final_domain

        s = source.lower().strip().encode('utf-8')
        if not s:
            app_log_process('parse empty source error %d' % len(s), logging.DEBUG)
            return RESULT_ERROR, 'empty source %s' % len(s)

        try:
            document = self.create_html_doc(s)
        except lxml.etree.ParserError as e:
            app_log_process('parser error %s' % e, logging.WARNING)
            return RESULT_ERROR, 'error parser %s' % e

        # a href
        href_links = self._links_domain_filter(document.xpath('//a/@href'), domain_name)
        app_log_process('found a@href links %d (%s)' % (len(href_links), ','.join(href_links)), logging.DEBUG)

        # # script src js
        # script_links = self._links_domain_filter(document.xpath('//script/@src'))
        # app_log_process('found script@src links %d (%s)' % (len(script_links), ','.join(script_links)), logging.DEBUG)
        #
        # # link href css
        # link_links = self._links_domain_filter(document.xpath('//link[contains(@rel, "stylesheet")]/@href'))
        # app_log_process('found link@href links %d (%s)' % (len(link_links), ','.join(link_links)), logging.DEBUG)
        #
        # # img src
        # img_links = self._links_domain_filter(document.xpath('//img/@src'))
        # app_log_process('found img@src links %d (%s)' % (len(img_links), ','.join(img_links)), logging.DEBUG)

        return RESULT_LINKS, href_links

    @tornado.gen.coroutine
    def run(self, domain_id):
        app_log_process('start parsing %s domain_id' % domain_id)

        crawling_result = None
        try:
            crawling_result = self.storage.get_crawling_result(domain_id)
            app_log_process('found response %s %s' % (crawling_result[0], crawling_result[1]))
        except IOError:
            app_log_process('skip by not found sources')
            return_by_raise()

        domain_name, error, effective_url, source = crawling_result

        parsing_result = self.parse_result(domain_name, error, effective_url, source)
        app_log_process('parsed result %s' % parsing_result[0])

        if parsing_result[0] == RESULT_ERROR:
            yield self.storage.update_by_parser(domain_id, False)
            yield self.storage.clear_relations_from(domain_id)

        elif parsing_result[0] == RESULT_FULL_REDIRECT:
            new_domain_id = yield self.storage.add_domain_custom(parsing_result[1])
            yield self.storage.update_by_parser(domain_id, True)
            yield self.storage.clear_relations_from(domain_id)
            yield self.storage.add_relations([(domain_id, new_domain_id)])

        elif parsing_result[0] == RESULT_LINKS:
            yield self.storage.update_by_parser(domain_id, True)
            relations = []
            for link in parsing_result[1]:
                new_domain_id = yield self.storage.add_domain_custom(link)
                relations.append((domain_id, new_domain_id))
            yield self.storage.clear_relations_from(domain_id)
            yield self.storage.add_relations(relations)
        else:
            raise RuntimeError('Unknown parsing result type %s' % parsing_result[0])

        self.storage.clear_crawling_result(domain_id)
        app_log_process('end parsing process')


@tornado.gen.coroutine
def parser_process():
    app_log_process('start parser process')
    log_fds('start')
    log_mem('start')
    q = Q()
    s = Storage()
    parser = Parser(s)

    while True:
        log_fds('start loop')
        log_mem('start loop')
        task = q.get_parser_task()
        if task:
            yield parser.run(task[2])
            q.complete_task(task[0])
        else:
            app_log_process("not found task")
            time.sleep(options.parser_sleep_period_sec)

    app_log_process('end parser process')


if __name__ == '__main__':
    parse_command_line()

    if options.debug:
        from tornado.log import app_log
        app_log.setLevel(logging.DEBUG)

    ioloop = tornado.ioloop.IOLoop()
    ioloop.make_current()
    ioloop.run_sync(parser_process)
