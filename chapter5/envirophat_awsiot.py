#! /usr/bin/env pyhton3

from logging import getLogger
logger = getLogger(__name__)

import envirophat
import time
import datetime
import os
import sys
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json


CHECK_SPAN = int(os.environ.get('CHECK_SPAN', '30'))
ENDPOINT=os.environ.get('AWSIOT_ENDPOINT')
ROOTCA = os.environ.get('AWSIOT_ROOTCA')
CERT = os.environ.get('AWSIOT_CERT')
PRIVATE = os.environ.get('AWSIOT_PRIVATE')
THING_NAME = os.environ.get('THING_NAME')


client = AWSIoTMQTTClient(THING_NAME)
client.configureEndpoint(ENDPOINT, 8883)
client.configureCredentials(ROOTCA, PRIVATE, CERT)

client.configureAutoReconnectBackoffTime(1, 32, 20)
client.configureOfflinePublishQueueing(-1)
client.configureDrainingFrequency(2)
client.configureConnectDisconnectTimeout(300)
client.configureMQTTOperationTimeout(5)


if __name__ == '__main__':
    from logging import StreamHandler
    logger.addHandler(StreamHandler(stream=sys.stdout))

    client.connect(250)

    # main loop
    while True:
        try:
            shadow = {
                "state": {
                    "reported": {
                        "temperature": round(envirophat.weather.temperature(), 1) - 2,
                        "pressure": round(envirophat.weather.pressure(unit='hPa'), 1),
                        "light": envirophat.light.light()
                    }
                }
            }

            client.publish('$aws/things/'+THING_NAME+'/shadow/update', json.dumps(shadow), 1)

        except IOError:
            # this is connection error to enviro phat
            time.sleep(CHECK_SPAN)
            continue

        except Exception as e:
            logger.exception(e)


        # wait time to next send timing
        time.sleep(CHECK_SPAN)

