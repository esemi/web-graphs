#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.escape
import tornado.httpserver
from tornado.options import define, options, parse_command_line

from components import uimodules, tld_extractor
from components.handlers import MainHandler, DomainPublicHandler


define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="enable debug mode", type=bool)
define("cookie_secret", help="set u cookie secret value into config.py", type=str)


class Application(tornado.web.Application):
    def __init__(self):
        self.tld_extractor = tld_extractor.Extractor()

        handlers = [
            (r"/?", MainHandler),
            (r"/domain/public", DomainPublicHandler)
        ]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules=uimodules,
            debug=options.debug
        )

        super(Application, self).__init__(handlers, **settings)


if __name__ == "__main__":
    parse_command_line()
    app = Application()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.bind(options.port)
    http_server.start()

    tornado.ioloop.IOLoop.instance().start()
