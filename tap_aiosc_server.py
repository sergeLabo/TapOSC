#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Envoie et reçoit pour TapOSC.
'''

import asyncio
import aiosc

'''
loop = asyncio.get_event_loop()

loop.run_until_complete(
    aiosc.send(('127.0.0.1', 8000), '/hello', 'world')
                        )
'''

def protocol_factory():
    osc = aiosc.OSCProtocol({
        '//*': lambda addr, path, *args: print(addr, path, args)
    })
    return osc

loop = asyncio.get_event_loop()
coro = loop.create_datagram_endpoint(protocol_factory,
                                     local_addr=('127.0.0.1', 9000))
transport, protocol = loop.run_until_complete(coro)

loop.run_forever()
