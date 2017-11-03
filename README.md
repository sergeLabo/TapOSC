## TapOSC
#### by Labomedia

TapOSC est une application Android, réalisée avec Kivy et buldozer en python 3

### buildozer est en développement

En novembre 2017, buildozer est en développement pour python 3.

Les apk ne marche pas, buildozer mélange du python2 et du python 3.

TapOSC aurait du envoyer et reçevoir en OSC.

Par contre, l'application tourne sur PC.

### Sinon

TapOSC is an Open Source project under GNU GENERAL PUBLIC LICENSE Version 2,
please see LICENSE file for details.

TapOSC n'est pas une pipe.

La page [TapOSC](https://wiki.labomedia.org/index.php/Kivy:_TapOSC) qui concerne le python 2.7

### OSC

OSC3.py pour python3

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


#### Bidouille pour que python trouve java sur PC

Si platform = linux ajout de

~~~text
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
~~~

Le chemin doit être défini en fonction de l'os

### Merci à
* Labomedia
