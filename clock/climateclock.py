#!/usr/bin/env python3

import os
import sys
import time
from datetime import datetime, timezone

import config
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

# Pulled from dateutil without all the dependencies
from relativedelta import relativedelta


SECONDS_PER_YEAR = 365.25 * 24 * 3600

# Snapshot of API data (the Good Stuff™)
CARBON_DEADLINE_1 = datetime.fromisoformat("2028-01-01T12:00:00+00:00")
RENEWABLES_1 = {
    "initial": 11.4,
    "timestamp": datetime.fromisoformat("2020-01-01T00:00:00+00:00"),
    "rate": 2.0428359571070087e-08,
}


relpath = lambda filename: os.path.join(sys.path[0], filename)
hex2color = lambda x: graphics.Color(
    int(x[-6:-4], 16), int(x[-4:-2], 16), int(x[-2:], 16)
)


def carbon_deadline_1():
    return relativedelta(CARBON_DEADLINE_1, datetime.now(timezone.utc))


def renewables_1():
    t = (datetime.now(timezone.utc) - RENEWABLES_1["timestamp"]).total_seconds()
    return RENEWABLES_1["rate"] * t + RENEWABLES_1["initial"]


def run(options):
    matrix = RGBMatrix(options=options)
    canvas = matrix.CreateFrameCanvas()

    f1 = graphics.Font()
    f1.LoadFont(relpath("10x20.bdf"))
    f2 = graphics.Font()
    f2.LoadFont(relpath("6x13.bdf"))
    f3 = graphics.Font()
    f3.LoadFont(relpath("8x13.bdf"))
    L1 = 15
    L2 = 30

    red = hex2color("#ff0000")
    green = hex2color("#00ff00")

    while not time.sleep(0.05):
        canvas.Clear()

        # Deadline
        now = datetime.now(timezone.utc)

        # Use relativedelta for leap-year awareness
        deadline_delta = relativedelta(CARBON_DEADLINE_1, now)
        years = deadline_delta.years
        # Extract concrete days from the months & days provided by relativedelta
        # @rubberduck: 1. Create a relativedelta object rdays containing Δ months & days
        #              2. Create a concrete time object rdays in the future
        #              3. Create a timedelta object representing that value - now
        #              4. Extract its days
        rdays = relativedelta(months=deadline_delta.months, days=deadline_delta.days)
        days = ((rdays + now) - now).days
        hours = deadline_delta.hours
        minutes = deadline_delta.minutes
        seconds = deadline_delta.seconds
        cs = deadline_delta.microseconds // 10000

        deadline = [
            [f1, red, 1, f"{years:1.0f}"],
            [f3, red, 1, "YEAR " if years == 1 else "YEARS"],
            [f1, red, 1, f"{days:03.0f}"],
            [f3, red, 1, "DAY " if days == 1 else "DAYS"],
            [f1, red, -2, f"{hours:02.0f}"],
            [f1, red, -1, (":", " ")[cs < 50]],
            [f1, red, -2, f"{minutes:02.0f}"],
            [f1, red, -1, (":", " ")[cs < 50]],
            [f1, red, 0, f"{seconds:02.0f}"],
        ]

        x = 1
        for font, color, space, string in deadline:
            x += space + graphics.DrawText(canvas, font, x, L1, color, string)

        # Lifeline
        r1 = renewables_1()
        lifeline = [
            [f1, green, -2, f"{r1:.0f}"],
            [f1, green, -2, f"."],
            [f1, green, 3, f"{format(r1, '.9f').split('.')[1]}%"],
            [f2, green, 0, "RENEWABLES"],
        ]

        x = 1
        for font, color, space, string in lifeline:
            x += space + graphics.DrawText(canvas, font, x, L2, color, string)

        canvas = matrix.SwapOnVSync(canvas)


options = RGBMatrixOptions()
for key, value in vars(config).items():
    if not key.startswith("__"):
        setattr(options, key, value)


if __name__ == "__main__":
    run(options)
