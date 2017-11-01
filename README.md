## TapOSC
#### by Labomedia

TapOSC est une application Android, réalisée avec Kivy et buldozer en python 3

TapOSC envoie et reçoit en OSC.

TapOSC is an Open Source project under GNU GENERAL PUBLIC LICENSE Version 2,
please see LICENSE file for details.

TapOSC n'est pas une pipe.

See [TapOSC](https://wiki.labomedia.org/index.php/Kivy:_TapOSC)

### OSC

OSC3.py pour python3

### Installation

#### kivy pour python3

~~~text
sudo apt-get install cython3 xclip xsel
sudo pip3 install kivy
~~~

#### pyjnuis

~~~text
sudo pip install cython
sudo pip install jnius
~~~

### Installation sur ANDROID

Télécharger TapOSC.apk et l'installer en autorisant les sources inconnues.

### Test surr PC

Ouvrir un terminal dans le dossier de main.py

~~~text
python3 main.py
~~~

### Bug connu

La rotation de l'écran dans les options ne s'applique pas immédiatement,
il faut relancer l'application.

Configurer KIVY dans les options avec Double Tap, pour que les boutons Menu
et Quitter ne s'active pas sur l'écran 1, lors de l'envoi de x y.


####Bidouille pour que python trouve java

Si platform = linux ajout de

~~~text
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
~~~

Le chemin doit être défini en fonction de l'os

### Merci à
* Labomedia
