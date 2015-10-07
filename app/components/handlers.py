# -*- coding: utf-8 -*-

from tornado.log import app_log
import tornado.web
import tornado.gen


class BaseHandler(tornado.web.RequestHandler):
    pass


class MainHandler(BaseHandler):
    @tornado.web.addslash
    def get(self):
        self.render("index.html")


class DomainPublicHandler(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        """Try adding new domain to index"""
        query = 'http://%s' % self.get_argument('domain')
        extract = self.application.tld_extractor.extract(query)
        app_log.info("request add domain %s (%s)" % (query, extract))

        if not extract:
            res = {'result': 'fail', 'message': 'not valid domain'}
        else:
            try:
                yield self.application.storage.add_domain(extract[0], extract[1])
            except Exception as e:
                app_log.info("add domain fail (%s)" % e)
                res = {'result': 'fail', 'message': str(e)}
            else:
                res = {'result': 'success', 'message': extract[0]}
        self.write(res)
