import asyncio
import logging
import os

from pytoniq import OverlayNode

from .utils import get_more_clients, get_first_good_peers
from .handlers import process_get_capabilities_request, process_get_random_peers_request
from .processer import process_external_message

from pytoniq.adnl import OverlayTransport, DhtClient, AdnlTransport
from pytoniq_core.crypto.ciphers import Client

logger = logging.getLogger(__name__)


async def start_up(

):
    logger.info('Starting up!')

    overlay.set_query_handler(type_='overlay.getRandomPeers', handler=lambda i: process_get_random_peers_request(i, overlay))
    overlay.set_query_handler(type_='tonNode.getCapabilities', handler=lambda i: process_get_capabilities_request(i))
    overlay.set_custom_message_handler(type_='overlay.broadcast', handler=lambda i: process_external_message(i))

    logger.info('Starting ADNL transport...')
    await adnl.start()
    logger.info('ADNL transport is launched ...')

    logger.info('Starting Overlay transport...')
    await overlay.start()
    logger.info('Overlay transport is launched ...')
    dht = DhtClient.from_mainnet_config(adnl_transport=adnl)

    while True:
        if len(overlay.peers) == 0:
            logger.info('Getting first peers! This may take some time')
            nodes = await dht.get_overlay_nodes(
                overlay_id=OverlayTransport.get_mainnet_overlay_id(
                    workchain=0,
                    shard=-2**63
                ),
                overlay_transport=overlay
            )
            for node in nodes + get_first_good_peers(overlay):
                node: OverlayNode
                if node is None:
                    continue
                try:
                    await node.connect()
                    logger.info(f'Connected to peer {node.key_id.hex()}')
                except asyncio.TimeoutError:
                    continue
            logger.info(f'Got {len(overlay.peers)} first peers')
        else:
            try:
                logger.info(f'Trying to get more peers. Currently has {len(overlay.peers)}')
                clients = await get_more_clients(overlay, dht, max_peers=50)
                logger.info(f'Got {len(clients)} more peers')
            except Exception as e:
                logger.warning(f'failed get more peers: {type(e)}: {str(e)}')
        # await dht.close()
        await asyncio.sleep(10)


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
    )

    asyncio.run(start_up())
