# -*- coding: utf-8 -*-

import multiprocessing as mp
import time
import logging
import resource

from tornado.options import options
import tornado.gen
from tornado.log import app_log
from pympler import tracker

from fd_table_status import fd_table_status_str as fds


def get_process_name():
    return '%d-%s' % (mp.current_process().pid, mp.current_process().name)


def return_by_raise(val=None):
    raise tornado.gen.Return(val)


def app_log_process(message, level=logging.INFO):
    app_log.log(level, '(%s) %s' % (get_process_name(), message))


def log_fds(mes=''):
    if options.debug:
        app_log_process('fds (%s): %s' % (mes, fds()), logging.DEBUG)


def log_mem(mes=''):
    if options.debug:
        app_log_process('mem (%s): %.2f mb' % (mes, float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024),
                        logging.DEBUG)


def to_unicode(s):
    if isinstance(s, unicode):
        return s
    elif isinstance(s, str):
        return unicode(s, encoding='utf-8', errors='ignore')
    else:
        return s


class LogStat():
    _tr = None
    _start_time = None
    _end_time = None

    @classmethod
    def start(cls):
        cls._start_time = time.time()
        cls._tr = tracker.SummaryTracker()

    @classmethod
    def end(cls, task_count):
        pass
        cls._end_time = time.time()
        sum_time_sec = cls._end_time - cls._start_time
        avg_task_per_sec = task_count / sum_time_sec
        app_log_process('stat log: sum time %.2fsec, sum task %d, task per sec %.2f' %
                        (sum_time_sec, task_count, avg_task_per_sec))
        cls._tr.print_diff()

