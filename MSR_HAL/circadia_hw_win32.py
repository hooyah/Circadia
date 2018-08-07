"""
    Circadia Sunrise Lamp - windows HAL emulation

    hardware abstraction layer running on win32

    Author: fhu
"""
import pygame
from MSR_OS.floatCanvas import Canvas
import time

def platform():
    """
    :return (string): returns the name of the platform
    """
    return "Windows"


def init(system, config):
    """
    bring the hardware online
    :param system (dict): global settings and handy objects
    :param config (dict): preferences in a global dictionary
    """

    # update system settings
    cfg = config['platform_cfg']['win32']

    system["theme_path"] = cfg['themebasepath']
    system["screen_width"] = cfg['screen_width']
    system["screen_height"] = cfg['screen_height']

    # init pygame
    pygame.mixer.pre_init(frequency=41000)
    pygame.init()
    pygame.mixer.set_num_channels(16)

    print 'opening window %dx%d' % (system['screen_width'], system['screen_height'])
    pygame.display.set_mode((160, 180))
    # start clocks
    # init pov
    # set time

    #system['lut'] = Gradient3().toGradient1()
    system['canvas'] = Canvas(w=16, h=18)

    print 'sys windows: init done.'


def getScreenDimensions():
    bg = pygame.display.get_surface()
    return ( int(bg.get_width()), int(bg.get_height()) )


def cfg_display():
    """"
    set up the display to work as needed
    separate from init because this has to be done after the display has spooled up
    """
    pass


def switchLut(lutName):
    """
    select a named lut, if it exists in the system
    :param lutName (string): name of the lut
    """
    pass


def audio_on():
    """
    bring the audio subsystem online
    """
    pygame.mixer.init()


def audio_off():
    """
    switch the audio subsystem off
    """
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
    pygame.display.quit()
    pygame.quit()
    print 'sys windows: shut down.'


def update_screen(surface):
    """
    update the screen with a given canvas
    :param surface (floatCanvas): source canvas
    """
    bg = pygame.display.get_surface()
    ps = surface.toPygameSurface()
    pygame.transform.scale(ps, (bg.get_width(), bg.get_height()), bg)

    pygame.display.flip()


def setTime(hour, minute, second):
    """ update the clock time
    :param hour (int): hours (24h format)
    :param minute (int): minutes
    :param second (int): seconds
    """
    pass


def switchClock(onoff, alarmSymbol):
    """
    changes the mode of the clock display, from time to text
    :param onoff (bool): True=Time mode False=Text Display
    :param alarmSymbol (bool): indicates whether the alarm is set when in clock mode (alarm symbol is drawn)
    :param scrollOverride (bool): indicates whether the scrolling will be stopped when in text mode
    """
    print "clock",onoff

def displayOn(onoff):
    """
    Switch display on or off
    :param onoff (bool): on or off
    :return: none
    """

    if onoff:
        print "display on"
    else:
        print "display off"


def textOut(txt, center=False):
    """
    prints text on the clock display
    :param txt (string): text
    :param center (bool): center the text
    :return:
    """
    txt = txt[:36]
    # add padding to place the text in the middle of the buffer
    if center:
        pad = (36 - len(txt))/2
        txt = txt.rjust(pad+len(txt), ' ')
    print '|',txt,'|'


def incMagLock():
    """
    rotate the text display
    """
    pass


__but1=0
__but2=0
__but4=0
def getEvent():
    """
    retrieve events from the clock, such as button clicks
    :return (tuple): (string(messageName), messageParam0, ...)
    """

    global __but1, __but2, __but4
    now = time.clock()

    for event in pygame.event.get():
        #print event
        if event.type == pygame.QUIT:
            return ('end', 0)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return ('end', 0)
            """            elif event.key == 44:  # ','
                __but1 = now
                return None
            elif event.key == 46:  # '.'
                __but2 = now
                return None
            elif event.key == 47:  # '/'
                __but4 = now
                return None
            #elif event.type == pygame.KEYDOWN:
            #    print event.key
        elif event.type == pygame.KEYUP:
            print __but1, __but2, __but4
            if event.key == 44 and (now - __but1) < 1:  # ','
                __but1=0
                return ('buttonClick', 1)
            elif event.key == 46 and (now - __but2) < 1:  # '.'
                __but2=0
                return ('buttonClick', 2)
            elif event.key == 47 and (now - __but4) < 1:  # '/'
                __but4=0
                return ('buttonClick', 4)

            """
            # print event.key # to figure out what code belongs to which key
        

    keystate = pygame.key.get_pressed()
    keys = 1 if (__but1 > 0) else 0
    keys |= 2 if (__but2 > 0) else 0
    keys |= 4 if (__but4 > 0) else 0
    m = max(max(__but1, __but2), __but4)
    hold = False
    if keystate[44]:
        if not __but1:
            __but1 = now
            return None
        elif now-__but1>2:
            hold = True
    else:
        if __but1:
            __but1=0
            return ('buttonClick', 1)
        __but1=0
    if keystate[46]:
        if not __but2:
            __but2 = now
            return None
        elif now-__but2>2:
            hold = True
    else:
        if __but2:
            __but2=0
            return ('buttonClick', 2)
        __but2=0
    if keystate[47]:
        if not __but4:
            __but4 = now
            return None
        elif now-__but4>2:
            hold = True
    else:
        if __but4:
            __but4=0
            return ('buttonClick', 4)
        __but4=0

    if hold:
        return ('buttonHold', keys, now - m)
    else:
        return None



__author__ = "fhu"