## TapOSC
#### by Labomedia

TapOSC is an Android Application, made with Kivy.

TapOSC is OSC control surface for smartphone.

TapOSC is an Open Source project under GNU GENERAL PUBLIC LICENSE Version 2,
please see LICENSE file for details.

TapOSC n'est pas une pipe.

See [TapOSC](http://wiki.labomedia.org/index.php/Kivy:_TapOSC)

### Android app

Compiled with buildozer

### Python 3.5

### OSC

Pyhton 3 OSC3.py

### Installation

#### kivy pour python3
sudo apt-get install cython3 xclip xsel
sudo pip3 install kivy

#### pyjnuis

 sudo pip install cython
 sudo pip install jnius

#### Buildozer



### Installation on tablet or phone with ANDROID
Download the TapOSC.apk file, install it.

### Test on your PC
Open a terminal in root directory

 python3 main.py

### Bug connu
La rotation de l'écran dans les options ne s'applique pas immédiatement,
il faut relancer l'application.

Configurer KIVY dans les options avec Double Tap, pour que les boutons Menu
et Quitter ne s'active pas sur l'écran 1, lors de l'envoi de x y.


####Bidouille pour que python trouve java
Si platform = linux ajout de
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"

Le chemin doit être défini en fonction de l'os

##Thank's to:
Labomedia
