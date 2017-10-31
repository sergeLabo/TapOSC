#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import threading
from OSC3 import OSCClient, OSCMessage, OSCServer



def create_server(svr_addr):
    """Create a thread with OSC server."""

    server = OSCServer(svr_addr)
    server.addMsgHandler("/info", info_handler)
    t_server = threading.Thread(target=server.serve_forever)
    t_server.start()

def info_handler(addr, tags, stuff, source):

    print(addr, tags, stuff, source)
    if addr == '/info':
        print("Message reçu: {} {} {} {}".format(addr, tags, stuff, source))


def main():
    svr_addr = "127.0.0.1", 8080
    create_server(svr_addr)

main()
