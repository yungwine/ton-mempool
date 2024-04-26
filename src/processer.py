import hashlib
import json

import websockets
from pytoniq import LiteBalancer
import time
from .ws import externals, blocks


messages = {}
client = LiteBalancer.from_mainnet_config(2)
counter = 0


async def broadcast_external(message):
    for websocket in externals.copy():
        try:
            await websocket.send(json.dumps({'type': 'external', 'data': message.hex()}).encode())
        except websockets.ConnectionClosed:
            pass


async def broadcast_block(message):
    for websocket in blocks.copy():
        try:
            await websocket.send(json.dumps({'type': 'block', 'data': message}).encode())
        except websockets.ConnectionClosed:
            pass


async def process_external_message(data: dict, *args, **kwargs):
    global counter
    counter += 1
    if not counter % 500:
        print(f'GOT {counter} msgs')

    await broadcast_external(message=data['message']['data'])

    messages[hashlib.sha256(data['message']['data'])] = time.time()

    # clear cache

    for m, t in list(messages.items()):
        if t + 60 < time.time():
            messages.pop(m)

    return data


async def process_block(data: dict, *args, **kwargs):
    if data['@type'] == 'tonNode.newShardBlockBroadcast':
        await broadcast_block({'id': data['block']['block'], 'data': data['block']['data'].hex()})
    elif data['@type'] == 'tonNode.blockBroadcast':
        await broadcast_block({'id': data['id'], 'data': data['data'].hex()})
