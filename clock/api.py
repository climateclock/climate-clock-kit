
from __future__ import annotations

import asyncio
import json

import aiohttp
from schema import And, Optional, Or, Schema, Use
from utils import log


API_ENDPOINT = 'https://api.climateclock.world/v1/clock'
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
            'device': str,
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


def update_valid_api_data(api_data: dict, config: dict, modules: list) -> [None, True]:
    '''
    Update mutable `config` dict and `modules` list with valid API data and
    return True when this has taken place.
    '''
    if api_schema.is_valid(api_data):
        config.clear()
        config.update(api_data['data']['config'])

        modules[:] = [module_schema.validate(module)
                      for name, module in api_data['data']['modules'].items()
                      if name in config['modules'] and module_schema.is_valid(module)]
        return True


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


async def provide_api_data(http: aiohttp.ClientSession, device_name: str, config: dict, modules: list) -> None:
    '''
    Periodically fetch API data with the `http` client and provide API data
    to the `config` dict and `modules` list.
    '''
    endpoint = f'{API_ENDPOINT}?device={device_name}'
    timeout = aiohttp.ClientTimeout(total=5)

    update_valid_api_data(load_cache(), config, modules)

    while True:
        try:
            async with http.get(endpoint, timeout=timeout) as r:
                api_data = await r.json()
                if update_valid_api_data(api_data, config, modules):
                    log(f'Received: {endpoint}')
                    save_cache(api_data)
        except Exception as e:
            log(f'Unavailable: {endpoint}')

        # Sleep based on whichever module has the shortest 
        # update_interval_seconds, or at least INTERVAL_MINIMUM_SECONDS
        await asyncio.sleep(max(
            INTERVAL_MINIMUM_SECONDS,
            min((m['update_interval_seconds'] for m in modules), default=0)
        ))


__all__ = [
    'API_ENDPOINT',
    'provide_api_data',
]
