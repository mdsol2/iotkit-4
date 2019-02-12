# coding: utf-8

"""
    画面操作の制御を行う
    __init__.pyファイルはこのディレクトリ以下をインポートされると必ず呼び出されるのでここに書く。
    もちろん、コードが増えてきた場合は別途ファイルに書いてここでインポートする構成でも構いません。

    ここでは画面に何を表示するかの管理を行う。
    このライブラリはMQTTと画面表示での並列動作が必要なので、
    threadingライブラリを使用してそれを実現しています。

    https://docs.python.jp/3/library/threading.html
"""

from logging import getLogger
logger = getLogger(__name__)

import unicornhathd
import time

# 表示動作を行う関数のインポート
from .clock import loop as clock_loop
from .weather import loop as weather_loop

from threading import Thread, Event

# eventオブジェクトを作成する
# https://docs.python.jp/3/library/threading.html#event-objects
event = Event()
driver = None

def change(mode):
    """
       画面の変更要求を受け付ける関数。
       使用時はこれをインポートして、随時関数を始動してこれを操作する。
    """

    # 渡されたモードの確認。
    # 知らないモードが渡された場合はここで受付を棄却する
    if mode not in ('clock', 'weather'):
        logger.warn('invalid mode (%s)', mode)
        return False

    logger.debug('get change call to "%s"', mode)

    # モードに対応した関数を用意する
    func = None
    if mode == 'clock':
        func = clock_loop
    elif mode == 'weather':
        func = weather_loop
    else:
        logger.error('cant get function.')
        return False

    # イベントオブジェクトをセットして現在動作している表示処理を終了させる。
    # これがセットされると表示関数中ループを抜け出すことにより関数が終了し、デーモンも消滅する。
    # 各表示関数はwhileループ毎でこれを確認しているので終了には時間がかかる。
    # なのである程度待つ必要がある。
    # 動作モードによって終了に必要な時間にばらつきがある場合は、Lockオブジェクトを使用するのもアリ
    event.set()
    time.sleep(1)
    # イベントオブジェクトをリセットして再利用可能にする
    event.clear()

    #　Threadオブジェクトに動作関数を渡し、並列動作を開始させる（デーモンの作成）
    # ここでeventオブジェクトを渡して終了イベントを渡せるようにする
    # https://docs.python.jp/3/library/threading.html#thread-objects
    driver = Thread(target=func, args=(event,))
    driver.daemon = True
    driver.start()

    logger.debug('change sequence is end.')
    return True

def start():
    ```
        スタート用の関数
        呼び出されるととりあず時計を表示する
    ```
    logger.debug('display initial function start.')
    change('clock')

def end():
    ```
        処理終了用の関数
        デーモンを終了させ、unicornHatHDの表示をOFFにする。
    ```
    event.set()
    time.sleep(1)
    unicornhathd.off()
