import asyncio
import json
import os

import websockets.exceptions
from pytoniq.adnl.overlay import ShardOverlay
from websockets.server import serve


externals = set()


async def handler(websocket):
    while True:
        try:
            message = await websocket.recv()
        except websockets.exceptions.ConnectionClosedOK:
            externals.discard(websocket)
            break
        message = json.loads(message)
        if message['type'] == 'subscribe':
            if message['data'] == 'external':
                externals.add(websocket)
            else:
                pass  # todo blocks
        elif message['type'] == 'send_external':
            await shard_node.send_external_message(bytes.fromhex(message['data']))
        elif message['type'] == 'get_peers_amount':
            await websocket.send(
                json.dumps({'type': 'get_peers_amount', 'answer': {'amount': len(shard_node._overlay.peers)}}).encode()
            )


async def run_websocket(shard: ShardOverlay):
    global shard_node
    shard_node = shard
    async with serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever
