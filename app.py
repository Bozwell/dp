#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import sys
import time
import logging
import requests
from waveshare_epd import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# Log configuration
logging.basicConfig(level=logging.DEBUG)

# Initialize e-Paper
epd = epd2in13_V4.EPD()
epd.init()
epd.Clear(0xFF)  # Clear screen

# Font settings (font file path)
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font12 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 12)

# Functions to get exchange rates and bitcoin price
def get_exchange_rate():
    try:
        # Get USD/KRW exchange rate
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url)
        data = response.json()
        usd_krw = data["rates"]["KRW"]
        return usd_krw
    except Exception as e:
        logging.error(f"Error occurred while getting USD exchange rate: {e}")
        return None
    
def get_jpy_exchange_rate():
    try:
        # Get JPY/KRW exchange rate
        url = "https://api.exchangerate-api.com/v4/latest/JPY"
        response = requests.get(url)
        data = response.json()
        usd_krw = data["rates"]["KRW"]
        return usd_krw
    except Exception as e:
        logging.error(f"Error occurred while getting JPY exchange rate: {e}")
        return None

def get_bitcoin_price():
    try:
        # Get Bitcoin price (USD) from CoinGecko
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        btc_usd = data["bitcoin"]["usd"]
        return btc_usd
    except Exception as e:
        logging.error(f"Error occurred while getting Bitcoin price: {e}")
        return None

# Initial screen setup (background)
image = Image.new('1', (epd.height, epd.width), 255)
draw = ImageDraw.Draw(image)

# Set base image for partial updates
epd.displayPartBaseImage(epd.getbuffer(image))

try:
    while True:
        # Get exchange rates and bitcoin price
        usd_krw = get_exchange_rate()
        jpy_krw = get_jpy_exchange_rate()
        btc_usd = get_bitcoin_price()
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Clear screen (fill with white for partial update)
        draw.rectangle((0, 0, epd.height, epd.width), fill=255)

        # Display information
        if usd_krw is not None:
            draw.text((10, 10), f"USD/KRW: {usd_krw:,.2f}", font=font18, fill=0)
        else:
            draw.text((10, 10), "USD/KRW: Error", font=font18, fill=0)

        if jpy_krw is not None:
            draw.text((10, 35), f"JPY/KRW: {jpy_krw:,.2f}", font=font18, fill=0)
        else:
            draw.text((10, 35), "JPY/KRW: Error", font=font18, fill=0)

        if btc_usd is not None:
            draw.text((10, 60), f"BTC/USD: ${btc_usd:,.2f}", font=font18, fill=0)
        else:
            draw.text((10, 60), "BTC/USD: Error", font=font18, fill=0)

        if last_updated is not None:
            draw.text((10, 85), f"Last Updated:", font=font12, fill=0)
            draw.text((10, 100), last_updated, font=font12, fill=0)


        # Partial update of e-Paper display
        epd.displayPartial(epd.getbuffer(image))

        # Wait 1 minute before next update
        time.sleep(60)

except KeyboardInterrupt:
    logging.info("Ctrl + C Detected, Clearing Screen and Exiting...")
    epd.init()
    epd.Clear(0xFF)
    epd.sleep()
    sys.exit()

