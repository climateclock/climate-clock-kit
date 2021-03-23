#!/usr/bin/env python3

from __future__ import annotations

import asyncio
import sys

import aiohttp
import rgbmatrix

import settings
import module_handlers
from api import provide_api_data
from display import Display
from utils import log


config = {}
modules = []


async def update_clock(options: rgbmatrix.RGBMatrixOptions, quit: asyncio.Future) -> None:
    ...


async def main() -> [str, int]:
    '''
    Load matrix config and launch all tasks
    '''
    # Apply matrix-specific configuration options from config module
    options = rgbmatrix.RGBMatrixOptions()
    options_prefix = 'matrix_'
    for key, value in vars(config).items():
        try:
            if key.startswith(options_prefix):
                setattr(options, key[len(options_prefix):], value)
        except AttributeError:
            log(f'Ignoring: {key} = {value}')

    # Run all tasks within the context of the aiohttp session
    async with aiohttp.ClientSession() as http:
        # Tasks can call quit.set_result(result) to quit
        quit = asyncio.Future()
        asyncio.create_task(provide_clock_modules(http, modules))
        asyncio.create_task(update_clock(options, quit))
        await quit


if __name__ == '__main__':
    asyncio.run(main())
