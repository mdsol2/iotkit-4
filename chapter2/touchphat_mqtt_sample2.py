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

NAME = 'TouchPhat Sample 1'

MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')
MQTT_PORT = int(os.environ.get('MQTT_PORT'))

TOPIC = 'button'

lock = Lock()

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.username_pw_set(MQTT_USER, password=MQTT_PASSWORD)

def main():
    client.connect(MQTT_HOST, MQTT_PORT)
    client.loop_forever()


@touchphat.on_release(['Back','A', 'B', 'C', 'D','Enter'])
def handle_touch(event):
    with lock:
        client.publish(
                topic=TOPIC,
                payload=event.name
            )
        time.sleep(1)

if __name__ == '__main__':
    main()
 