import datetime
import logging
import time

from pytoniq_core import MessageAny, Cell


messages = {}


# this function can be async as well
def process_external_message(data: dict):
    message_cell = Cell.one_from_boc(data['data']['message']['data'])
    msg = MessageAny.deserialize(message_cell.begin_parse())
    if message_cell.hash not in messages:
        print('EXTERNAL', datetime.datetime.now(), f'https://tonviewer.com/{msg.info.dest.to_str()}')
        messages[message_cell.hash] = time.time()

    # clear cache

    for m, t in list(messages.items()):
        if t + 300 < time.time():
            messages.pop(m)
