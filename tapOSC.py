#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = '0.01'


'''Application Android:
Envoie les datas d'un smartphone en OSC.
simpleOSC et OSC.py sont en version python 3
'''

import sys
import threading
from time import sleep

import kivy
kivy.require('1.8.0')
from kivy.app import App
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, ObjectProperty
from kivy.core.window import Window

import simpleOSC

Window.size = (450, 800)

class MainScreen(Screen):
    pass

class Screen1(Screen):
    def __init__ (self,**kwargs):
        super(Screen1, self).__init__(**kwargs)
        config = TapOSCApp.get_running_app().config
        host = config.get('network', 'host')
        sport = config.getint('network', 'sport')
        rport = config.getint('network', 'rport')
        print(host, sport, rport)

        # osc
        self.host = host
        self.sport = sport
        self.clt = simpleOSC.initOSCClient(self.host, self.sport)

    def on_touch_move(self, touch):
        # <MouseMotionEvent spos=(0.49, 0.49) pos=(313.0, 421.0)>
        xy_abs = int(touch.pos[0]), int(touch.pos[1])
        print("Absolute", xy_abs)

        ws = Window.size
        x_percent = xy_abs[0] / ws[0]
        y_percent = xy_abs[1] / ws[1]
        xy_relative = x_percent, y_percent
        print("Relative", xy_relative)

        try:
            # Error if nothing listen the port
            simpleOSC.sendtoOSCMsg(self.clt, "/1/xy/x", [x_percent],
                                   ip=self.host, port=self.sport, timeout=0.05)
            simpleOSC.sendtoOSCMsg(self.clt, "/1/xy/y", [y_percent],
                                   ip=self.host, port=self.sport, timeout=0.05)
        except:
            print("PB with connected UDP: à revoir plus tard")
            print("simpleOSC.sendtoOSCMsg must be connected, stupid code")
            print("Connected UDP is stupid: see twisted documentation")

class Screen2(Screen):
    pass

class Screen3(Screen):
    pass

class Screen4(Screen):
    pass

class JsonScreen(Screen):
    pass

class OpenScreen(Screen):
    pass

SCREENS = { 0: (MainScreen,       "Menu"),
            1: (Screen1,          "Ecran 1"),
            2: (Screen2,          "Ecran 2"),
            3: (Screen3,          "Ecran 3"),
            4: (Screen4,          "Ecran 4"),
            5: (JsonScreen,       "Texte libre"),
            6: (OpenScreen,       "Page libre")
           }

class TapOSCApp(App):
    '''app est le parent de cette classe dans kv.'''
    def build(self):
        # Création des écrans
        screen_manager = ScreenManager()
        for i in range(len(SCREENS)):
            screen_manager.add_widget(SCREENS[i][0](name=SCREENS[i][1]))
        return screen_manager

    def build_config(self, config):
        '''Si le fichier *.ini n'existe pas,
        il est crée avec ces valeurs par défaut.
        Si il manque seulement des lignes, il ne fait rien !
        '''
        config.setdefaults('network',
            {
            'host': '127.0.0.1',
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

    # BEGIN ON_CONFIG_CHANGE
    def on_config_change(self, config, section, key, value):
        if config is self.config and key == "temp_type":
            try:
                self.root.children[0].update_weather()
            except AttributeError:
                pass
    # END ON_CONFIG_CHANGE

    def do_connect(self):
        # osc
        config = self.config
        host = config.get('network', 'host')
        sport = config.getint('network', 'send_port')
        rport = config.getint('network', 'receive_port')
        simpleOSC.initOSCClient(host, sport)

    def do_quit(self):
        print("Quit in TapOSCApp(App)")
        sys.exit()


if __name__ == '__main__':
    TapOSCApp().run()
