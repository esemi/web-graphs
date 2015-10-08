# -*- coding: utf-8 -*-

import json

import pika


CRAWLER_Q_NAME = 'crawler_q'


class Q:
    def __init__(self):
        self.conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.conn.channel()
        self.channel.queue_declare(queue=CRAWLER_Q_NAME, durable=True)
        self.channel.basic_qos(prefetch_count=1)

    def add_crawler_task(self, domains):
        message = json.dumps(domains)
        self.channel.basic_publish('', CRAWLER_Q_NAME, message)
