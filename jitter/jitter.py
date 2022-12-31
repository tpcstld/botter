#!/usr/bin/env python3
import argparse
import asyncio
from websockets import serve

WAIT_TIME = 0.001
RADIUS = 2

async def do_once(fd, stuff):
    await asyncio.sleep(WAIT_TIME)
    fd.write(stuff)
    fd.flush()

def value_to_byte(value):
    if value < 0:
        value = 256 + value

    return value.to_bytes(1, 'big')

assert value_to_byte(-1) == b'\xff'


async def move_mouse(fd, x, y):
    await do_once(fd, b'\x00' + value_to_byte(x) + value_to_byte(y))


async def do_jitter():
    while True:
        with open('/dev/hidg0', 'rb+') as fd:
            await move_mouse(fd, RADIUS, 0)
            await move_mouse(fd, 0, RADIUS)
            await move_mouse(fd, -RADIUS, 0)
            await move_mouse(fd, 0, -RADIUS)


task = None


def process_message(message):
    global task
    print(message)

    if message == 'start':
        task = asyncio.Task(do_jitter())
        return

    if message == 'end' and task is not None:
        task.cancel()
        task = None
        return


async def handle_request(websocket):
    async for message in websocket:
        process_message(message)


async def main():
    parser = argparse.ArgumentParser(
        prog = "Jitter",
        description = "Jitters the mouse in Apex",
    )

    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--standalone', type=bool, default=False)

    args = parser.parse_args()

    if args.standalone is True:
        print('Always jittering.')
        await do_jitter()
    else:
        async with serve(handle_request, host=None, port=args.port):
            print(f'Spun up service on port {args.port}.')
            await asyncio.Future()

asyncio.run(main())
