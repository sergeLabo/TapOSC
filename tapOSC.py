#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''Application Android:
Envoie les datas d'un smartphone en OSC
et reçois.
Peut envoyer en json du UTF8
'''

import sys
import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout

from kivy.lib import osc

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
    '''app est le parent de cette classe'''
    def build(self):
        scrman = ScreenManager()
        for i in range(len(SCREENS)):
            scrman.add_widget(SCREENS[i][0](name=SCREENS[i][1]))
        return scrman

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
        print("Fichier taposc.ini ok", config)

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

    def do_connect(self):
        config = self.config
        host = config.get('network', 'host')
        sport = config.getint('network', 'send_port')
        rport = config.getint('network', 'receive_port')
        print("host = {} sport = {} rport = {}".format(host, sport, rport))
        # osc server
        osc.init()
        oscid = osc.listen(ipAddr=host, port=rport)
        #osc.bind(oscid, some_api_callback, '/some_api')


    def do_quit(self):
        print("Quit in TapOSCApp(App)")
        sys.exit()


if __name__ == '__main__':
    TapOSCApp().run()
