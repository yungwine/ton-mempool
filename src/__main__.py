import asyncio
import logging
import os

from .ws import run_websocket
from .processer import process_external_message

from pytoniq.adnl import OverlayTransport, DhtClient, AdnlTransport
from pytoniq.adnl.overlay import ShardOverlay, OverlayManager
from pytoniq_core.crypto.ciphers import Client

logger = logging.getLogger(__name__)


async def start_up(

):
    logger.info('Starting up!')

    logger.info('Starting ADNL transport...')
    await adnl.start()
    logger.info('ADNL transport is launched ...')

    logger.info('Starting Overlay transport...')
    await overlay.start()
    logger.info('Overlay transport is launched ...')
    dht = DhtClient.from_mainnet_config(adnl_transport=adnl)
    manager = OverlayManager(overlay, dht, max_peers=30)
    await manager.start()
    await asyncio.sleep(15)
    shard_node = ShardOverlay(manager, external_messages_handler=process_external_message, shard_blocks_handler=lambda i, j: print(i))
    # await asyncio.sleep(150)
    logger.info('Starting websocket.')
    await run_websocket(shard_node)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    files = os.listdir('.')
    if 'key.txt' not in files:
        with open('key.txt', 'wb') as f:
            f.write(Client.generate_ed25519_private_key())
    with open('key.txt', 'rb') as f:
        key = f.read()

    adnl = AdnlTransport(timeout=5)

    overlay = OverlayTransport(
        private_key=key,
        local_address=('0.0.0.0', 12000),
        overlay_id=OverlayTransport.get_mainnet_overlay_id(
            workchain=0,
        ),
        timeout=10,
        allow_fec=True
    )

    asyncio.run(start_up())
