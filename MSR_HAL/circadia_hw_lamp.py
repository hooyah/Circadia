"""
    Circadia Sunrise Lamp - the lamp HAL

    hardware abstraction layer running on the lamp

    Author: fhu
"""

import json
import pygame

import neopixel
import RPi.GPIO as gpio
from MSR_HAL import povserial
import MSR_OS.floatCanvas as fc


# neopixels
# LED strip configuration:
LED_COUNT      = 5       # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

# GPIO, audio relay
GPIO_RELAY = 23

_strip = None
_display = None
_activeLUT = None
_defaultLUTs = {'off': None, 'default': None}

_screenW = 16
_screenH = 18

def platform():
    """
    :return (string): returns the name of the platform
    """
    return "circadia sunrise lamp"



def init(system, config):
    """
    bring the hardware online
    :param system (dict): global settings and handy objects
    :param config (dict): preferences in a global dictionary
    """

    # update system settings

    global _screenW
    global _screenH
    cfg = config['platform_cfg']['raspi']
    system["theme_path"] = cfg['themebasepath']
    _screenW = system["screen_width"] = cfg['screen_width'] # this is specific to this hardware anyway
    _screenH = system["screen_height"] = cfg['screen_height']

    global _display
    _display = povserial.pov(cfg)

    # setup gpios
    gpio.setmode(gpio.BCM)
    # pin GPIO23 is connected to the sound relay
    gpio.setup(GPIO_RELAY, gpio.OUT, initial=gpio.LOW)

    # Create NeoPixel object with appropriate configuration.
    global _strip
    _strip = neopixel.Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
    _strip.begin()


    pygame.mixer.pre_init(frequency=41000, channels=1, buffer=4096*2)
    pygame.init()
    pygame.mixer.set_num_channels(16)


    if 'forceDisplayWindow' in system:  # for debugging
        pygame.display.set_mode((160, 180))

    _display.set_rpm(80)
    _display.secondsDisplay(False)
    _display.clear()

    __init_lut(system)
    system['canvas'] = fc.Canvas(w=_screenW, h=_screenH)

    print 'sys lamp: init done.'


def getScreenDimensions():
    return ( _screenW, _screenH )


def __init_lut(system):
    """
    load the system luts (gamma_grad.json)
    :param system (dict): global settings and handy objects
    """

    global _activeLUT
    global _defaultLUTs
    lut_path = 'gamma_grad.json'
    lut_file = open(lut_path, "r")

    if not lut_file:
        print "couldn't open lut file", lut_path
        #system['lut'] = None
    else:
        lutjson = json.load(lut_file)
        lut_file.close()
        lut = fc.Gradient3(lutjson['gamma']).toGradient1()
        print 'LUT loaded'
        _activeLUT = lut
        _defaultLUTs['default'] = lut
        return lut

    return None


def switchLut(lutName):
    """
    select a named lut, if it exists in the system
    :param lutName (string): name of the lut
    """

    global _activeLUT
    global _defaultLUTs
    if lutName in _defaultLUTs:
        _activeLUT = _defaultLUTs[lutName]
    else:
        print 'manulahw: undefined lut "%s"'%lutName


def audio_on():
    """
    bring the audio subsystem online
    """

    # resetting mixer
    pygame.mixer.init()
    gpio.output(GPIO_RELAY, gpio.HIGH)  # toggle the relais pin


def audio_off():
    """
    switch the audio subsystem off
    """

    gpio.output(GPIO_RELAY, gpio.LOW) # toggle the relais pin
    pygame.mixer.quit()


def audio_fadeout(fadetime):
    """
    fade out all currently playing sound effects
    :param fadetime (float): time in seconds
    """
    pygame.mixer.fadeout(fadetime)


def shutdown():
    """
    switch the system off
    """

    global _strip
    for i in range(_strip.numPixels()):
        _strip.setPixelColor(i, neopixel.Color(0,0,0) )
    _strip.show()

    audio_off()
    gpio.cleanup()

    print 'sys lamp: shut down.'


def update_screen(surface):
    """
    update the screen with a given canvas
    :param surface floatCanvas): source canvas
    """

    global _activeLUT
    ps = surface.toPygameSurface(_activeLUT)
    global _strip
    for x in xrange(_screenW):
        for y in xrange(_screenH):
            col = ps.get_at((x,y))
            if x%2==0:
                ind = _screenH-y-1 + x*_screenH
            else:
                ind = y + x*_screenH
            #_strip.setPixelColorRGB(ind, col[0],col[1],col[2] )
            _strip.setPixelColorRGB(ind, col[1], col[0], col[2] ) # green&red are swapped for some reason in this version of rpi_ws281x
    _strip.show()


def setTime(hour, minute, second):
    """ update the clock time
    :param hour (int): hours (24h format)
    :param minute (int): minutes
    :param second (int): seconds
    """

    global _display
    _display.setTime(hour, minute, second)


def switchClock(onoff, alarmSymbol, scrollOverride=False):
    """
    changes the mode of the clock display, from time to text
    :param onoff (bool): True=Time mode False=Text Display
    :param alarmSymbol (bool): indicates whether the alarm is set when in clock mode (alarm symbol is drawn)
    :param scrollOverride (bool): indicates whether the scrolling will be stopped when in text mode
    """

    global _display
    if onoff:
        _display.switchToClock()
        _display.start_scroll()
        #_display.set_scroll_speed(2)
        if alarmSymbol:
            _display.textPos(40, '%c'%148)
            _display.textPos(112, '%c'%148)
            _display.textPos(184, '%c'%148)
    else:
        _display.switchToDisplay()
        #_display.set_scroll_speed(1)
        if not scrollOverride:
            _display.stop_scroll()
        else:
            _display.start_scroll()


def textOut(txt, center=False):
    """
    prints text on the clock display
    :param txt (string): text
    :param center (bool): center the text
    :return:
    """
    global _display

    txt = txt[:36]
    # add padding to place the text in the middle of the buffer
    if center:
        pad = (36 - len(txt))/2
        txt = txt.rjust(pad+len(txt), ' ')

    _display.text(txt)


def incMagLock():
    """
    rotate the text display
    """
    global _display
    _display.incMagLock()


def getEvent():
    """
    retrieve events from the clock, such as button clicks
    :return (tuple): (string(messageName), messageParam0, ...)
    """

    _display.handleRx()
    msg = _display.getNextMessage()
    if msg:
        #print list(msg)
        if msg[0] == ord('B'): # button pressed (and released, actually)
            return ('buttonClick', msg[1])
        if msg[0] == ord('H'): # a held button sends a repeated H+timecode message
            return ('buttonHold', msg[1], (((msg[3]-1)<<7) + msg[2]))

    return None



__author__ = "fhu"
