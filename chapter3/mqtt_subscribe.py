#!/usr/bin/env python3
# coding: utf-8

"""
    MQTTの簡単なサブスクライバー
    
    usage: mqtt_subscribe.py [-h] [-H HOST] [-P PORT] [-t TOPIC] [-u USER] [-p PASSWORD] [-d]
    optional arguments:
      -h, --help            show this help message and exit
      -H HOST, --host HOST  host
      -P PORT, --port PORT  port
      -t TOPIC, --topic TOPIC
      -u USER, --user USER
      -p PASSWORD, --password PASSWORD
      -d, --debug

    $ python3 mqtt_subscribe.py  -H test.mosquitto.org -t 'aichi/nagoya' -P 1883

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

# コマンドライン引数パーサの設定
# https://docs.python.jp/3/library/argparse.html
parser = argparse.ArgumentParser(description="MQTTの簡単なサブスクライバー")
parser.add_argument('-H', '--host', action='store', type=str, default='localhost', help='host')
parser.add_argument('-P', '--port', action='store', type=int, default=1883, help='port')
parser.add_argument('-t', '--topic', action='store', type=str, default='#')
parser.add_argument('-u', '--user', action='store', type=str, default=None)
parser.add_argument('-p', '--password', action='store', type=str, default=None)
parser.add_argument('-d', '--debug', action='store_true', default=False)


def main():
    # コマンドライン引数のパース
    arg = parser.parse_args()

    # 引数 --debug によりログレベルの変更
    if arg.debug:
        logger.setLevel(DEBUG)

    # トピックの設定
    topic = arg.topic

    def on_connect(client, userdata, flags, respons_code):
        logger.info('subscribe %s', topic)
        client.subscribe(topic)

    def on_message(client, userdata, msg):
        try:
            retain = 'Yes' if msg.retain else 'No'
            logger.info('%s retain=%s qos=%s [%s] %s', msg.timestamp, retain, msg.qos, msg.topic, msg.payload.decode('utf-8'))

        except Exception as e:
            logger.exception(e)


    client = mqtt.Client(protocol=mqtt.MQTTv311)

    if arg.user:
        client.username_pw_set(arg.user, password=arg.password)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(arg.host, arg.port)

    try:
        client.loop_forever()
    finally:
        client.disconnect()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('bye.')
        sys.exit(0)

