## TapOSC
#### by Labomedia

TapOSC est une application Android, réalisée avec Kivy et buildozer en python 3

TapOSC envoie et reçoit en OSC.

TapOSC n'est pas une pipe.


Documentation à [TapOSC](https://wiki.labomedia.org/index.php/Kivy:_TapOSC)

### Buildozer

TapOSC est construit avec kivy en python 3.5,

et est compilée avec buildozer pour obtenir un apk, une application Android

Buildozer pour python 3.x est en développement

### Licence

TapOSC is an Open Source project under GNU GENERAL PUBLIC LICENSE Version 2,
please see LICENSE file for details.

### OSC

OSC3.py pour python3

[Documentation très perfectible](https://wiki.labomedia.org/index.php/Open_Sound_Control_:_OSC)


### Installation

* [Kivy et pyjnius](https://wiki.labomedia.org/index.php/2_Kivy:_Installation)
* [Buildozer](https://wiki.labomedia.org/index.php/Kivy_Buildozer_pour_cr%C3%A9er_une_application_Android_avec_un_script_python#Version_M.C3.A9thode_2)


### Installation sur ANDROID

Télécharger TapOSC.apk et l'installer en autorisant les sources inconnues.

### Test sur PC

Ouvrir un terminal dans le dossier de main.py

~~~text
python3 main.py
~~~

### Bug connu

La rotation de l'écran dans les options ne s'applique pas immédiatement,
il faut relancer l'application.

Configurer KIVY dans les options avec Double Tap, pour que les boutons Menu
et Quitter ne s'active pas sur l'écran 1, lors de l'envoi de x y.

### Développement prévu

* rajouter les accents
* envoyer les accélérations

### Merci à
* Labomedia
