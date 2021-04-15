# TODO: Uncomment the lcd_1in44 line and comment the lcd_stub one if you want to run it on the display
# from lcd_1in44 import LCD
from lcd_stub import LCD

from PIL import Image, ImageDraw, ImageFont

from typing import List, Tuple, Dict, Callable
import json
import time
import datetime
import pytz
import math

import requests


def fetch_ohlc(symbol: str) -> List[Tuple[float, ...]]:
    res = requests.get(
        "https://api.binance.com/api/v3/klines", params={"symbol": symbol.upper(), "interval": "1h", "limit": 25})
    res.raise_for_status()

    json_data = json.loads(res.text)

    ohlc = []
    for data_entry in json_data:
        ohlc.append(tuple([float(data_entry[i]) for i in [1, 2, 3, 4]]))

    return ohlc


def fetch_crypto_data(symbol: str) -> Tuple[float, float, List[Tuple[float, ...]]]:
    ohlc_data = fetch_ohlc(symbol)
    price_current = ohlc_data[-1][-1]
    price_day_ago = ohlc_data[0][0]
    price_diff = price_current - price_day_ago

    return price_current, price_diff, ohlc_data


def render_candlestick(ohlc: Tuple[float, ...], x: int, y_transformer: Callable[[float], int], draw: ImageDraw):
    color = (255, 55, 55, 255) if ohlc[3] < ohlc[0] else (55, 255, 55, 255)
    draw.rectangle((x, y_transformer(
        max(ohlc[0], ohlc[3])), x + 2, y_transformer(min(ohlc[0], ohlc[3]))), fill=color)
    draw.line(
        (x + 1, y_transformer(ohlc[1]), x + 1, y_transformer(ohlc[2])), fill=color)


def render_ohlc_data(ohlc: List[Tuple[float, ...]], draw: ImageDraw):
    X_START = 18
    Y_START = 54
    HEIGHT = 50

    y_min = min([d[2] for d in ohlc])
    y_max = max([d[1] for d in ohlc])

    def y_transformer(y: float) -> int:
        multiplier = HEIGHT / (y_max - y_min)
        offset = int(multiplier * (y - y_min))
        return Y_START + HEIGHT - offset

    x = X_START + 24 * 4 + 1
    for candle_data in ohlc[::-1]:
        x -= 4
        render_candlestick(candle_data, x, y_transformer, draw)


def price_to_str(price: float) -> str:
    exp10 = math.floor(math.log10(abs(price)))
    num_decimals = int(min(5, max(0, 3 - exp10)))
    return "%.*f" % (num_decimals, price)


def main():
    lcd = LCD()
    lcd.LCD_Init()
    lcd.LCD_Clear()

    img = Image.new("RGB", (lcd.width, lcd.height))
    font = ImageFont.truetype("OpenSans-Regular.ttf", 20)
    font_small = ImageFont.truetype("OpenSans-Regular.ttf", 16)
    font_tiny = ImageFont.truetype("OpenSans-Regular.ttf", 12)

    timezone = pytz.timezone("US/Eastern")
    while True:
        price, diff, ohlc = fetch_crypto_data("btcusdt") # TODO: use any binance symbol you want (Ex.: DOGE = dogeusdt)

        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, lcd.width, lcd.height), fill=(0, 0, 0, 0))
        draw.text((8, 5), text="{}$".format(
            price_to_str(price)), font=font, fill=(255, 255, 255, 255))

        diff_symbol = ""
        diff_color = (255, 255, 255, 255)
        if diff > 0:
            diff_symbol = "+"
            diff_color = (55, 255, 55, 255)
        if diff < 0:
            diff_color = (255, 55, 55, 255)

        draw.text((8, 30), text="{}{}$".format(diff_symbol,
                                               price_to_str(diff)), font=font_small, fill=diff_color)
        draw.text((6, 106), text=datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S"),
                  font=font_tiny, fill=(200, 200, 200, 255))

        render_ohlc_data(ohlc, draw)

        lcd.LCD_ShowImage(img)
        time.sleep(30)


if __name__ == "__main__":
    main()
