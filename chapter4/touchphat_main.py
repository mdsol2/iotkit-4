#! /usr/bin/env python3
# coding: utf-8

"""
    touchphat_mqtt_controllerを始動させるサンプル
    別途環境変数の指定が必要です。

    
    必要な環境変数は以下のとおりです。
    
    MQTT_TARGET_NAME 表示制御を行うUnicornHatHDで指定した名前
    MQTT_NAME MQTT上で使用する名前
    MQTT_HOST MQTTホスト名
    MQTT_USER MQTTユーザー名
    MQTT_PASSWORD MQTTパスワード
    MQTT_PORT MQTTポート
 """

# ロギング設定
# 今回は標準出力でINFO以上のログを出力する

# ロガー作成
from logging import getLogger
logger = getLogger('touchphat_mqtt_controller')

# ハンドラの指定（出力設定）
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


# ここから始動処理

from touchphat_mqtt_controller import main

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

    except Exception as e:
        logger.exception(e)
        raise e

    finally:
        logger.info('stopping...')
        sys.stdout.write("bye.\n")
