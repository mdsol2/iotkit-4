#!/usr/bin/env python3
# coding: utf-8

from logging import getLogger
logger = getLogger(__name__)

from PIL import Image
from io import BytesIO
import unicornhathd
import datetime
import requests
import os
import sys
import time


APIBASE = 'https://api.openweathermap.org/data/2.5/forecast'
ICON_PATH = 'http://openweathermap.org/img/w'
APIKEY = os.environ.get('OPENWEATHER_API_KEY')

CITY = os.environ['WEATHER_CITY']


width, height = unicornhathd.get_shape()


def getWeather(city, apikey):
    """
    天気を取得する
    リクエストにAPIKeyと都市をパラメーターに入れる

    https://openweathermap.org/forecast5
    """

    logger.debug('get weather of %s from API', city)

    payload = {
        'APIKEY': APIKEY,
        'q': CITY
    }
    r = requests.get(
        APIBASE,
        params=payload
    )
    return r


def filterNearstWeather(weathers, date):
    """
    openWeatherレスポンスのweatherリストから指定時刻に一番近いものを選択する
    Noneが帰る場合もある
    """

    if isinstance(date, datetime.datetime):
        target_timestamp = date.timestamp()
    else:
        target_timestamp = date

    weather = None
    for i in weathers:
        if i['dt'] > target_timestamp and abs(i['dt'] - target_timestamp) <= 3600 * 3:
            weather = i
            break

    return weather

def getIconImage(icon):
    """
    openWeatherのアイコンデータを取得する。

    やり方としてはHTTPリクエストでpngファイルを取得し、
    PILのimage形式にしてリサイズする。

    https://openweathermap.org/weather-conditions
    """

    # os.path.joinでアイコンIDにURLと拡張子をくっつける
    # パス周りの操作はなるべくこれを使ったほうが無難
    # https://docs.python.jp/3/library/os.path.html
    path = os.path.join(ICON_PATH, icon + '.png')
    logger.debug('request image from %s', path)

    # requestsを使用してアイコンの取得
    r = requests.get(path)

    if r.ok:
        # リクエストが正常終了した場合の処理

        # このリクエストではバイナリ（画像）を扱うので、
        # Pillowに渡すときはio.BytesIOを介す必要がある。
        # https://docs.python.jp/3/library/io.html
        image = Image.open(BytesIO(r.content))

        # 画像をリサイズし、RGBモードに変換する。
        # （大本は透過が入っているため）
        image.thumbnail((width, height))
        image = image.convert('RGB')

        return image

    logger.warning('fail of image get. %s', path)
    return None

def main():
    """
    メイン処理
    これをループし続ける
    """

    # 現在時刻の取得
    now = datetime.datetime.now()

    # datetimeオブジェクトをUnixTimeに変換し、ターゲット時間を作る
    # ターゲットを2時間先とする
    target_timestamp = now.timestamp() + 60 * 60 * 2

    try:
        r = getWeather(CITY, APIKEY)
        if not r.ok:
            logger.warn('error, weather get fail')
            time.sleep(30 * 3)
            return

        weathers = r.json()['list']
        weather = filterNearstWeather(weathers, target_timestamp)
        logger.debug('weather is %s', weather)

        image = getIconImage(weather['weather'][0]['icon'])

        if image is None:
            logger.warning("image is None.")
            time.sleep(30 * 3)
            return

    except requests.exceptions.ConnectionError as e:
        logger.exception(e)
        time.sleep(30 * 3)

    except KeyError:
        time.sleep(30 * 3)
        return

    logger.debug('start write icon.')

    unicornhathd.clear()

    # x, yを指定して1ドットずつ描写する
    for x in range(width):
        for y in range(height):
            r, g, b = image.getpixel((x, y))
            # ここの部分でx軸を反転させている
            unicornhathd.set_pixel(width-x-1, y, r, g, b)

    unicornhathd.show()

    time.sleep(1800)


if __name__ == '__main__':
    """
    この書き方をしているのは
    これをライブラリとしてロードできるようにするため。

    https://docs.python.jp/3/library/__main__.html

    """

    # ロガーの設定
    # スクリプトとして動作する場合のみ出力ハンドラを追加する。
    from logging import StreamHandler, INFO, DEBUG, Formatter

    # 環境変数DEBUGによってロギングレベルを変更する
    if os.environ.get('DEBUG', None):
        logger.setLevel(DEBUG)
    else:
        logger.setLevel(INFO)

    # StreamHandlerはそのまま標準出力として出力する。
    # つまりprint()と同様の動きをする
    handler = StreamHandler(stream=sys.stdout)
    handler.setFormatter(Formatter('[%(levelname)s] %(asctime)s %(message)s'))
    logger.addHandler(handler)

    logger.info('start application.')
    logger.info('city is %s', CITY)

    unicornhathd.brightness(0.5)
    unicornhathd.rotation(0)

    # ここがメイン処理。
    # main()をひたすらループさせる。
    # finally
    try:
        while True:
            main()

    # Ctrl+C時に起きる例外を取得し、エラーメッセージが出ないようにする。
    except KeyboardInterrupt:
        logger.info('detect sigterm. goodbye.')

    # finallyは例外が出ようが出まいが終了時に必ず動作される。
    # ここでは、unicornhathdの終了処理を行わさせている。
    finally:
        unicornhathd.off()

