import hashlib

import websockets
from pytoniq import LiteBalancer
import time
from .ws import connected


messages = {}
client = LiteBalancer.from_mainnet_config(2)
counter = 0


async def broadcast(message):
    for websocket in connected.copy():
        try:
            await websocket.send(message)
        except websockets.ConnectionClosed:
            pass


# this function can be sync as well
async def process_external_message(data: dict, *args, **kwargs):
    global counter
    counter += 1
    if not counter % 500:
        print(f'GOT {counter} msgs')

    await broadcast(message=data['message']['data'])

    messages[hashlib.sha256(data['message']['data'])] = time.time()

    # clear cache

    for m, t in list(messages.items()):
        if t + 300 < time.time():
            messages.pop(m)

    return data
