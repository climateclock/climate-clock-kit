#!/usr/bin/env python3

import json
import os
import sys
import time
from datetime import datetime, timezone

import requests
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics


FONT = '9x18B.bdf'
TIME_COLOR = '#ffd919'
CO2_COLOR = '#9900e6'
JSON = 'https://raw.githubusercontent.com/beautifultrouble/climate-clock-widget/master/src/clock.json'

# TODO: Pull these from the network
SECONDS_PER_YEAR = 365.25 * 24 * 3600
START_DATE = datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
START_EMISSIONS_BUDGET = 4.2e11
START_EMISSIONS_YEARLY = 4.2e10


relpath = lambda filename: os.path.join(sys.path[0], filename)
hex2color = lambda x: graphics.Color(int(x[-6:-4], 16), int(x[-4:-2], 16), int(x[-2:], 16))


def time_and_budget():
    '''
    Return the time (in seconds) until the carbon budget is spent, and the
    remaining carbon budget (in tons).
    '''
    now = datetime.now(timezone.utc)
    emissions_per_second = START_EMISSIONS_YEARLY / SECONDS_PER_YEAR
    emissions_budget_spent = ((now - START_DATE).total_seconds() * emissions_per_second)
    emissions_budget = START_EMISSIONS_BUDGET - emissions_budget_spent
    time_remaining = emissions_budget / emissions_per_second
    
    return time_remaining, emissions_budget


def run(options):
    matrix = RGBMatrix(options=options)
    canvas = matrix.CreateFrameCanvas()

    font = graphics.Font()
    font.LoadFont(relpath(FONT))

    time_color = hex2color(TIME_COLOR)
    co2_color = hex2color(CO2_COLOR)

    while not time.sleep(.25):
        time_remaining, emissions_budget = time_and_budget()

        years, r = divmod(time_remaining, SECONDS_PER_YEAR)
        days, r = divmod(r, 24 * 3600)
        hours, r = divmod(r, 3600)
        minutes, seconds = divmod(r, 60)
        time_string = (f"{years:1.0f}{'YR' if years == 1 else 'YRS'} "
                       f"{days:3.0f}{'DAY' if days == 1 else 'DAYS'} "
                       f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}")

        budget_string = f"{int(emissions_budget):,} TONS"

        canvas.Clear()
        graphics.DrawText(canvas, font, 1, 14, time_color, time_string)
        graphics.DrawText(canvas, font, 1, 28, co2_color, budget_string)
        canvas = matrix.SwapOnVSync(canvas)


options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 3
options.gpio_slowdown = (0, 1, 2, 3)[2 - (options.chain_length == 3)]
# These may be preconfigured in the rgbmatrix library
options.hardware_mapping = 'adafruit-hat' 
options.disable_hardware_pulsing = True

run(options)

