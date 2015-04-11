#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
TapOSC est une Application Android construite avec kivy
et compilée avec Buildozer

ZORG: "Vous voulez quelque chose, faites le vous mëme !"

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


__version__ = '0.66'


'''
version
0.66 main propre
0.65 acc à 0.01 près, xy à 0.01 près, plus de float(int(float()))
0.64 acc envoyé si nouveau, debit xy jusque 73 Hz, beaucoup trop
'''

import sys
import socket
import fcntl
import struct
from time import sleep
import threading

import kivy
kivy.require('1.8.0')
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.core.window import Window
from kivy.config import Config

from OSC import OSCClient, OSCMessage, OSCServer
from jnius import autoclass


def get_lan_ip():
    '''Retourne l'IP sur le réseau local.'''

    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127."):
        interfaces = ["eth0", "eth1", "eth2", "wlan0", "wlan1", "wifi0",
                      "ath0", "ath1", "ppp0"]
        for ifname in interfaces:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,
                                      struct.pack('256s', ifname[:15]))[20:24])
                break
            except IOError:
                pass
    return ip

def xy_correction(x, y):
    '''Retourne x, y recalculé au dessus du bouton, de 0 à 1.'''

    a1 = 0.015
    a2 = 0.50
    b1 = 0.09
    b2 = 0.97

    if x <= a1:
        x = 0.0
    elif x >= a2:
        x = 1.0
        y = None
    elif a1 < x < a2:
        x = (x / (a2 - a1)) - a1 / (a2- a1)

    if y:
        if y <= b1:
            y = 0.0
        elif y >= b2:
            y = 1.0
        elif b1 < y < b2:
            y = (y / (b2 - b1)) - b1 / (b2- b1)

    return x, y

def test_old_new_acc(acc_old, acc_new):
    '''acc = liste de 3
    arrondi à 0.01
    retourne True si différent, False sinon
    les capteurs sont imprécis et instable, retourne toujours True
    donc fréquence maxi définie dans les options.
    '''

    ret = False
    if isinstance(acc_old, list) and len(acc_old) == 3:
        if isinstance(acc_new, list) and len(acc_new) == 3:
            # Arrondi à 0.01
            a_old = [int(100 * acc_old[0]),
                     int(100 * acc_old[1]),
                     int(100 * acc_old[2])]
            a_new = [int(100 * acc_new[0]),
                     int(100 * acc_new[1]),
                     int(100 * acc_new[2])]
            if a_old != a_new:
                ret = True
            else:
                print("Pas de changement des Accélérations à 0.01 près")
    return ret

def test_old_new_xy(xy_old, xy_new):
    '''xy = liste de 2
    arrondi à 0.01
    retourne True si différent, False sinon
    La fréquence d'envoi des xy peut monter à 73 Hz = beaucoup trop,
    à 0.01 c'est suffisamment précis.
    '''

    ret = False
    # Bug incompréhensible
    if isinstance(xy_old, list) and len(xy_old) == 2:
        if isinstance(xy_new, list) and len(xy_new) == 2:
            # Vérification des valeurs
            print(xy_old[0], xy_old[1], xy_new[0], xy_new[1])
            # Arrondi à 0.01
            a_old = [int(100 * xy_old[0]), int(100 * xy_old[1])]
            a_new = [int(100 * xy_new[0]), int(100 * xy_new[1])]
            print(a_old, a_new)
            if a_old != a_new:
                ret = True

    print("Envoi de xy: ", ret)
    return ret


class AndroidOnly(object):
    '''Cette classe crée un thread si un accéléromètre existe, et si oui
    envoie les accélérations à la fréquence définie dans les options.'''

    def __init__(self, clt, address, freq):
        '''Clt pour cette classe seule, Address = Client address.'''
        self.hardware = None
        self.acc_thread = None
        self.platform = sys.platform
        print("Platform = {}".format(self.platform))
        self.loop = 1
        # Osc Client de MainScreen
        self.android_clt = clt
        self.address = address
        self.freq = freq
        self.acc = [0, 0, 0]

        # Il faut vérifier sur plusieurs téléphones: linux3
        if 'linux3' in self.platform:
            try:
                self.hardware = autoclass('org.renpy.android.Hardware')
                self.hardware.accelerometerEnable(True)
                self.acc_thread = threading.Thread(target=self.send_acc)
                self.acc_thread.start()
            except:
                print("Pb with Android Hardware")
        print("AndroidOnly init ok")

    def send_acc(self):
        '''Infinite loop to send acc if new, freq in options,
        loop ended with self.loop.
        '''

        while self.loop:
            try:
                acc = self.hardware.accelerometerReading()
            except:
                acc = [0, 0, 0]
            if 1:  #test_old_new_acc(self.acc, acc):
                try:
                    msg = OSCMessage('/1/acc')
                    msg.append([acc[1], acc[0], acc[2]])
                    self.android_clt.sendto(msg, self.address)
                except:
                    pass
            # 60 fps: 0.015
            if self.freq != 0:
                periode = 1.0 / float(self.freq)
                # Maxi 60 Hz
                if periode < 0.015:
                    periode = 0.015
            else:
                # Mini = 1 Hz
                periode = 1
            self.acc = acc
            sleep(periode)

    def reset_freq(self, freq):
        self.freq = freq

    def reset_address(self, address):
        self.address = address

    def stop_loop(self):
        '''Stoppe la boucle infinie de send_acc.'''

        print("AndroidOnly loop stop")
        self.loop = 0


class MainScreen(Screen):
    '''Crée le client OSC qui est toujours le même, seule l'adresse utilisée
    par sendto est mise à jour.'''

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        # OSC client isn't connected, created without address
        # sendto use address, if address change, adress only must be updated
        self.clt = OSCClient()
        self.clt_addr, self.svr_addr = self.get_clt_svr_address()
        self.freq = self.get_freq()
        self.android_thread = AndroidOnly(self.clt, self.clt_addr, self.freq)
        self.server = None
        self.create_server(self.svr_addr)
        print("Main Screen init ok")

    def get_freq(self):
        '''Return freq with config.'''

        config = TapOSCApp.get_running_app().config
        freq = int(config.get('network', 'freq'))
        return freq

    def change_android_freq(self, freq):
        '''Sert à rien'''

        self.android_thread.reset_freq(freq)

    def create_server(self, svr_addr):
        '''Create a thread with OSC server.'''

        # OSC Server only to receive OSC message from host with default "/info"
        svr_addr = self.get_clt_svr_address()[1]
        self.server = OSCServer(svr_addr)
        self.server.addMsgHandler("/info", self.info_handler)
        t_server = threading.Thread(target=self.server.serve_forever)
        t_server.start()

    def restart_server(self):
        '''Restart the sever if server address change.'''

        if self.server:
            self.server.close()
        svr_addr = self.get_clt_svr_address()[1]
        self.create_server(svr_addr)
        print("Server restart with {}".format(svr_addr))

    def info_handler(self, addr, tags, stuff, source):
        '''Call if /info tag receive. Set Text info in ScreenX'''

        if addr == '/info':
            print("Info {} {} {} {}".format(addr, tags, stuff, source))
            stuff = str(stuff[0])
            screen_manager = TapOSCApp.get_running_app().screen_manager
            for scr in ["Ecran 1", "Ecran 2", "Ecran 3", "Ecran 4"]:
                screen_manager.get_screen(scr).set_info(stuff)

    def reset_address(self, address):
        '''Reset client address in Android.'''

        self.clt_addr = address
        self.android_thread.reset_address(address)
        print("MainScreen: Reset OSC address with {}".format(address))

    def get_clt_svr_address(self):
        '''Return address with config, and set self.clt_addr'''

        config = TapOSCApp.get_running_app().config
        host = config.get('network', 'host')
        sport = int(config.get('network', 'send_port'))
        rport = int(config.get('network', 'receive_port'))
        self.clt_addr = host, sport
        self.svr_addr = get_lan_ip(), rport
        print("Client Address = {}".format(self.clt_addr))
        print("Server Address = {}".format(self.svr_addr))
        return self.clt_addr, self.svr_addr


class Screen1(Screen):
    '''Ecran 1.'''
    info = StringProperty()

    def __init__(self, **kwargs):
        super(Screen1, self).__init__(**kwargs)
        self.clt, self.clt_addr = self.get_clt_and_address()
        print("OSC Client = {} address = {}".format(self.clt, self.clt_addr))
        # Info from server : set with info from server
        self.info = "Retour d'info"
        print("Screen1 init ok")
        self.xy_old = [0, 0]

    def set_info(self, stuff):
        '''self.info is used to display info in every Sceen.'''

        self.info = str(stuff)

    def reset_address(self, address):
        '''Reset client address.'''

        self.clt_addr = address
        print("Screen1: Reset OSC address with {}".format(address))

    def get_clt_and_address(self):
        '''Accès à Menu = MainScreen pour récupérer self.clt'''

        # Accès à screen manager dans TapOSCApp
        screen_manager = TapOSCApp.get_running_app().screen_manager
        # Accès à l'écran Menu
        menu = screen_manager.get_screen("Menu")
       # Accès à l'attibut clt
        self.clt = menu.clt
        # Accès à address
        self.clt_addr = menu.get_clt_svr_address()[0]
        return self.clt, self.clt_addr

    def on_touch_move(self, touch):
        '''Si tap sur l'écran, n'import où.'''

        ws = Window.size
        # float pour python 2.7
        x_rel = float(touch.pos[0]) / ws[0]
        y_rel = float(touch.pos[1]) / ws[1]
        xy_new = [x_rel, y_rel]

        if test_old_new_xy(self.xy_old, xy_new):
            # OSC
            msg = OSCMessage('/1/xy')
            msg.append(x_rel)
            msg.append(y_rel)
            self.clt.sendto(msg, self.clt_addr)
            self.xy_old = xy_new


class Screen2(Screen):
    '''Ecran 2.'''
    info = StringProperty()

    def __init__(self, **kwargs):
        super(Screen2, self).__init__(**kwargs)
        self.clt, self.clt_addr = self.get_clt_and_address()
        print("OSC Client = {} address = {}".format(self.clt, self.clt_addr))
        # Info from server : set with info from server
        self.info = "Retour d'info"
        print("Screen2 init ok")

    def set_info(self, stuff):
        '''self.info is used to display info in every Sceen.'''

        self.info = str(stuff)

    def reset_address(self, address):
        '''self.info is used to display info in every Sceen.'''

        self.clt_addr = address
        print("Screen1: Reset OSC address with {}".format(address))

    def get_clt_and_address(self):
        '''Accès à Menu = MainScreen pour récupérer self.clt'''

        # Accès à screen manager dans TapOSCApp
        screen_manager = TapOSCApp.get_running_app().screen_manager
        # Accès à l'écran Menu
        menu = screen_manager.get_screen("Menu")
       # Accès à l'attibut clt
        self.clt = menu.clt
        # Accès à address
        self.clt_addr = menu.get_clt_svr_address()[0]
        return self.clt, self.clt_addr

    def do_button_on(self, iD, instance):
        '''Call if button is on.'''

        print("Button {} on".format(iD))
        # OSC envoi de iD, 1
        msg = OSCMessage(iD)
        msg.append(1)
        self.clt.sendto(msg, self.clt_addr)

    def do_button_off(self, iD, instance):
        '''Call if button is on.'''

        print("Button {} off".format(iD))
        # OSC envoi de iD, 0
        msg = OSCMessage(iD)
        msg.append(0)
        self.clt.sendto(msg, self.clt_addr)

    def do_slider(self, iD, instance, value):
        '''Call if slider change.'''

        print("Slider value {} = {}".format(iD, value))
        # OSC envoi de slider value
        msg = OSCMessage(iD)
        msg.append(value)
        self.clt.sendto(msg, self.clt_addr)


class Screen3(Screen):
    '''Ecran 3.'''
    info = StringProperty()

    def __init__(self, **kwargs):
        super(Screen3, self).__init__(**kwargs)
        self.ws = Window.size
        self.clt, self.clt_addr = self.get_clt_and_address()
        print("OSC Client = {} address = {}".format(self.clt, self.clt_addr))
        # Info from server : set with info from server
        self.info = "Retour d'info"
        self.xy_old = [0, 0]
        print("Screen3 init ok")

    def set_info(self, stuff):
        '''self.info is used to display info in every Sceen.'''

        self.info = str(stuff)

    def reset_address(self, address):
        '''Reset client address.'''

        self.clt_addr = address
        print("Screen1: Reset OSC address with {}".format(address))

    def get_clt_and_address(self):
        '''Accès à Menu = MainScreen pour récupérer self.clt'''

        # Accès à screen manager dans TapOSCApp
        screen_manager = TapOSCApp.get_running_app().screen_manager
        # Accès à l'écran Menu
        menu = screen_manager.get_screen("Menu")
       # Accès à l'attibut clt
        self.clt = menu.clt
        # Accès à address
        self.clt_addr = menu.get_clt_svr_address()[0]
        return self.clt, self.clt_addr

    def on_touch_move(self, touch):
        '''Si tap sur l'écran, n'import où.'''

        x = float(touch.pos[0]) / self.ws[0]
        y = float(touch.pos[1]) / self.ws[1]
        xy_cor = xy_correction(x, y)

        # OSC
        xy_new = [xy_cor[0], xy_cor[1]]
        if test_old_new_xy(self.xy_old, xy_new):
            msg = OSCMessage('/3/xy')
            msg.append(x)
            msg.append(y)
            self.clt.sendto(msg, self.clt_addr)
            self.xy_old = xy_new
            print("new")

    def do_slider(self, iD, instance, value):
        '''Call if slider change.'''

        print("slider", iD, value)
        # OSC envoi de slider value
        msg = OSCMessage(iD)
        msg.append(value)
        self.clt.sendto(msg, self.clt_addr)


class Screen4(Screen):
    '''Ecran 4.'''
    info = StringProperty()
    blanche = ObjectProperty(None)

    def __init__(self, **kwargs):
        '''Buttons are created here, not in kv.'''

        super(Screen4, self).__init__(**kwargs)
        for x in xrange(16):
            btn = TapOscButton(index=x)
            btn.bind(state=self.on_button_state)
            self.blanche.add_widget(btn)
        self.clt, self.clt_addr = self.get_clt_and_address()
        print("OSC Client = {} address = {}".format(self.clt, self.clt_addr))
        # Info from server : set with info from server
        self.info = "Retour d'info"
        print("Screen4 init ok")

    def set_info(self, stuff):
        '''self.info is used to display info in every Sceen.'''

        self.info = str(stuff)

    def reset_address(self, address):
        '''Reset client address.'''
        self.clt_addr = address
        print("Screen4: Reset OSC address with {}".format(address))

    def get_clt_and_address(self):
        '''Accès à Menu = MainScreen pour récupérer self.clt'''

        # Accès à screen manager dans TapOSCApp
        screen_manager = TapOSCApp.get_running_app().screen_manager
        # Accès à l'écran Menu
        menu = screen_manager.get_screen("Menu")
       # Accès à l'attibut clt
        self.clt = menu.clt
        # Accès à address
        self.clt_addr = menu.get_clt_svr_address()[0]
        return self.clt, self.clt_addr

    def on_button_state(self, instance, value):
        '''Call if button state change.'''

        index = instance.index
        if value == 'down':
            value = int(index)
        else:
            value = 0
        # OSC
        msg = OSCMessage('/4/b')
        msg.append(value)
        self.clt.sendto(msg, self.clt_addr)


class TapOscButton(Button):
    '''Utilisé dans Ecran 4 pour créer les boutons dans init.'''

    index = NumericProperty(0)


# Liste des écrans, cette variable appelle les classes ci-dessus
# et doit être placée après ces classes
SCREENS = {0: (MainScreen, "Menu"),
            1: (Screen1, "Ecran 1"),
            2: (Screen2, "Ecran 2"),
            3: (Screen3, "Ecran 3"),
            4: (Screen4, "Ecran 4")}


class TapOSCApp(App):
    '''Excécuté par __main__,
    app est le parent de cette classe dans kv.'''

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
                            {'host': '192.168.1.4',
                              'receive_port': '9000',
                              'send_port': '8000',
                              'freq': '10'})
        config.setdefaults('kivy',
                            {'log_level': 'debug',
                              'log_name': 'tapOSC_%y-%m-%d_%_.txt',
                              'log_dir': '/sdcard',
                              'log_enable': '1'})
        config.setdefaults('postproc',
                            {'double_tap_time': 250,
                              'double_tap_distance': 20})

    def build_settings(self, settings):
        '''Construit l'interface de l'écran Options, pour TapOSC seul,
        Kivy est par défaut, appelé par app.open_settings() dans .kv
        '''

        data = '''[{"type": "title", "title": "Configuration du réseau"},
                    {"type": "string", "title": "Adresse IP d'envoi",
                      "desc": "Adresse Ip de l'appareil qui reçoit",
                      "section": "network", "key": "host"},
                    {"type": "numeric", "title": "Port d'envoi",
                      "desc": "Port d'envoi, de 1024 à 65535",
                      "section": "network", "key": "send_port"},
                    {"type": "numeric", "title": "Port de réception",
                      "desc": "Port de réception, de 1024 à 65535",
                      "section": "network", "key": "receive_port"},
                      {"type": "numeric",
                      "title": "Fréquence d'envoi des accélérations",
                      "desc": "Fréquence entre 1 et 60 Hz",
                      "section": "network", "key": "freq"}]'''

        # self.config est le config de build_config
        settings.add_json_panel('TapOSC', self.config, data=data)

    def on_config_change(self, config, section, key, value):
        '''Si modification des options, fonction appelée automatiquement.'''

        host = self.config.get('network', 'host')
        sport = int(self.config.get('network', 'send_port'))
        rport = int(self.config.get('network', 'receive_port'))
        menu = self.screen_manager.get_screen("Menu")
        if config is self.config:
            token = (section, key)
            # If host ou send port change
            if token == ('network', 'send_port') or token == ('network', 'host'):
                # Reset OSC client address only in all screen
                clt_addr = host, sport
                # Update address client in every Screen
                for i in range(len(SCREENS)):
                    self.screen_manager.get_screen(SCREENS[i][1])\
                                                .reset_address(clt_addr)
                # Update android_only
                menu.android_thread.reset_address(clt_addr)

            if token == ('network', 'receive_port'):
                # Restart the server with new address
                self.screen_manager.get_screen("Menu").restart_server()

            if token == ('network', 'freq'):
                # Restart android with new frequency
                menu.android_thread.reset_freq(int(value))

        if section == 'graphics' and key == 'rotation':
            Config.set('graphics', 'rotation', int(value))
            print("Screen rotation = {}".format(value))

    def go_mainscreen(self):
        '''Retour au menu principal depuis les autres écrans.'''

        self.screen_manager.current = ("Menu")

    def do_quit(self):
        '''Quit propre, stop le thread Android, le client, le serveur.'''

        # Accès à screen manager dans TapOSCApp
        screen_manager = TapOSCApp.get_running_app().screen_manager
        # Accès à l'écran Menu
        menu = screen_manager.get_screen("Menu")
        # Stop thread andoid
        menu.android_thread.stop_loop()
        print("Quit in TapOSCApp(App)")
        # Voir OSC.py, running is set to True with serve_forever
        menu.server.running = False
        # Kivy
        TapOSCApp.get_running_app().stop()
        # La bombe
        sys.exit()


if __name__ == '__main__':
    TapOSCApp().run()
