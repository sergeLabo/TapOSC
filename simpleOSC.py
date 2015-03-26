#! /usr/bin/env python3
# -*- coding: utf-8 -*-

''' Basic module to ease the use of pyOSC module:

https://gitorious.org/pyosc/devel/source/6aaf78b0c1e89942a9c5b1952266791b7ae16012:
or
http://goo.gl/Mxpyy6

Copy OSC.py in the your simpleOSC.py directory
...
Python 3 Version
Python 3 Version
Python 3 Version
...

This is meant to be used by students or newies that are starting to experiment
with OSC. If you are an advanced user you probably want to bypass this module
and use directly pyOSC, we have some examples of very simple use in our website.
Check the pyOSC website for more documentation.

License : LGPL

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

Modification Labomedia March 2015:
    - Convert with 2to3
    -

'''

import OSC

basic_client = None
basic_server = None
st = None

def printing_handler(addr, tags, data, source):
    print("---")
    print("received new osc msg from : {}".format(getUrlStr(source)))
    print("with addr : {}".format(addr))
    print("typetags : {}".format(tags))
    print("the actual data is : {}".format(data))
    print("---")

def initOSCClient(ip='127.0.0.1', port=8000):
    global basic_client
    basic_client = OSC.OSCClient()
    return basic_client

def initOSCServer(ip='127.0.0.1', port=9000, mode=0):
    '''Mode 0 for basic server, 1 for threading server, 2 for forking server.
    '''
    global basic_server, st

    if mode == 0 :
        basic_server = OSC.OSCServer( (ip ,port) ) # basic
    elif mode == 1 :
        basic_server = OSC.ThreadingOSCServer( (ip ,port) ) # threading
    elif mode == 2 :
        basic_server = OSC.ForkingOSCServer( (ip ,port) ) # forking

    basic_server.addDefaultHandlers()
    st = threading.Thread( target=basic_server.serve_forever )
    st.start()

def setOSCHandler(address="/print", hd=printing_handler) :
    basic_server.addMsgHandler(address, hd) # adding our function

def closeOSC():
    if basic_client:
        basic_client.close()
    if basic_server:
        basic_server.close()
    if st:
        st.join()

def reportOSCHandlers() :
    print("Registered Callback-functions are :")
    for addr in basic_server.getOSCAddressSpace():
        print(addr)

def sendOSCMsg(clt, address='/print', data=[]):
    m = OSC.OSCMessage()
    m.setAddress(address)
    for d in data :
        m.append(d)
    clt.send(m)

def sendtoOSCMsg(clt, address='/print', data=[], ip='127.0.0.1', port=8000, timeout=0.05):
    m = OSC.OSCMessage()
    m.setAddress(address)
    for d in data :
        m.append(d)
    clt.sendto(m, (ip, port))

def createOSCBundle() :
    # just for api consistency
    return OSC.OSCBundle()

def sendOSCBundle(b):
    basic_client.send(b)

def createOSCMsg(address='/print', data=[]) :
    m = OSC.OSCMessage()
    m.setAddress(address)
    for d in data :
        m.append(d)
    return m

if __name__ == '__main__':
    from time import sleep
    ip = "127.0.0.1"
    sport = 8000

    initOSCClient(ip, sport)
    # Some thing must listen the port, for example pd
    while True:
        sleep(1)
        msg = "toto"
        sendtoOSCMsg("/1/xy", [msg], ip=ip, port=sport, timeout=0.05)
        print(msg)
