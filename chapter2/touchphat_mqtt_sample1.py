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
 
NAME = 'TouchPhat Sample 1'
 
 
MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')
MQTT_PORT = int(os.environ.get('MQTT_PORT'))
 
TOPIC = 'button'
 
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.username_pw_set(MQTT_USER, password=MQTT_PASSWORD)

def on_connect(client, userdata, flags, code):
    print('Status code: {0}'.format(code))
    client.publish(
            topic=TOPIC,
            payload=event.name
    )
 
def main():
    client.on_connect = on_connect
    client.connect(MQTT_HOST, MQTT_PORT)
    client.loop_forever()
 
@touchphat.on_release(['Back','A', 'B', 'C', 'D','Enter'])
def handle_touch(event):
    client.publish(
            topic=TOPIC,
            payload=event.name
        )
 
if __name__ == '__main__':
    main()
