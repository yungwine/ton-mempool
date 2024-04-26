import asyncio
import logging
import os

from .ws import run_websocket
from .processer import process_external_message, process_block

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
    shard_node = ShardOverlay(
        manager,
        external_messages_handler=process_external_message,
        shard_blocks_handler=process_block,
        blocks_handler=process_block
    )
    # await asyncio.sleep(150)
    logger.info('Starting websocket.')
    await run_websocket(shard_node)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    WORKCHAIN = int(os.getenv('WORKCHAIN', 0))
    NETWORK = os.getenv('NETWORK', 'mainnet')
    if NETWORK == 'mainnet':
        overlay_id = OverlayTransport.get_mainnet_overlay_id(workchain=WORKCHAIN)
    elif NETWORK == 'testnet':
        overlay_id = OverlayTransport.get_testnet_overlay_id(workchain=WORKCHAIN)
    else:
        ZERO_STATE_FILE_HASH = os.getenv('ZERO_STATE_FILE_HASH')
        if ZERO_STATE_FILE_HASH is None:
            raise ValueError('ZERO_STATE_FILE_HASH is not set')
        overlay_id = OverlayTransport.get_overlay_id(ZERO_STATE_FILE_HASH, workchain=WORKCHAIN)

    print('Overlay ID:', overlay_id)

    files = os.listdir('.')
    if 'key.txt' not in files:
        with open('key.txt', 'wb') as f:
            f.write(Client.generate_ed25519_private_key())
    with open('key.txt', 'rb') as f:
        key = f.read()

    adnl = AdnlTransport(timeout=5)

    overlay = OverlayTransport(
        private_key=key,
        overlay_id=overlay_id,
        timeout=10,
        allow_fec=True
    )

    asyncio.run(start_up())
