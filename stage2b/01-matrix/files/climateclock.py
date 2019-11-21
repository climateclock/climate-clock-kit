#!/usr/bin/env python3

import time
import datetime

while not time.sleep(5):
    print('Tick')
    with open("/tmp/clock.text", "w") as f:
        f.write(str(datetime.datetime.now()))
