#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''Application Android:
Envoie les datas d'un smartphone en OSC
et reçois.
Peut envoyer en json du UTF8
'''

import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

Window.size = (630, 1120)

class MainScreen(Screen):
    pass

class Screen1(Screen):
    pass

class Screen2(Screen):
    pass

class Screen3(Screen):
    pass

class Screen4(Screen):
    pass

class SettingsScreen(Screen):
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
            5: (SettingsScreen,   "Options"),
            6: (JsonScreen,       "Texte libre"),
            7: (OpenScreen,       "Page libre")
           }

class TapOSCMain(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__()

        self.ip = self.app.config.get('network', 'host')
        self.sendport = int(self.app.config.get('network' , 'send_port'))
        self.receiveport = int(self.app.config.get('network' , 'receive_port'))

    def do_quit(self, value):
        print("Strictly Quit in progess")
        sys.exit()

class TapOSCApp(App):
    def build(self):
        scrman = ScreenManager()
        for i in range(8):
            scrman.add_widget(SCREENS[i][0](name=SCREENS[i][1]))

        # switch to main screen
        parent = self.root.parent
        parent.remove_widget(self.root)
        # lien avec TapOSCMain
        self.root = TapOSCMain()
        parent.add_widget(self.root)

        return scrman

    def build_config(self, config):
        config.add_section('network')
        config.set('network', 'host', '127.0.0.1')
        config.set('network', 'receive_port', '9000')
        config.set('network', 'send_port', '8000')
        config.add_section('kivy')

    def build_settings(self, settings):
        data = '''[

            { "type": "string", "title": "Host",
              "desc": "Ip address to use",
              "section": "network", "key": "host" },

            { "type": "title", "title": "Network configuration" },

            { "type": "numeric", "title": "Send port",
              "desc": "Send port to use, from 1024 to 65535",
              "section": "network", "key": "send_port" },

            { "type": "numeric", "title": "Receive port",
              "desc": "Receive port to use, from 1024 to 65535",
              "section": "network", "key": "receive_port" }

        ]'''
        settings.add_json_panel('KiviOSC', self.config, data=data)

    def do_play(self):
        config = self.config
        host = config.get('network', 'host')
        sport = config.getint('monome', 'send_port')
        rport = config.getint('monome', 'receive_port')

        # osc
        #appel fichier asyncio

if __name__ == '__main__':
    TapOSCApp().run()
