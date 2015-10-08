# -*- coding: utf-8 -*-

import tornado.gen
from tornado_mysql import connect


class Storage:
    def __init__(self):
        self.__conn = None

    @property
    @tornado.gen.coroutine
    def cursor(self):
        if not self.__conn:
            self.__conn = yield connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='web_graph',
                                        use_unicode=True, autocommit=True)
        raise tornado.gen.Return(self.__conn.cursor())

    @tornado.gen.coroutine
    def add_domain(self, domain_full, tld):
        cur = yield self.cursor
        yield cur.execute(u"INSERT INTO `domain` (`domain_full`, `tld`, `date_add`) VALUES (%s, %s, CURRENT_DATE)",
                          (domain_full, tld))
        raise tornado.gen.Return(cur.lastrowid)

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

        ids = map(lambda x: str(x[0]), domains)
        yield cur.execute(u"UPDATE `domain` SET last_update_date = NOW() WHERE id IN (%s)" % ','.join(ids))

        raise tornado.gen.Return(domains)
