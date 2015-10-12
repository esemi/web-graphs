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
            res = {'success': False, 'message': 'not valid domain'}
        else:
            try:
                yield self.application.storage.add_domain(extract)
            except Exception as e:
                res = {'success': False, 'message': str(e)}
            else:
                res = {'success': True, 'message': extract}

        app_log.info("response add domain %s" % res)
        self.write(res)
