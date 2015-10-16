# -*- coding: utf-8 -*-

import os
from codecs import open

import tornado.gen
from tornado_mysql import connect

from utils import to_unicode

SOURCE_STORAGE_PATH = '/tmp/webgraph/crawler_source/'
DATA_STORAGE_PATH = '/tmp/webgraph/crawler_data/'
DATA_STORAGE_SEPARATOR = u"\n<=====================>\n"


class Storage:
    def __init__(self):
        self.__conn = None
        try:
            os.makedirs(DATA_STORAGE_PATH)
        except OSError:
            pass
        try:
            os.makedirs(SOURCE_STORAGE_PATH)
        except OSError:
            pass

    @property
    @tornado.gen.coroutine
    def cursor(self):
        if not self.__conn:
            self.__conn = yield connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='web_graph',
                                        use_unicode=True, autocommit=True, charset='utf8')
        raise tornado.gen.Return(self.__conn.cursor())

    @tornado.gen.coroutine
    def add_domain(self, domain_full):
        cur = yield self.cursor
        yield cur.execute(u"INSERT INTO `domain` (`domain_full`, `date_add`) VALUES (%s, CURRENT_DATE)", (domain_full))
        raise tornado.gen.Return(cur.lastrowid)

    @tornado.gen.coroutine
    def add_domain_custom(self, domain_full):
        new_domain_id = yield self.get_domain_by_name(domain_full)
        if not new_domain_id:
            try:
                new_domain_id = yield self.add_domain(domain_full)
            except:
                new_domain_id = yield self.get_domain_by_name(domain_full)
        raise tornado.gen.Return(new_domain_id)

    @tornado.gen.coroutine
    def clear_relations_from(self, domain_id):
        cur = yield self.cursor
        yield cur.execute(u"DELETE FROM `relations` WHERE from_domain_id = %s", (domain_id))

    @tornado.gen.coroutine
    def add_relations_from(self, relations_list):
        cur = yield self.cursor
        yield cur.executemany(u"INSERT INTO `relations` (`from_domain_id`, `to_domain_id`) VALUES (%s, %s) "
                              u"ON DUPLICATE KEY UPDATE from_domain_id=from_domain_id", relations_list)

    @tornado.gen.coroutine
    def get_domain_by_name(self, domain_full):
        cur = yield self.cursor
        yield cur.execute(u"SELECT id FROM `domain` WHERE `domain_full` = %s", (domain_full))
        res = cur.fetchone()
        if res:
            raise tornado.gen.Return(res[0])
        else:
            raise tornado.gen.Return(None)

    @tornado.gen.coroutine
    def update_by_parser(self, domain_id, is_success):
        cur = yield self.cursor
        yield cur.execute(u"UPDATE `domain` SET last_update_date = NOW(), last_update_state = %s WHERE id = %s LIMIT 1",
                          ('success' if is_success else 'error', domain_id))

    @tornado.gen.coroutine
    def fetch_domains_for_update(self, limit):
        cur = yield self.cursor
        yield cur.execute(u"""SELECT id, domain_full FROM `domain`
            WHERE last_update_date IS NULL OR last_update_date <= NOW() - INTERVAL 1 MONTH
            ORDER BY last_update_date
            LIMIT %s
        """, limit)
        domains = cur.fetchall()
        if not domains:
            raise tornado.gen.Return(None)

        raise tornado.gen.Return(domains)

    @tornado.gen.coroutine
    def update_domains_after_fetch(self, domains):
        ids = map(lambda x: str(x[0]), domains)
        cur = yield self.cursor
        yield cur.execute(u"UPDATE `domain` SET last_update_date = NOW() WHERE id IN (%s)" % ','.join(ids))

    @staticmethod
    def get_source_fname(domain_id):
        return os.path.join(SOURCE_STORAGE_PATH, '%s.html' % domain_id)

    @staticmethod
    def get_data_fname(domain_id):
        return os.path.join(DATA_STORAGE_PATH, '%s.data' % domain_id)

    def save_crawling_result(self, domain_id, domain_name, error, effective_url, body):
        with open(self.get_data_fname(domain_id), mode='w', encoding='utf-8') as f:
            f.write(DATA_STORAGE_SEPARATOR.join([domain_id, domain_name, error, to_unicode(effective_url)]))
        with open(self.get_source_fname(domain_id), mode='w', encoding='utf-8') as f:
            f.write(body)

    def clear_crawling_result(self, domain_id):
        try:
            os.remove(self.get_data_fname(domain_id))
        except OSError:
            pass
        try:
            os.remove(self.get_source_fname(domain_id))
        except OSError:
            pass

    def get_crawling_result(self, domain_id):
        with open(self.get_data_fname(domain_id), mode='r', encoding='utf-8') as f:
            data = f.read()
            domain_id, domain_name, error, effective_url = data.split(DATA_STORAGE_SEPARATOR)
        with open(self.get_source_fname(domain_id), mode='r', encoding='utf-8') as f:
            body = f.read()

        return domain_name, error, effective_url, body

