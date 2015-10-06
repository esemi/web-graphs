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
        root_domain = self.application.tld_extractor.extract(query)

        if not root_domain:
            res = {'result': 'fail', 'message': 'not valid domain'}
        else:
            request_id = yield self.application.db.add_request(query, root_domain)
            app_log.info("add request %s (%s) with id %s" % (root_domain, query, request_id))
            res = {'url':  self.reverse_url('search-result', request_id)}
            try:
                yield self.application.db.add_graph_domain(root_domain)
                app_log.info("force parse domain %s success" % root_domain)
            except pymongo.errors.DuplicateKeyError:
                app_log.info("force parse domain %s already parced" % root_domain)

            domain = yield self.application.db.find_domain(root_domain)
            app_log.info("find domain data by %s (%s)" % (root_domain, domain))

            if domain['crawling_status'] in (models.CRAWLING_WAIT_STATUS, models.CRAWLING_PROCESS_STATUS):
                res['result'] = 'wait'
            else:
                if domain['crawling_status'] == models.CRAWLING_FAIL_STATUS:
                    res['result'] = 'error'
                    res['error'] = domain['crawling_error']
                else:
                    res['result'] = 'success'
                    res['relations'] = domain['relations']

        self.write(res)