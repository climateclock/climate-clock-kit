#!/usr/bin/env python3

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import aiohttp

import config
from api import provide_clock_modules


modules = []


async def update_clock(options: rgbmatrix.RGBMatrixOptions, quit: asyncio.Future) -> None:
    from pprint import pprint
    while True:
        print(__import__('time').time(), len(modules))
        pprint(modules)
        await asyncio.sleep(.2)


async def main() -> [str, int]:
    '''
    Load matrix config and launch all tasks
    '''
    options = None
    #options = RGBMatrixOptions()
    #for key, value in vars(config).items():
        #if not key.startswith('__'):
            #setattr(options, key, value)

    async with aiohttp.ClientSession() as http:
        loop.create_task(provide_clock_modules(http, modules))
        loop.create_task(update_clock(options))
        await quit
    

if __name__ == '__main__':
    quit = asyncio.Future()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
