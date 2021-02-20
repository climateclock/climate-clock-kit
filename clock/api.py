
from __future__ import annotations

import asyncio
import json

import aiohttp
from schema import And, Optional, Or, Schema, Use
from utils import log


API_DEVICE = 'portable_pi'
API_ENDPOINT = f'https://api.climateclock.world/v1/clock?device={API_DEVICE}'
API_CACHE = 'api_cache.json'
API_FROZEN = 'api_frozen.json'

INTERVAL_MINIMUM_SECONDS = 300


# Validation schemata for API data

Misc = {Optional(object): object}
Number = Or(float, int)

api_schema = Schema({
    'status': 'success',
    'data': {
        **Misc,
        'config': {
            **Misc,
            'device': API_DEVICE,
            'modules': [str],
        },
        'modules': {str: dict},
    },
})

_module_base = {
    **Misc,
    'type': str,
    'flavor': Or('lifeline', 'deadline', 'neutral'),
    'description': str,
    'update_interval_seconds': Number,
    Optional('label'): str,
    Optional('label_short'): str,
    Optional('lang'): str,
}

_module_value_base = {
    **_module_base,
    'type': 'value',
    'initial': Number,
    'timestamp': str,
    'units': str,
}

module_schema = Schema(Or(
    { 
        **_module_base,
        'type': 'timer',
        'timestamp': str,
    }, 
    { 
        **_module_base,
        'type': 'newsfeed',
        'newsfeed': [{
            **Misc,
            'date': str,
            'headline': str,
            'headline_original': str,
            'source': str,
            'link': str,
            Optional('summary'): str,
        }],
    }, 
    Or(
        {
            **_module_value_base,
            'growth': 'linear',
            'rate': Number,
        },
        {
            **_module_value_base,
            'growth': 'exponential',    # TODO: Not yet in the spec
            'exponent': Number,
        },
    ),
))


def get_valid_modules(api_data: dict) -> list:
    '''
    Given raw API data, return any and all valid, supported clock modules
    based on the `api_schema` and `module_schema` schemas.
    '''
    if not api_schema.is_valid(api_data):
        return []

    return [module_schema.validate(module) for name, module in api_data['data']['modules'].items()
            if name in api_data['data']['config']['modules'] and module_schema.is_valid(module)]


def load_cache(filenames: list[str]=[API_CACHE, API_FROZEN]) -> dict:
    '''
    Attempt to load API cache, falling back to frozen API data
    '''
    for filename in filenames:
        try:
            with open(filename) as f:
                api_data = json.load(f) or {}
                log(f'Loaded: {filename}')
                return api_data
        except Exception as e: log(e)


def save_cache(api_data: dict, filename: str=API_CACHE) -> None:
    '''
    Attempt to save cache and log failure
    '''
    try:
        with open(filename, 'w') as f:
            json.dump(api_data, f)
            log(f'Saved: {filename}')
    except Exception as e: log(e)


async def provide_clock_modules(http: aiohttp.ClientSession, modules: list) -> None:
    '''
    Periodically fetch API data with the `http` client and provide clock 
    modules to the `modules` list.
    '''
    timeout = aiohttp.ClientTimeout(total=5)
    modules[:] = get_valid_modules(load_cache())

    while True:
        try:
            async with http.get(API_ENDPOINT, timeout=timeout) as r:
                api_data = await r.json()
                if (m := get_valid_modules(api_data)):
                    modules[:] = m
                    log(f'Received: {API_ENDPOINT}')
                    save_cache(api_data)
        except Exception as e: ...

        # Sleep based on whichever module has the shortest 
        # update_interval_seconds, or at least INTERVAL_MINIMUM_SECONDS
        await asyncio.sleep(max(
            INTERVAL_MINIMUM_SECONDS,
            min((m['update_interval_seconds'] for m in modules), default=0)
        ))


__all__ = [
    'API_ENDPOINT',
    'provide_clock_modules',
]
