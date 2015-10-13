# -*- coding: utf-8 -*-

import multiprocessing as mp
import logging

from tornado.options import options
import tornado.gen
from tornado.log import app_log
from fd_table_status import fd_table_status_str as fds


def get_process_name():
    return '%d-%s' % (mp.current_process().pid, mp.current_process().name)


def return_by_raise(val=None):
    raise tornado.gen.Return(val)


def app_log_process(message, level=logging.INFO):
    app_log.log(level, '(%s) %s' % (get_process_name(), message))


def log_fds(mes=''):
    if options.debug:
        app_log.log(logging.DEBUG, 'fds (%s): %s' % (mes, fds()))