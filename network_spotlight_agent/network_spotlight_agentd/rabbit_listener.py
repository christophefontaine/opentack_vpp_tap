#!/usr/bin/env python
# Copyright  Qosmos 2000-2015 - All rights reserved

import pika
import json
import sys
import argparse
import traceback
from threading import Thread

# All conf variables are in conf.py
from conf import RABBIT_USER, RABBIT_PASSWORD, RABBIT_SERVER

MQHooks = []


class AMQPListener(Thread):
    def __init__(self, exchange_name, routing_key):
        Thread.__init__(self)
        self.daemon = True
        credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)
        conn_param = pika.ConnectionParameters(host=RABBIT_SERVER,
                                               credentials=credentials)
        self.connection = pika.BlockingConnection(conn_param)
        self.channel = self.connection.channel()
        self.instances = dict()
        result = self.channel.queue_declare()
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange_name,
                                queue=queue_name,
                                routing_key=routing_key)
        self.channel.basic_consume(self.callback,
                                   queue=queue_name,
                                   no_ack=True)

    def run(self):
        self.channel.start_consuming()

    def stop(self):
        self.channel.stop_consuming()

    def callback(self, ch, method, properties, body):
        try:
            msg = json.loads(body)
        except:
            print "Error when loading msg: %s" % msg
            return
        try:
            # print '***********************************  MSG  ****************************************'
            if 'oslo.message' in msg:
                msg = json.loads(msg['oslo.message'])  # The payload is a json string
                method_name = ""
                # print " [%s:%s] Received %s" % (ch, method, json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': ')))
                for class_instance in MQHooks:
                    method_name = '_RPC_' + msg["method"]
                    if method_name in dir(class_instance):
                        getattr(class_instance, method_name)(msg['args'])

#            print '***********************************  END  ****************************************'
        except Exception:
            print '*********************************** ERROR ****************************************'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print (repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            print " [%s:%s] Received %s" % (ch, method, json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': ')))
            print '**********************************************************************************'
            raise


def list_exchanges():
    import subprocess
    import re
    return re.findall('\n?(.*)\ttopic\n', subprocess.check_output('rabbitmqctl list_exchanges', shell=True))


def run_listener(exchange_name, routing_key):
    listener = AMQPListener(exchange_name, routing_key)
    try:
        listener.run()
    except KeyboardInterrupt:
        listener.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--topic', default='nova',
                        required=True, dest='exchange_name',
                        choices=list_exchanges(),
                        help='MQ channel topic, default to "nova"')
    parser.add_argument('-r', '--routing-key', default='#',
                        required=False, dest='routing_key',
                        help='MQ routing key, default to "#"')
    args = parser.parse_args()
    print ' [*] Waiting for messages [%s:%s] To exit press CTRL+C' % (args.exchange_name, args.routing_key)
    run_listener(args.exchange_name, args.routing_key)


if __name__ == '__main__':
    main()
