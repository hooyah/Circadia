
ABOUT THE CIRCADIA SUNRISE LAMP PROJECT
---------------------------------------

A python framework to create a sunrise lamp
and to easily author various themes of light and sound.

It is running on a Raspberry Pi 2/3.
The editor is running on Windows (only tested Windows).

project page:  https://sites.google.com/site/fpgaandco/sunrise



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


INSTALLATION (PC)
-----------------

* install all requirements
* clone or download everything
* create a folder for your themes
  * copy some themes in there (see themes above)
* open themedit/editor_cfg_template.json in a text editor
  * change the "themeRootPath" value to your theme folder path
  * (otionally) change "startupTheme" to an existing theme name
  * save it as editor_cfg.json
* open circadia_cfg_template.json in a text editor
  * under platform_cfg, win32 change the "themebasepath" to your theme path
  * save it as manila_cfg.json
* (Windows users, avoid backslashes (\) in config paths, use / instead, or escape it \\ )

* run the editor with: python themedit/edit.py



REQUIREMENTS (Alarm clock/Raspberry Pi)
--------------------
* Raspbian image (wheezy/jessie)
* Python (2.7.3 pre-installed)
* Pygame (1.9.1 pre-installed)
* rpi_ws281x  (https://github.com/jgarff/rpi_ws281x)


INSTALLATION (Raspberry Pi)
---------------------------

(summary, check wiki/forum for detailed instructions)
* install a recent Raspbian image on your Pi
* setup wifi and audio (usb sound card)
* clone and build rpi_ws281x library (see link above, follow projects build instructions)
* clone or download this repository to your pi
* open MSR_HAL/circadia_hw_lamp.py in your favourite editor
  * change the neopixel hardware configuration at the top of the file to your setup
    especially LED_COUNT, LED_INVERT
* open circadia_cfg_template.json
  * under platform_cfg, raspi change the screen_width and height to your setup
  * change the serial device name to your system (PI 2=ttyAMA0, PI 3=serial0)
    * (on a Raspberry Pi 3 the uart is a bit messed up and needs to be dealt with)
       enable serial0 uart or don't specify a device with "serial": ""
  * save it as circadia_cfg.json
* add the environment variable CIRCADIA_PLATFORM to your env
  * make sure sudo is able to see it too (visudo)
  * the code uses this variable to detect whether it is running on the raspi or win32

* run the lamp app with: sudo python circadia_alarm.py [themename]
