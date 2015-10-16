# -*- coding: utf-8 -*-

import json

import pika


CRAWLER_Q_NAME = 'crawler_q'
PARSER_Q_NAME = 'parser_q'


class Q:
    def __init__(self):
        self.conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.conn.channel()
        self.channel.queue_declare(queue=CRAWLER_Q_NAME, durable=True)
        self.channel.queue_declare(queue=PARSER_Q_NAME, durable=True)
        self.channel.basic_qos(prefetch_count=10)

    def add_crawler_task(self, domains):
        message = json.dumps(domains)
        self.channel.basic_publish('', CRAWLER_Q_NAME, message)

    def get_crawler_task(self):
        method_frame, header_frame, body = self.channel.basic_get(CRAWLER_Q_NAME)
        if not method_frame:
            return None

        return method_frame, header_frame, json.loads(body)

    def complete_task(self, method_frame):
        self.channel.basic_ack(method_frame.delivery_tag)

    def add_parser_task(self, domain_id):
        self.channel.basic_publish('', PARSER_Q_NAME, str(domain_id))

    def get_parser_task(self):
        method_frame, header_frame, body = self.channel.basic_get(PARSER_Q_NAME)
        if not method_frame:
            return None

        return method_frame, header_frame, body

