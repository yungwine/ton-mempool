# TON-mempool

## Very experimental version

TON Blockchain MemPool listener is a simple tool that runs a websocket server which allows you to
* send [external messages](https://docs.ton.org/develop/smart-contracts/guidelines/external-messages)
directly to the [overlay](https://docs.ton.org/learn/networking/overlay-subnetworks)
* listen to external messages coming to the blockchain
* listen to new blocks before their application (will be implemented soon).

## Installation

You can run either in Docker or locally.

### Env

* WS_PORT - port for WebSocket server, must be provided for using in Docker
* NETWORK - network name (`mainnet`, `testnet`, or `ownnet`), default is `mainnet`
* ZERO_STATE_FILE_HASH - zero state file hash hex, must be provided for using with `ownnet`
* WORKCHAIN - workchain id, default is `0`

### Run in Docker

Clone the repository and configure `.env` file.

Example:

```
#.env
WS_PORT=8765
WORKCHAIN=0
NETWORK=testnet
```

After that build and run docker-compose

```commandline
$ docker-compose up --build -d
```

### Run locally

Export `env` variables and install requirements

```commandline
$ pip install -r requirements.txt
```

After that run the server

```commandline
$ python3 -m src
```

## Usage

After you ran the server, wait 15 seconds, and then you will be able to connect to it using any WebSocket client ([python example](examples/listener.py)).
Then you need to wait until the `Overlay Client` find the peers and connect to them. This process can take from 10 seconds to a few minutes.

### Methods

* `{'type': 'get_peers_amount'}` - get peers amount server knows. 
* `{'type': 'subscribe', 'data': 'external'}` - subscribe to external messages. 
* `{'type': 'send_external', 'data': hex_boc}` - send external message to the network.

### Receive messages

* `{"type": "get_peers_amount", "answer": {"amount": peers_amount}}` - amount of peers.
* `{'type': 'external', 'data': hex_boc}` - new external message found in mempool.

### What can I do with messages I receive?

The server sends you `external messages` as bocs. After deserializing you will get a Cell serialized as `Message Any` TL-b scheme.
This structure contains message info and body. Most likely you want to know what events will be triggered by this message, 
so you can emulate it locally using [pytvm](https://github.com/yungwine/pytvm) or some APIs (find examples in [process_external.py](examples/process_external.py)).

### Examples

Find Python examples in the [examples](examples/) folder. 

## Donation

TON wallet: `EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG`
