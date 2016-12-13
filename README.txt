
ABOUT THE CIRCADIA SUNRISE LAMP PROJECT
---------------------------------------
General info
https://sites.google.com/site/fpgaandco/sunrise



LICENCE
-------

Use it however you like. And/or contribute. MIT Licence.
See the file named LICENCE.TXT (included in this distribution) for details.


THEMES
------

Popular themes can be found here:
https://sites.google.com/site/fpgaandco/sunrise/resources


REQUIREMENTS (Editor/PC)
---------------------
* Python (2.7.9) [https://www.python.org/downloads/release/python-279/]
* Pillow (3.2.0) [https://pillow.readthedocs.io/en/3.4.x/]
* Pygame (1.9.1) [http://www.pygame.org/download.shtml]

REQUIREMENTS (Raspberry Pi)
--------------------
* Raspian image (wheezy)
* Python (2.7.3 pre-installed)
* Pygame (1.9.1 pre-installed)
* rpi_ws281x  (https://github.com/jgarff/rpi_ws281x)

INSTALLATION (PC)
-----------------

* install all requirements
* copy to drive
* create a folder for your themes
  * copy some themes in there
* open themedit/editor_cfg_template.json in a text editor
  * change the "themeRootPath" value to your theme folder path
  * (otionally) change "startupTheme" to an existing theme name
  * save it as editor_cfg.json
* open circadia_cfg_template.json in a text editor
  * under platform_cfg, win32 change the "themebasepath" to your theme path
  * save it as manila_cfg.json
* (Windows users, avoid backslashes (\) in config paths, use / instead, or escape it \\ )

INSTALLATION (Raspberry Pi)
---------------------------

* coming soon...



