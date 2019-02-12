# coding: utf-8

"""
MQTT通信の制御部分を担う。

ここで通信、ディスプレイへの制御要求を出す。
使用する場合はstart(), stop()をインポートして動かす。

必要な環境変数

MQTT_NAME (任意）
MQTT_HOST
MQTT_USER
MQTT_PASSWORD
MQTT_PORT

https://www.eclipse.org/paho/clients/python/docs/
"""

from logging import getLogger
logger = getLogger(__name__)

import paho.mqtt.client as mqtt
from . import display
import json
import os

# 環境変数から通信状況を取得する
NAME = os.environ.get('MQTT_NAME', 'mqtt_display')
MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')
MQTT_PORT = int(os.environ.get('MQTT_PORT'))


# MQTTクライアントオブジェクトを作成する
client = mqtt.Client(protocol=mqtt.MQTTv311)


def on_connect(sclient, userdata, flags, respons_code):
    """
        接続完了時のコールバック
    """
    logger.debug('connection success.')

    # 画面の変更要求を受け付けるトピック名を購読する。
    client.subscribe('cmnd/' + NAME + '/display/change')
    # 接続できたことをパブリッシュする。
    client.publish('stat/' + NAME + '/status', 'connected.')


def on_message(client, userdata, msg):
    """
    　 メッセージ受信時に呼び出されるコールバック
       購読しているトピックにパブリッシュがあるとこれが呼び出される。
       メッセージ詳細は引数で渡される。
    """
    logger.debug('get message (%s)', msg.topic + ' : ' + msg.payload.decode('utf-8'))

    # 変更要求受付トピックで有ることを確認
    if msg.topic == 'cmnd/' + NAME + '/display/change':

        # メッセージはバイト型として渡されるので、デコードして文字型に変更する
        message = msg.payload.decode('utf-8')

        # ディスプレイに変更要求をする
        r = display.change(message)

        # 結果をパブリッシュする
        result = {
            'success': True if r else False,
            'mode': message
        }
        client.publish('result/' + NAME + '/display/change', json.dumps(result))


def on_disconnect(client, userdata, rc):
    """
        接続が切れた時に呼び出されるコールバック
        切断時は毎回呼び出されるが、異常切断の際にエラーログを残すようにする。
    """
    logger.debug('connection disconnected. rc=%s', rc)
    if rc != 0:
        logger.error('Unexpected disconnection.')


def start():
    """
        接続開始関数
    """

    # ユーザー情報をセット
    client.username_pw_set(MQTT_USER, password=MQTT_PASSWORD)
    # 各コールバックをセットする
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_connect = on_connect

    # 接続開始
    logger.debug('connection start.')
    client.connect(MQTT_HOST, MQTT_PORT)

    # ディスプレイのスタート
    display.start()

    # 通信処理の開始。
    # loop_forever()は通信が続く限りブロックされ続ける
    # https://www.eclipse.org/paho/clients/python/docs/#network-loop
    logger.debug('loop start.')
    client.loop_forever()


def end():
    display.end()
