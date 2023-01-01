#!/usr/bin/env python
import argparse
import asyncio

import win32api
from websockets import connect

POLLING_INTERVAL = 0.001

async def main():
    parser = argparse.ArgumentParser(prog = "Host Jitter")

    parser.add_argument('--host', type=str, required=True)
    parser.add_argument('--port', type=int, default=8765)

    args = parser.parse_args()

    url = f'ws://{args.host}:{args.port}'

    async with connect(url) as ws:
        print(f'Connected to server on {url}')

        state_left = win32api.GetKeyState(0x01)  # Left button down = 0 or 1. Button up = -127 or -128
        while True:
            await asyncio.sleep(POLLING_INTERVAL)

            a = win32api.GetKeyState(0x01)

            if a != state_left:  # Button state changed
                state_left = a
                if a < 0:
                    print('Pressed')
                    await ws.send('start')
                else:
                    print('Released')
                    await ws.send('end')


asyncio.run(main())
