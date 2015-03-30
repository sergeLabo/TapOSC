#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
TapOSC est une Application Android made with kivy

Copyright (C) Labomedia March 2015

    This file is part of TapOSC.

    TapOSC is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    TapOSC is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TapOSC.  If not, see <http://www.gnu.org/licenses/>. 2
'''

__version__ = '0.32'

'''
version
0.32 modif options ne reset pas config, quit bug, thread non stoppé
'''

import sys, platform
from time import sleep
import threading

import kivy
kivy.require('1.8.0')
from kivy.app import App
from kivy.config import Config
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, ObjectProperty
from kivy.core.window import Window

from OSC import OSCClient, OSCMessage, OSCBundle
from jnius import autoclass

class AndroidOnly(object):
    def __init__(self, address):
        self.address = address
        self.acc = 0
        self.dpi = 0
        self.Hardware = None
        self.platform = sys.platform
        print("Platform = {}".format(self.platform))
        self.loop = 1
        # Osc Client only for this thread
        self.android_clt = OSCClient()

        if 'linux3' in self.platform:
            try:
                self.Hardware = autoclass('org.renpy.android.Hardware')
                self.Hardware.accelerometerEnable(True)
                acc_thread = threading.Thread(target=self.send_acc)
                acc_thread.start()
            except:
                print("Pb with AndroidOnly")
        print("AndroidOnly init ok")

    def send_acc(self):
        while self.loop:
            self.acc = self.Hardware.accelerometerReading()
            msg = OSCMessage('/1/acc')
            msg.append(self.acc)
            self.android_clt.sendto(msg, self.address)
            # 60 fps: 0.015
            sleep(1)  #(0.015)

    def stop_loop(self):
        self.loop = 0

class MainScreen(Screen):
    pass

class Screen1(Screen):
    def __init__ (self,**kwargs):
        super(Screen1, self).__init__(**kwargs)
        # window
        self.ws = Window.size
        # osc
        config = TapOSCApp.get_running_app().config
        host = config.get('network', 'host')
        sport = int(config.get('network', 'send_port'))
        self.address = host, sport
        self.clt = OSCClient()
        AndroidOnly(self.address)
        print("Screen1 init ok")

    def on_touch_move(self, touch):
        xy_abs = int(touch.pos[0]), int(touch.pos[1])
        #print("Mouse Absolute", xy_abs)
        x_rel = float(xy_abs[0]) / self.ws[0]
        y_rel = float(xy_abs[1]) / self.ws[1]
        print("Mouse Relative Position", x_rel, y_rel)

        # OSC
        bundle = OSCBundle()

        msgx = OSCMessage('/1/xy/x')
        msgx.append(x_rel)
        bundle.append(msgx)

        msgy = OSCMessage('/1/xy/y')
        msgy.append(y_rel)
        bundle.append(msgy)

        self.clt.sendto(bundle, self.address)

class Screen2(Screen):
    def __init__ (self,**kwargs):
        super(Screen2, self).__init__(**kwargs)
        # osc
        config = TapOSCApp.get_running_app().config
        host = config.get('network', 'host')
        sport = int(config.get('network', 'send_port'))
        self.address = host, sport
        self.clt = OSCClient()
        print("Screen2 init ok")

    def do_button_on(self, iD, instance):
        print("button", iD, "on")
        # OSC envoi de iD, 1
        msg = OSCMessage(iD)
        msg.append(1)
        self.clt.sendto(msg, self.address)

    def do_button_off(self, iD, instance):
        print("button", iD, "off")
        # OSC envoi de iD, 0
        msg = OSCMessage(iD)
        msg.append(0)
        self.clt.sendto(msg, self.address)

    def do_slider(self, iD, instance, value):
        print("slider", iD, value)
        # OSC envoi de slider value
        msg = OSCMessage(iD)
        msg.append(value)
        self.clt.sendto(msg, self.address)

class Screen3(Screen):
    def __init__ (self,**kwargs):
        super(Screen3, self).__init__(**kwargs)
        self.ws = Window.size
        # osc
        config = TapOSCApp.get_running_app().config
        host = config.get('network', 'host')
        sport = int(config.get('network', 'send_port'))
        self.address = host, sport
        self.clt = OSCClient()
        print("Screen3 init ok")

    def on_touch_move(self, touch):
        xy_abs = int(touch.pos[0]), int(touch.pos[1])
        #print("Mouse Absolute", xy_abs)
        x_rel = float(xy_abs[0]) / self.ws[0]
        y_rel = float(xy_abs[1]) / self.ws[1]
        print("Mouse Relative Position", x_rel, y_rel)

        # OSC
        bundle = OSCBundle()

        msgx = OSCMessage('/3/xy/x')
        msgx.append(x_rel)
        bundle.append(msgx)

        msgy = OSCMessage('/3/xy/y')
        msgy.append(y_rel)
        bundle.append(msgy)

        self.clt.sendto(bundle, self.address)

    def do_slider(self, iD, instance, value):
        print("slider", iD, value)
        # OSC envoi de slider value
        msg = OSCMessage(iD)
        msg.append(value)
        self.clt.sendto(msg, self.address)

class Screen4(Screen):
    blanche = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(Screen4, self).__init__(**kwargs)
        for x in xrange(16):
            btn = TapOscButton(index=x)
            btn.bind(state=self.on_button_state)
            self.blanche.add_widget(btn)
        # osc
        config = TapOSCApp.get_running_app().config
        host = config.get('network', 'host')
        sport = int(config.get('network', 'send_port'))
        self.address = host, sport
        self.clt = OSCClient()
        print("Screen4 init ok")

    def on_button_state(self, instance, value):
        index = instance.index
        if value == 'down':
            value = 1
        else:
            value = 0

        # OSC
        msg = OSCMessage('/4/b/' + str(index))
        msg.append(value)
        self.clt.sendto(msg, self.address)

class TapOscButton(Button):
    index = NumericProperty(0)

class TapOscSlider(Slider):
    index = NumericProperty(0)

SCREENS = { 0: (MainScreen,       "Menu"),
            1: (Screen1,          "Ecran 1"),
            2: (Screen2,          "Ecran 2"),
            3: (Screen3,          "Ecran 3"),
            4: (Screen4,          "Ecran 4")}

class TapOSCApp(App):
    '''app est le parent de cette classe dans kv.'''
    def build(self):
        '''Exécuté en premier après run()'''
        # Création des écrans
        self.screen_manager = ScreenManager()
        for i in range(len(SCREENS)):
            self.screen_manager.add_widget(SCREENS[i][0](name=SCREENS[i][1]))
        return self.screen_manager

    def on_start(self):
        '''Exécuté après build()'''
        pass

    def build_config(self, config):
        '''Si le fichier *.ini n'existe pas,
        il est crée avec ces valeurs par défaut.
        Si il manque seulement des lignes, il ne fait rien !
        '''
        config.setdefaults('network',
            {
            'host': '192.168.0.103',
            'receive_port': '9000',
            'send_port': '8000'
            })

        config.setdefaults('kivy',
            {
            'log_level': 'debug',
            'log_name': 'tapOSC_%y-%m-%d_%_.txt',
            'log_dir': '/sdcard',
            'log_enable': '1'
            })

    def build_settings(self, settings):
        '''Construit l'interface de l'écran Options,
        appelé par app.open_settings() dans .kv
        '''
        data = '''[
                    { "type": "title", "title": "Network configuration" },

                    { "type": "string", "title": "Host",
                      "desc": "Ip address to use",
                      "section": "network", "key": "host" },

                    { "type": "numeric", "title": "Send port",
                      "desc": "Send port to use, from 1024 to 65535",
                      "section": "network", "key": "send_port" },

                    { "type": "numeric", "title": "Receive port",
                      "desc": "Receive port to use, from 1024 to 65535",
                      "section": "network", "key": "receive_port" }
                ]'''
        # self.config est le config de build_config
        settings.add_json_panel('TapOSC', self.config, data=data)

    def on_config_change(self, config, section, key, value):
        if config is self.config:
            token = (section, key)
            if token == ('network', 'host'):
                print('host', value)
            elif token == ('network', 'send_port'):
                print('send_port', value)
            elif token == ('network', 'receive_port'):
                print('receive_port', value)
            # Reset des écrans
            self.screen_manager.clear_widgets()
            for i in range(len(SCREENS)):
                self.screen_manager.add_widget(SCREENS[i][0](name=SCREENS[i][1]))

    def go_mainscreen(self):
        self.screen_manager.current = ("Menu")

    def on_stop(self):
        '''Déruit la fenêtre puis stop python'''
        sys.exit()
        pass

    def do_quit(self):
        self.on_stop()
        print("Quit in TapOSCApp(App)")
        sys.exit()

if __name__ == '__main__':
    TapOSCApp().run()
