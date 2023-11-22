from pytoniq.adnl.overlay import OverlayTransport


def process_get_random_peers_request(_, overlay_client: OverlayTransport):
    peers = [
        overlay_client.get_signed_myself()
    ]
    return {
        '@type': 'overlay.nodes',
        'nodes': peers
    }


def process_get_capabilities_request(_):
    return {
        '@type': 'tonNode.capabilities',
        'version': 2,
        'capabilities': 1,
    }
