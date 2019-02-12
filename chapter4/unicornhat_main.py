#!/usr/bin/env python3
# coding: utf-8

from logging import getLogger
logger = getLogger('unicorn_mqtt_display')

from logging import Formatter, StreamHandler, INFO
import sys
import os

logger.setLevel(INFO)
handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(
    Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
)
logger.addHandler(handler)


from unicorn_mqtt_display.mqtt import start, end

if __name__ == '__main__':
    try:
        start()

    except KeyboardInterrupt:
        pass

    except Exception as e:
        logger.exception(e)
        raise e

    finally:
        logger.info('stopping...')
        end()
        sys.stdout.write("bye.\n")
