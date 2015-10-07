# -*- coding: utf-8 -*-

import tornado.gen

from tornado_mysql import pools, connect


class Storage:
    def __init__(self):
        self.db_pool = pools.Pool(
            dict(host='127.0.0.1', port=3306, user='root', passwd='root', db='web_graph', use_unicode=True, autocommit=True),
            max_idle_connections=1,
            max_recycle_sec=30)

    @tornado.gen.coroutine
    def add_domain(self, domain_full, tld):
        conn = yield connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='web_graph',
                             use_unicode=True, autocommit=True)
        cur = conn.cursor()
        yield cur.execute(u"INSERT INTO `domain` (`domain_full`, `tld`, `date_add`) VALUES (%s, %s, CURRENT_DATE)",
                          (domain_full, tld))
        raise tornado.gen.Return(cur.fetchall())

