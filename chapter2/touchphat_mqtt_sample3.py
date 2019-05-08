# coding: utf-8

"""

required packages
- touchphat
- paho.mqtt

"""

from logging import getLogger
logger = getLogger(__name__)

import paho.mqtt.client as mqtt
import touchphat
import os
from threading import Lock
import time

NAME = 'TouchPhat Sample 3'

MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')
MQTT_PORT = int(os.environ.get('MQTT_PORT'))

TOPIC = 'button'

lock = Lock()

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.error('Unexpected disconnection.')

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.username_pw_set(MQTT_USER, password=MQTT_PASSWORD)
client.on_disconnect = on_disconnect


def animation():
    touchphat.all_off()
    for i in range(1, 7):
        touchphat.led_on(i)
        time.sleep(0.05)
    for i in range(1, 7):
        touchphat.led_off(i)
        time.sleep(0.05)

def blink(key):
    touchphat.all_off()
    for i in range(0, 3):
        touchphat.led_off(key)
        time.sleep(0.1)
        touchphat.led_on(key)
        time.sleep(0.1)
    touchphat.all_off()


@touchphat.on_release(['Back','A', 'B', 'C', 'D','Enter'])
def handle_touch(event):
    with lock:
        client.publish(
                topic=TOPIC,
                payload=event.name
            )
        if event.name=='Enter':
            # Enter押下時にアニメーションを実行
            animation()
        else:
            blink(event.name)


def main():
    # 初回起動時にアニメーションを実行
    animation()
    client.connect(MQTT_HOST, MQTT_PORT)
    client.loop_forever()


if __name__ == '__main__':
    main()
