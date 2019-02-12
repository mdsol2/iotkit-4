#!/usr/bin/env python3
# coding: utf-8

"""
    MQTTの簡単なパブリッシャー

    usage: mqtt_publish.py [-h] [-H HOST] [-P PORT] [-t TOPIC] [-u USER] [-p PASSWORD] [-r]
                 [-d]
                 message

    positional arguments:
      message

    optional arguments:
      -h, --help            show this help message and exit
      -H HOST, --host HOST  host
      -P PORT, --port PORT  port
      -t TOPIC, --topic TOPIC
      -u USER, --user USER
      -p PASSWORD, --password PASSWORD
      -r, --retain
      -d, --debug


    $ python3 mqtt_publish.py -H test.mosquitto.org -P 1883 -t 'aichi/nagoya' 'message'

    必須パッケージ
    - paho-mqtt
"""

from logging import getLogger, DEBUG, INFO, StreamHandler
import sys
logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(StreamHandler(stream=sys.stdout))

import argparse
import paho.mqtt.client as mqtt
import os

parser = argparse.ArgumentParser(description="")
parser.add_argument('-H', '--host', action='store', type=str, default='localhost', help='host')
parser.add_argument('-P', '--port', action='store', type=int, default=1883, help='port')
parser.add_argument('-t', '--topic', action='store', type=str, default='test')
parser.add_argument('-u', '--user', action='store', type=str, default=None)
parser.add_argument('-p', '--password', action='store', type=str, default=None)
parser.add_argument('-r', '--retain', action='store_true', default=False)
parser.add_argument('-d', '--debug', action='store_true', default=False)
parser.add_argument('message', metavar='message', action='store', type=str, default=None)

def main():
    arg = parser.parse_args()
    topic = arg.topic

    if arg.debug:
        logger.setLevel(DEBUG)

    logger.debug(arg)

    message = arg.message
    if not os.isatty(0):
        message = sys.stdin.read()

    if not message:
        sys.stdout.write("EMPTY MESSAGE. \r\n")
        sys.exit(1)

    client = mqtt.Client(protocol=mqtt.MQTTv311)

    if arg.user:
        client.username_pw_set(arg.user, password=arg.password)

    try:
        client.connect(arg.host, arg.port)
        client.publish(topic, message, retain=arg.retain)
    finally:
        client.disconnect()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)

