#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import sys
import time
import logging
import requests
from waveshare_epd import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# 로그 설정
logging.basicConfig(level=logging.DEBUG)

# e-Paper 초기화
epd = epd2in13_V4.EPD()
epd.init()
epd.Clear(0xFF)  # 화면 초기화

# 폰트 설정 (폰트 파일 경로)
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font12 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 12)


# -------------------------------------------------
def get_exchange_rate():
    """ USD/KRW 환율 가져오는 함수 """

    try:
        # USD/KRW 환율 가져오기
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url)
        data = response.json()
        usd_krw = data["rates"]["KRW"]
        return usd_krw
    except Exception as e:
        logging.error(f"USD 환율 정보를 가져오는 중 오류 발생: {e}")
        return None


# -------------------------------------------------
def get_jpy_exchange_rate():
    """ JPY/KRW 환율 가져오는 함수 """

    try:
        # JPY/KRW 환율 가져오기
        url = "https://api.exchangerate-api.com/v4/latest/JPY"
        response = requests.get(url)
        data = response.json()
        usd_krw = data["rates"]["KRW"]
        return usd_krw
    except Exception as e:
        logging.error(f"JPY 환율 정보를 가져오는 중 오류 발생: {e}")
        return None


# -------------------------------------------------
def get_bitcoin_price():
    """ 비트코인 가격 가져오는 함수 """

    try:
        # 코인게코에서 비트코인 가격 (USD) 가져오기
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        btc_usd = data["bitcoin"]["usd"]
        return btc_usd
    except Exception as e:
        logging.error(f"비트코인 가격 정보를 가져오는 중 오류 발생: {e}")
        return None


# -------------------------------------------------
def main():
    """ 메인함수 """
    # 초기 화면 설정 (기본 배경)
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)

    # 기본 화면을 설정한 후 부분 업데이트를 사용할 것
    epd.displayPartBaseImage(epd.getbuffer(image))

    try:
        while True:
            # 환율 및 비트코인 가격 가져오기
            usd_krw = get_exchange_rate()
            jpy_krw = get_jpy_exchange_rate()
            btc_usd = get_bitcoin_price()
            last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 화면 지우기 (부분 업데이트를 위해 흰색으로 덮어씌움)
            draw.rectangle((0, 0, epd.height, epd.width), fill=255)

            # 정보 표시
            if usd_krw is not None:
                draw.text((10, 10),
                          f"USD/KRW: {usd_krw:,.2f}",
                          font=font18,
                          fill=0)
            else:
                draw.text((10, 10), "USD/KRW: Error", font=font18, fill=0)

            if jpy_krw is not None:
                draw.text((10, 35),
                          f"JPY/KRW: {jpy_krw:,.2f}",
                          font=font18,
                          fill=0)
            else:
                draw.text((10, 35), "JPY/KRW: Error", font=font18, fill=0)

            if btc_usd is not None:
                draw.text((10, 60),
                          f"BTC/USD: ${btc_usd:,.2f}",
                          font=font18,
                          fill=0)
            else:
                draw.text((10, 60), "BTC/USD: Error", font=font18, fill=0)

            if last_updated is not None:
                draw.text((10, 85), f"Last Updated:", font=font12, fill=0)
                draw.text((10, 100), last_updated, font=font12, fill=0)

            # e-Paper 부분 업데이트
            epd.displayPartial(epd.getbuffer(image))

            # 1분 대기 후 업데이트
            time.sleep(60)

    except KeyboardInterrupt:
        logging.info("Ctrl + C Detected, Clearing Screen and Exiting...")
        epd.init()
        epd.Clear(0xFF)
        epd.sleep()
        sys.exit()


# -------------------------------------------------
if __name__ == '__main__':
    main()
