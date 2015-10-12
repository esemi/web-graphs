# -*- coding: utf-8 -*-

import multiprocessing as mp
import logging

import tornado.gen
from tornado.log import app_log


def get_process_name():
    return '%d-%s' % (mp.current_process().pid, mp.current_process().name)


def return_by_raise(val=None):
    raise tornado.gen.Return(val)


def app_log_process(message, level=logging.INFO):
    app_log.log(level, '(%s) %s' % (get_process_name(), message))
