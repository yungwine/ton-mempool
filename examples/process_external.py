from pytoniq_core.tlb import MessageAny
from pytoniq_core import Slice
from pytoniq import LiteBalancer, Contract
from pytvm.transaction_emulator import TraceEmulator, TransactionEmulator
from pytvm.tvm_emulator import TvmEmulator

client = LiteBalancer.from_mainnet_config(trust_level=2)
emulator = TransactionEmulator()


def process_external_deserialize(message_boc):
    msg = MessageAny.deserialize(Slice.one_from_boc(message_boc))
    to_address = msg.info.dest  # address external goes to
    body = msg.body  # external body
    print('got external on ', f'https://tonviewer.com/{to_address.to_str()}')


async def emulate_external_trace(message_boc):
    if not client.inited:
        await client.start_up()
    msg = MessageAny.deserialize(Slice.one_from_boc(message_boc))
    trace_emulator = TraceEmulator(client, emulator)
    result = await trace_emulator.emulate(msg)
    if not result['transaction']:
        print('failed to emulate: ', result)
    tr = result['transaction']  # Transaction result
    children = result['children']  # list of children transactions

    # check that tr will not fail:
    if tr.description.compute_ph.type_ != 'skipped' and tr.description.compute_ph.exit_code != 0:
        print('Transaction failed')

    if children:
        print('children 1: ', children[0])


async def check_contract_type(message_boc):
    if not client.inited:
        await client.start_up()
    msg = MessageAny.deserialize(Slice.one_from_boc(message_boc))

    if msg.init is not None:  # probably contract is not deployed, but need additional check for state in blockchain
        code = msg.init.code
        data = msg.init.data
    else:
        contract = await Contract.from_address(client, msg.info.dest)
        code = contract.code
        data = contract.data

    tvm = TvmEmulator(code, data)
    result = tvm.run_get_method('seqno', [])  # probably wallet
    if not result['success']:
        print('failed to run seqno')
    else:
        print('seqno is', result['stack'][0])
