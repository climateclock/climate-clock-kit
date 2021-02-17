
import asyncio
import json

import aiohttp
from schema import And, Optional, Or, Schema, Use
from utils import log


API_DEVICE = 'portable_pi'
API_ENDPOINT = f'https://api.climateclock.world/v1/clock?device={API_DEVICE}'
API_FROZEN = 'api_frozen.json'

INTERVAL_MINIMUM_SECONDS = 300


# Validation schema for API data

Misc = {Optional(object): object}
Number = Or(float, int)

api_data = Schema({
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
    'flavor': Or('lifeline', 'deadline'),
    'description': str,
    'update_interval_seconds': Number,
    Optional('label'): str,
    Optional('label_short'): str,
    Optional('lang'): str,
}

module_data = Schema(Or(
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
    Or({ 
        **_module_base,
        'type': 'value',
        'initial': Number,
        'timestamp': str,
        'growth': 'linear',
        'units': str,
        'rate': Number,
    },
    {
        **_module_base,
        'type': 'value',
        'initial': Number,
        'timestamp': str,
        'growth': 'exponential',    # TODO: Not yet in the spec
        'units': str,
        'exponent': Number,
    }),
))


def get_valid_modules(d):
    '''
    Given raw API data, return any and all valid, supported clock modules
    '''
    if not api_data.is_valid(d):
        return []

    return [module_data.validate(module) for name, module in d['data']['modules'].items()
            if name in d['data']['config']['modules'] and module_data.is_valid(module)]


async def provide_clock_modules(session: aiohttp.ClientSession, modules: list):
    '''
    Periodically fetch API data and provide clock modules to the `modules`
    list. 
    '''
    timeout = aiohttp.ClientTimeout(total=5)

    # Load known good frozen API data from disk
    with open(API_FROZEN) as f:
        data = json.load(f)['data']

    while True:
        try:
            log('--> Fetching API data')
            async with session.get(API_ENDPOINT, timeout=timeout) as r:
                if (m := get_valid_modules(await r.json())):
                    modules.clear()
                    modules.extend(m)
                    # TODO: Save good api snapshot

                # TODO: Else????????????

        #except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        except Exception as e:
            # TODO: Get good API snapshot
            log('--> Falling back to snapshot/frozen', e)

        # Sleep based on whichever module has the shortest 
        # update_interval_seconds, or at least INTERVAL_MINIMUM_SECONDS
        await asyncio.sleep(max(
            INTERVAL_MINIMUM_SECONDS,
            min(m['update_interval_seconds'] for m in modules)
        ))

