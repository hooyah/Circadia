"""
    Circadia Sunrise Lamp - AV engine

    Handles audio and graphics modules, themes, etc

    Author: fhu
"""

import json
import os
import time

from MSR_OS import mgraphic, msound
from MSR_HAL import circadiahw



# global vars -----------------------------------------------------------------------------
__author__ = "fhu"
System = dict()
msr_graphic_modules = list()
msr_sound_modules = list()
sys_hw = circadiahw.CircadiaHw
__callbacks = list()

# registered modules
Modules = {'gradient': mgraphic.gradient_module, 'imgShift': mgraphic.ImgShift_module, 'wav': msound.wav_module}
Themes = []



def loadTheme(themename):
    """
    Loads a theme by name
    A theme is a folder containing all the associated files, including a file called theme.json
    :param themename (string): name of the theme (folder, not a full path)
    :return:
    """

    theme_basepath = System['theme_path']+themename+os.path.sep
    file = open( theme_basepath+'theme.json', "r")

    if not file:
        print "couldn't open file", theme_basepath+themename
    else:
        prg = json.load(file)
        #pprint(prg)

        print 'loading theme "%s"...'%prg['name'],

        global Modules
        global msr_graphic_modules
        global msr_sound_modules

        if 'LUT' in prg:
            print "switching lut to '%s'"%prg['LUT']
            sys_hw.switchLut(prg['LUT'])

        # create graphics modules
        msr_graphic_modules = list()
        for m in prg['graphics']:
            if m['mod'] in Modules:
                mod = Modules[m['mod']]
                msr_graphic_modules.append( mod(theme_basepath, moduleDef=m, height=System["screen_height"], width=System["screen_width"]))


        # create sound modules
        msr_sound_modules = list()
        for m in prg['sounds']:
            if m['mod'] in Modules:
                mod = Modules[m['mod']]
                msr_sound_modules.append(mod(theme_basepath, m))

        file.close()
        print 'done.'

    return themename


def reset_audioVideo():
    """ resets all modules """

    for mod in msr_sound_modules:
        mod.reset()

    for mod in msr_graphic_modules:
        mod.reset()


def handle_audioVideo(timeElapsed):
    """
    updates video and audio modules to the new time
    :param timeElapsed (class modbase.timeInterval): the time elapsed since the start of the theme
    """

    for mod in msr_sound_modules:
        mod.tick(timeElapsed)

    canvas = System['canvas']

    updated = False
    for mod in msr_graphic_modules:
        if mod.tick(timeElapsed) == True:
            mod.updateCanvas(canvas)
            updated = True

    if updated:     # if none of the modules updated the canvas, no screen update is required
        sys_hw.update_screen(canvas)



#  handle a gentle screen fadeout
def fadeOut(percent):
    """
    Poll this with an increasing intensity(percent) to gently fade out the graphics
    :param percent (float): 0-1 with 0=no effect, 1=black
    :return:
    """

    canvas = System['canvas']

    if percent < 0.99:
        canvas.multFill(0, (1-percent)*canvas.height*3, 0.9, 0.9, 0.9)
    else:
        canvas.fill( 0,0,0 )
    sys_hw.update_screen(canvas)


# update system settings
def setPrefs(system):
    """
    sets the system settings dictionary
    :param system (dict): a dictionary with named settings and objects
    :return:
    """

    global System
    System = system



def loadConfig(cfg_path):
    """
    load and return a config

    :param cfg_path (string): full path name to config file
    :return (json): config as a python list or dict
    """

    try:
        cfg_file = open(cfg_path, "r")
        config = json.load(cfg_file)
        cfg_file.close()
        return config
    except:
        print "couldn't open config file. configure circadia_cfg_template.json and rename it to circadia_cfg.json"
        raise(RuntimeError)



def addCallback(callbackFn, param, delay, perpetual=False):

    global __callbacks
    if perpetual:
        delay *= -1
    __callbacks.append([time.time(), delay, callbackFn, param])


def pollCallbacks():

    global __callbacks
    now = time.time()

    #print 'now',now
    #print __callbacks

    remaining = []
    for cb in __callbacks:
        delay = abs(cb[1])
        perpetual = True if cb[1] < 0 else False

        if now-cb[0] > delay:
            print 'running callback', cb[2]
            cb[2](cb[3])
            if perpetual:
                cb[0] = now
                remaining.append(cb)
        else:
            remaining.append(cb)

    __callbacks = remaining


def clearCallbacks():

    global __callbacks
    __callbacks = []

