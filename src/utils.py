import asyncio
import logging

from pytoniq import OverlayNode
from pytoniq.adnl import OverlayTransport, DhtClient
from pytoniq_core.crypto.ciphers import Server


logger = logging.getLogger(__name__)


async def get_more_clients(overlay: OverlayTransport, dht_client: DhtClient, max_peers: int = 20):
    clients = []
    for _, peer in list(overlay.peers.items()):
        if len(overlay.peers) > max_peers:
            return clients
        logger.info(f'getting nodes from peer {peer.get_key_id().hex()}')
        if not peer.connected:
            logger.info(f'peer {peer.get_key_id().hex()} is already not connected')
            continue
        resp = await overlay.get_random_peers(peer)
        logger.info(f"got {len(resp[0]['nodes'])} from peer")
        for node in resp[0]['nodes']:
            pub_k = bytes.fromhex(node['id']['key'])
            adnl_addr = Server('', 0, pub_key=pub_k).get_key_id()
            if adnl_addr not in overlay.peers:
                new_client = await dht_client.get_overlay_node(node, overlay)
                if new_client is not None:
                    clients.append(new_client)
    for new_client in clients:
        if len(overlay.peers) > max_peers:
            return []
        try:
            if new_client is not None:
                await new_client.connect()
                logger.info('connected')
        except asyncio.TimeoutError:
            logger.info('not connected')
            continue
    return clients


#### some good peers ####
host1 = '65.108.45.90'
port1 = 23649
pub_k1 = 'K09zRUv1K3fT3bNwGOg8zBs6DIc6h4735+FF14ZrMA8='

host2 = '65.21.229.49'
port2 = 40657
pub_k2 = 'bCx+04+yUrIQ+3vUzaWWUegU6iWDfuGLEH7vAG6bvHw='

testnet_host1 = '94.237.45.107'
testnet_port1 = 42123
testnet_pub1 = 'vdreSex+SeTx5JWJDMUfQDxc3A+CzP7k7G5t1NB3k0w='


testnet_host2 = '69.67.151.218'
testnet_port2 = 54265
testnet_pub2 = 'aatc1iS1xDcYH700mi0GhIxPxd9UPopQQdh46676yQc='


def get_first_good_peers(overlay: OverlayTransport):
    client = OverlayNode(
        peer_host=host1,
        peer_port=port1,
        peer_pub_key=pub_k1,
        transport=overlay
    )

    client2 = OverlayNode(
        peer_host=host2,
        peer_port=port2,
        peer_pub_key=pub_k2,
        transport=overlay
    )

    testnet_client = OverlayNode(
        peer_host=testnet_host1,
        peer_port=testnet_port1,
        peer_pub_key=testnet_pub1,
        transport=overlay
    )

    testnet_client2 = OverlayNode(
        peer_host=testnet_host2,
        peer_port=testnet_port2,
        peer_pub_key=testnet_pub2,
        transport=overlay
    )

    return [client, client2]
