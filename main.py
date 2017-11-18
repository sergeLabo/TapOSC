#! /usr/bin/env python3
# -*- coding: utf-8 -*-

######################################################################
# TapOSC est une Application Android construite avec kivy
# et compilee avec Buildozer
#
# ZORG: "Vous voulez quelque chose, faites le vous meme !"
#
# Copyright (C) Labomedia March 2015
#
# This file is part of TapOSC.
#
# TapOSC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TapOSC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TapOSC.  If not, see <http://www.gnu.org/licenses/>. 2
######################################################################


__version__ = '0.955'


"""
version
0.955 sans get ip, sans android, ip serveur revu, sans acceleration
version suivante en python 3
0.67 version python2
"""


import os

# Bidouille pour que python trouve java sur mon PC
##os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"

import threading
import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.core.window import Window
from kivy.config import Config
import OSC3


def get_my_LAN_ip():
    # Oui, pas d'import sauvage
    import socket
    sok = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sok.connect(("8.8.8.8", 80))
    ip = sok.getsockname()[0]
    sok.close()
    print("LAN Ip =", ip)
    return ip

def xy_correction(x, y):
    """Retourne x, y recalcule au dessus du bouton, de 0 a 1."""

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
    """acc = liste de 3
    arrondi a 0.01
    retourne True si different, False sinon
    les capteurs sont imprecis et instable, retourne toujours True
    donc frequence maxi definie dans les options.
    """

    ret = False
    if isinstance(acc_old, list) and len(acc_old) == 3:
        if isinstance(acc_new, list) and len(acc_new) == 3:
            # Arrondi a 0.01
            a_old = [int(100 * acc_old[0]),
                     int(100 * acc_old[1]),
                     int(100 * acc_old[2])]
            a_new = [int(100 * acc_new[0]),
                     int(100 * acc_new[1]),
                     int(100 * acc_new[2])]
            if a_old != a_new:
                ret = True
            else:
                print("Pas de changement des Accelerations a 0.01 pres")
    return ret

def test_old_new_xy(xy_old, xy_new):
    """xy = liste de 2
    arrondi a 0.01
    retourne True si different, False sinon
    La frequence d'envoi des xy peut monter a 73 Hz = beaucoup trop,
    a 0.01 c'est suffisamment precis.
    """

    ret = False

    if xy_new[0] != None and xy_new[1] != None:
        if isinstance(xy_old, list) and len(xy_old) == 2:
            if isinstance(xy_new, list) and len(xy_new) == 2:
                # Arrondi a 0.01
                a_old = [int(100 * xy_old[0]), int(100 * xy_old[1])]
                a_new = [int(100 * xy_new[0]), int(100 * xy_new[1])]
                if a_old != a_new:
                    ret = True

    return ret


class MainScreen(Screen):
    """Cree le client OSC qui est toujours le meme, seule l'adresse utilisee
    par sendto est mise a jour."""

    def __init__(self, **kwargs):

        super(MainScreen, self).__init__(**kwargs)

        # OSC client isn't connected, created without address
        # sendto use address, if address change, adress only must be updated
        self.clt = OSC3.OSCClient()
        self.clt_addr, self.rport = self.get_clt_svr_address()

        self.server = None
        self.create_server()
        print("Main Screen init ok")

    def create_server(self):
        """Create a thread with OSC server."""

        # OSC Server recoit seulemnt les messages OSC  "/info"
        # Ip serveur
        ip = get_my_LAN_ip()
        self.server = OSC3.OSCServer((ip, self.rport))
        self.server.addMsgHandler("/info", self.info_handler)

        t_server = threading.Thread(target=self.server.serve_forever)
        t_server.start()

    def restart_server(self):
        """Restart the sever if server address change."""

        if self.server:
            self.server.close()

        self.create_server()

        print("Server restart with port {}".format(self.rport))

    def info_handler(self, addr, tags, stuff, source):
        """Called if /info tag receive. Set Text info in ScreenX"""

        print(addr, tags, stuff, source)

        if addr == '/info':
            print("Info {} {} {} {}".format(addr, tags, stuff, source))
            stuff = str(stuff[0])
            screen_manager = TapOSCApp.get_running_app().screen_manager
            for scr in ["Ecran 1", "Ecran 2", "Ecran 3", "Ecran 4"]:
                screen_manager.get_screen(scr).set_info(stuff)

    def reset_address(self, address):
        """Reset client address."""

        self.clt_addr = address

        print("MainScreen: Reset OSC address with {}".format(address))

    def get_clt_svr_address(self):
        """Retourne adresse client et port serveur"""

        config = TapOSCApp.get_running_app().config
        host = config.get('network', 'host')
        sport = int(config.get('network', 'send_port'))
        self.clt_addr = host, sport

        self.rport = int(config.get('network', 'receive_port'))


        print("Le server ecoute le  port {}".format(self.rport))

        print("Client Address = {}".format(self.clt_addr))

        return self.clt_addr, self.rport


class Screen1(Screen):
    """Ecran 1."""

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
        """self.info is used to display info in every Sceen."""

        self.info = str(stuff)

    def reset_address(self, address):
        """Reset client address."""

        self.clt_addr = address
        print("Screen1: Reset OSC address with {}".format(address))

    def get_clt_and_address(self):
        """Acces a Menu = MainScreen pour recuperer self.clt"""

        # Acces a screen manager dans TapOSCApp
        screen_manager = TapOSCApp.get_running_app().screen_manager

        # Acces a l'ecran Menu
        menu = screen_manager.get_screen("Menu")
       # Acces a l'attibut clt
        self.clt = menu.clt

        # Acces a address
        self.clt_addr = menu.get_clt_svr_address()[0]
        return self.clt, self.clt_addr

    def on_touch_move(self, touch):
        """Si move sur l'ecran, n'import ou."""

        x = touch.spos[0]
        y = touch.spos[1]
        self.apply_on_touch(x, y)

    def apply_on_touch(self, x, y):
        """Envoi la position du curseur."""

        xy_new = [x, y]
        # Pas de None
        if x and y:
            # Si valeurs differente a 0.01 pres
            if test_old_new_xy(self.xy_old, xy_new):
                # OSC
                msg = OSC3.OSCMessage('/1/xy')
                msg.append(x)
                msg.append(y)
                self.clt.sendto(msg, self.clt_addr)
                self.xy_old = xy_new


class Screen2(Screen):
    """Ecran 2."""
    info = StringProperty()

    def __init__(self, **kwargs):

        super(Screen2, self).__init__(**kwargs)

        self.clt, self.clt_addr = self.get_clt_and_address()
        print("OSC Client = {} address = {}".format(self.clt, self.clt_addr))

        # Info from server : set with info from server
        self.info = "Retour d'info"

        print("Screen2 init ok")

    def set_info(self, stuff):
        """self.info is used to display info in every Sceen."""

        self.info = str(stuff)

    def reset_address(self, address):
        """self.info is used to display info in every Sceen."""

        self.clt_addr = address
        print("Screen1: Reset OSC address with {}".format(address))

    def get_clt_and_address(self):
        """Acces a Menu = MainScreen pour recuperer self.clt"""

        # Acces a screen manager dans TapOSCApp
        screen_manager = TapOSCApp.get_running_app().screen_manager

        # Acces a l'ecran Menu
        menu = screen_manager.get_screen("Menu")

       # Acces a l'attibut clt
        self.clt = menu.clt

        # Acces a address
        self.clt_addr = menu.get_clt_svr_address()[0]

        return self.clt, self.clt_addr

    def do_button_on(self, iD, instance):
        """Call if button is on."""

        print("Button {} on".format(iD))

        # OSC envoi de iD, 1
        msg = OSC3.OSCMessage(iD)
        msg.append(1)
        self.clt.sendto(msg, self.clt_addr)

    def do_button_off(self, iD, instance):
        """Call if button is on."""

        print("Button {} off".format(iD))

        # OSC envoi de iD, 0
        msg = OSC3.OSCMessage(iD)
        msg.append(0)
        self.clt.sendto(msg, self.clt_addr)

    def do_slider(self, iD, instance, value):
        """Call if slider change."""

        print("Slider value {} = {}".format(iD, value))

        # OSC envoi de slider value
        msg = OSC3.OSCMessage(iD)
        msg.append(value)
        self.clt.sendto(msg, self.clt_addr)


class Screen3(Screen):
    """Ecran 3."""

    info = StringProperty()

    def __init__(self, **kwargs):

        super(Screen3, self).__init__(**kwargs)

        self.clt, self.clt_addr = self.get_clt_and_address()
        print("OSC Client = {} address = {}".format(self.clt, self.clt_addr))

        # Info from server : set with info from server
        self.info = "Retour d'info"
        self.xy_old = [0, 0]

        print("Screen3 init ok")

    def set_info(self, stuff):
        """self.info is used to display info in every Sceen."""

        self.info = str(stuff)

    def reset_address(self, address):
        """Reset client address."""

        self.clt_addr = address
        print("Screen1: Reset OSC address with {}".format(address))

    def get_clt_and_address(self):
        """Acces a Menu = MainScreen pour recuperer self.clt"""

        # Acces a screen manager dans TapOSCApp
        screen_manager = TapOSCApp.get_running_app().screen_manager
        # Acces a l'ecran Menu
        menu = screen_manager.get_screen("Menu")
        # Acces a l'attibut clt
        self.clt = menu.clt
        # Acces a address
        self.clt_addr = menu.get_clt_svr_address()[0]

        return self.clt, self.clt_addr

    def on_touch_move(self, touch):
        """Si move sur l'ecran, n'import ou."""

        x = touch.spos[0]
        y = touch.spos[1]
        self.apply_on_touch(x, y)

    def apply_on_touch(self, x, y):
        """Envoi la position du curseur.
        Non applique si slider
        """

        print("apply_on_touch", x, y)

        xy_cor = xy_correction(x, y)
        xy_new = [xy_cor[0], xy_cor[1]]

        # Pas de None
        if x and y:
            if test_old_new_xy(self.xy_old, xy_new):
                print("Position x={} y={}".format(x, y))

                # OSC
                msg = OSC3.OSCMessage('/3/xy')
                msg.append(x)
                msg.append(y)
                self.clt.sendto(msg, self.clt_addr)
                self.xy_old = xy_new

    def do_slider(self, iD, instance, value):
        """Called if slider change."""

        print("slider", iD, value)

        # OSC envoi de slider value
        msg = OSC3.OSCMessage(iD)
        msg.append(value)
        self.clt.sendto(msg, self.clt_addr)


class Screen4(Screen):
    """Ecran 4."""
    info = StringProperty()
    blanche = ObjectProperty(None)

    def __init__(self, **kwargs):
        """Buttons are created here, not in kv."""

        super(Screen4, self).__init__(**kwargs)

        for x in range(16):
            btn = TapOscButton(index=x)
            btn.bind(state=self.on_button_state)
            self.blanche.add_widget(btn)

        self.clt, self.clt_addr = self.get_clt_and_address()
        print("OSC Client = {} address = {}".format(self.clt, self.clt_addr))

        # Info from server : set with info from server
        self.info = "Retour d'info"

        print("Screen4 init ok")

    def set_info(self, stuff):
        """self.info is used to display info in every Sceen."""

        self.info = str(stuff)

    def reset_address(self, address):
        """Reset client address."""

        self.clt_addr = address
        print("Screen4: Reset OSC address with {}".format(address))

    def get_clt_and_address(self):
        """Acces a Menu = MainScreen pour recuperer self.clt"""

        # Acces a screen manager dans TapOSCApp
        screen_manager = TapOSCApp.get_running_app().screen_manager

        # Acces a l'ecran Menu
        menu = screen_manager.get_screen("Menu")

       # Acces a l'attibut clt
        self.clt = menu.clt

        # Acces a address
        self.clt_addr = menu.get_clt_svr_address()[0]

        return self.clt, self.clt_addr

    def on_button_state(self, instance, value):
        """Call if button state change."""

        index = instance.index
        if value == 'down':
            value = int(index)
        else:
            value = 0

        # OSC
        msg = OSC3.OSCMessage('/4/b')
        msg.append(value)
        self.clt.sendto(msg, self.clt_addr)


class TapOscButton(Button):
    """Utilise dans Ecran 4 pour creer les boutons dans init."""

    index = NumericProperty(0)


# Liste des ecrans, cette variable appelle les classes ci-dessus
# et doit etre placee apres ces classes
SCREENS = {0: (MainScreen, "Menu"),
            1: (Screen1, "Ecran 1"),
            2: (Screen2, "Ecran 2"),
            3: (Screen3, "Ecran 3"),
            4: (Screen4, "Ecran 4")}


class TapOSCApp(App):
    """Excecute par __main__,
    app est le parent de cette classe dans kv."""

    def build(self):
        """Execute en premier apres run()"""

        print("build begining")
        # Creation des ecrans
        self.screen_manager = ScreenManager()
        for i in range(len(SCREENS)):
            self.screen_manager.add_widget(SCREENS[i][0](name=SCREENS[i][1]))
        return self.screen_manager

    def on_start(self):
        """Execute apres build()"""

        pass

    def build_config(self, config):
        """Si le fichier *.ini n'existe pas,
        il est cree avec ces valeurs par defaut.
        Si il manque seulement des lignes, il ne fait rien !
        """

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
        """Construit l'interface de l'ecran Options, pour TapOSC seul,
        Kivy est par defaut, appele par app.open_settings() dans .kv
        """

        data = """[{"type": "title", "title": "Configuration du reseau"},
                    {"type": "string", "title": "Adresse IP d'envoi",
                      "desc": "Adresse Ip de l'appareil qui reçoit",
                      "section": "network", "key": "host"},
                    {"type": "numeric", "title": "Port d'envoi",
                      "desc": "Port d'envoi, de 1024 a 65535",
                      "section": "network", "key": "send_port"},
                    {"type": "numeric", "title": "Port de reception",
                      "desc": "Port de reception, de 1024 a 65535",
                      "section": "network", "key": "receive_port"},
                      {"type": "numeric",
                      "title": "Frequence d'envoi des accelerations",
                      "desc": "Frequence entre 1 et 60 Hz",
                      "section": "network", "key": "freq"}]"""

        # self.config est le config de build_config
        settings.add_json_panel('TapOSC', self.config, data=data)

    def on_config_change(self, config, section, key, value):
        """Si modification des options, fonction appelee automatiquement."""

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

            if token == ('network', 'receive_port'):
                # Restart the server with new address
                self.screen_manager.get_screen("Menu").restart_server()


        if section == 'graphics' and key == 'rotation':
            Config.set('graphics', 'rotation', int(value))
            print("Screen rotation = {}".format(value))

    def go_mainscreen(self):
        """Retour au menu principal depuis les autres ecrans."""

        #if touch.is_double_tap:
        self.screen_manager.current = ("Menu")

    def do_quit(self):
        """Quit propre, stop le client, le serveur."""

        # Acces a screen manager dans TapOSCApp
        screen_manager = TapOSCApp.get_running_app().screen_manager
        # Acces a l'ecran Menu
        menu = screen_manager.get_screen("Menu")

        print("Quit in TapOSCApp(App)")

        # Voir OSC.py, running is set to True with serve_forever
        menu.server.running = False

        # Kivy
        TapOSCApp.get_running_app().stop()

        # Fin
        os._exit(0)


if __name__ == '__main__':
    TapOSCApp().run()
