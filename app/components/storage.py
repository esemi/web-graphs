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

