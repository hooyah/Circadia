"""
    Circadia Sunrise Lamp - Implementation

    Author: fhu
"""

import os, sys
import random
import time, datetime
import MSR_OS.engine as MSR
from MSR_OS.modbase import timeInterval


# globals, defaults

# todo: (re)store this in a cfg file
alarm_enabled = True
alarm_time_hour = 6
alarm_time_minute = 50
alarm_length = 30 # length of the theme in minutes
alarm_post = 30  # how long the alarm keeps going after it's fully ramped on in minutes

dbg_alarm_override = False
alarm_intermediate = None
dsp_on = False

but_left = 1
but_middle = 2
but_right = 4







# Menu ------------------------------------------------------------------------------------
# minimal menu
# current behaviour: any button click will bring up the menu
# left button will enable/disable the alarm
# middle button will change the alarm time
# right button will run the current theme in demo mode (sped up to 2 minutes)
# holding the left or right button while in the main menu will start rotating the display
# holding the middle button will shut down the display
# 5 seconds of inactivity will exit the menu

def __handle_menu():
    """
    this function handles the menu
    """

    global alarm_enabled, alarm_time_hour, alarm_time_minute, dsp_on
    menu = "top"
    MSR.sys_hw.switchClock(False, alarm_enabled) # switch to display

    if not dsp_on:  # switch the display on before we continue
        menu = "dispOn"

    while menu != "exit":

        if menu == "top":
            # main menu

            MSR.sys_hw.textOut("alrm tm prf", center=True)

            lasttime = time.time()
            while True:

                event = MSR.sys_hw.getEvent()
                if event:
                    if event[0] == "end":
                        menu = "exit"
                        break
                    elif event[0] == "buttonClick" and (event[1] & but_left) and dsp_on:
                        menu = "alarmToggle"
                        break
                    elif event[0] == "buttonClick" and (event[1] & but_right) and dsp_on:
                        print "horray, alarm"
                        global dbg_alarm_override
                        dbg_alarm_override = True
                        menu = "exit"
                        break
                    elif event[0] == "buttonClick" and (event[1] & but_middle) and dsp_on:
                        menu = "setAlarmTime"
                        break
                    elif event[0] == "buttonHold" and (event[1] & (but_left|but_right)) and dsp_on:
                        # holding down the left or right button will rotate the display
                        menu = "magLock"
                        break
                    elif event[0] == "buttonHold" and (event[1] & but_middle) and dsp_on:
                        # holding down the middle button will switch off the clock display
                        menu = "dispOff"
                        break

                if time.time() - lasttime > 5:
                    menu = "exit"
                    break

        elif menu == "magLock":
            # rotate the display one mag lock at a time until button is released

            MSR.sys_hw.textOut("_  _  _  |  _  _  _", center=True)
            lasttime = time.time()
            while True:

                event = MSR.sys_hw.getEvent()
                if event:
                    if event[0] == "buttonHold" and time.time() - lasttime > 0.5:
                        MSR.sys_hw.incMagLock()
                        lasttime = time.time()
                        continue
                    elif event[0] == "buttonClick":
                        menu = "top"
                        break

                if time.time() - lasttime > 5:  # missed end of buttonHold
                    menu = "top"
                    break


        elif menu == "dispOff":

            MSR.sys_hw.displayOn(False)
            dsp_on = False

            #wait for button release
            time.sleep(2)
            while MSR.sys_hw.getEvent():
                pass

            menu = "exit"

        elif menu == "dispOn":

            MSR.sys_hw.displayOn(True)
            dsp_on = True
            MSR.addCallback(__initDisplayCb, param=None, delay=30, perpetual=False)
            time.sleep(5)
            #print "display ramping on"
            #wait for button release
            while MSR.sys_hw.getEvent():
                pass

            menu = "exit"


        elif menu == "alarmToggle":

            MSR.sys_hw.textOut("alarm on" if alarm_enabled else "alarm off", center=True)
            lasttime = time.time()
            while True:

                event = MSR.sys_hw.getEvent()
                if event:
                    if event[0] == "end":
                        menu = "exit"
                        break
                    elif event[0] == "buttonClick" and (event[1] & but_left):
                        alarm_enabled = not alarm_enabled
                        lasttime = time.time()
                        MSR.sys_hw.textOut("alarm on" if alarm_enabled else "alarm off", center=True)
                    elif event[0] == "buttonClick" and not (event[1] & but_left):
                        menu = "top"
                        break

                if time.time() - lasttime > 2.5:
                    if alarm_enabled:
                        MSR.sys_hw.textOut("alarm ON %2d:%02d"%(alarm_time_hour, alarm_time_minute), center=True)
                        time.sleep(2)
                    menu = "exit"
                    break

        elif menu == "setAlarmTime":
            MSR.sys_hw.textOut("alarm> %2d:%02d"%(alarm_time_hour, alarm_time_minute), center=True )
            lasttime = time.time()
            changed = False
            while True:
                event = MSR.sys_hw.getEvent()
                offs = 0
                if event:
                    if event[0] == "end":
                        menu = "exit"
                        break
                    elif (event[0] == "buttonClick" or event[0] == "buttonHold") and (event[1] & but_middle): #dec time
                        offs = -5
                    elif (event[0] == "buttonClick" or event[0] == "buttonHold") and (event[1] & but_right):  #inc time
                        offs = 5

                    if offs:
                        tm = alarm_time_hour * 60 + alarm_time_minute
                        tm = (tm + offs) % (24*60)
                        alarm_time_minute = int(tm % 60)
                        alarm_time_hour = int(tm / 60)
                        MSR.sys_hw.textOut("alarm> %2d:%02d" % (alarm_time_hour, alarm_time_minute), center=True)
                        lasttime = time.time()
                        changed = True

                if time.time() - lasttime > 3:
                    if changed:
                        # save in settings file
                        pass
                    if alarm_enabled:
                        MSR.sys_hw.textOut("alarm ON %2d:%02d"%(alarm_time_hour, alarm_time_minute), center=True)
                        time.sleep(2)
                    menu = "exit"
                    break
                time.sleep(0.1)


    MSR.sys_hw.switchClock(True, alarm_enabled) # return to clock display





def __setTime():
    """
    set display to clock mode and set the current time
    """
    now = datetime.datetime.now()
    MSR.sys_hw.setTime(now.hour, now.minute, now.second)


def __updateTimeCb(arg):
    """
    callback that updates the system time periodically
    :param arg: Nothing
    :return: none
    """

    print 'updateTime', datetime.datetime.now()
    __setTime()
    #MSR.addCallback(__updateTimeRecCb, None, 3600 * 3)


def __initDisplayCb(arg):
    """
    callback that initializes the display when it comes back from sleep
    :param arg: Nothing
    :return: none
    """

    print 'initDisplayCb', datetime.datetime.now()
    __setTime()
    MSR.sys_hw.cfg_display()
    MSR.sys_hw.switchClock(1, alarm_enabled)






# --------------- Main --------------------------------------------------------------------------

def main(themeName=None):
    """
    run the clock
    usually only returns in win32 mode or with CTRL-C in the shell
    :param themeName: can be called with a specific theme name, otherwise a random theme is chosen
    """

    global alarm_length
    global dbg_alarm_override
    global alarm_intermediate
    global dsp_on
    alarm_autothemes = True

    print 'running on', MSR.sys_hw.platform()
    p,n = os.path.split(os.path.abspath(__file__))
    cfg_path = p+os.sep+'circadia_cfg.json'
    config = MSR.loadConfig(cfg_path)
    prefs = dict()
    MSR.sys_hw.init(prefs, config)
    MSR.setPrefs(prefs)

    if themeName:
        alarm_currentTheme = MSR.loadTheme(themeName)
        alarm_autothemes = False
    else:
        alarm_currentTheme = MSR.loadTheme( random.choice(config['autoThemes']) )


    MSR.sys_hw.audio_off()
    __setTime()
    MSR.sys_hw.switchClock(1, alarm_enabled)
    MSR.addCallback(__initDisplayCb, param=None, delay=15, perpetual=False)  # update the time in 10s
    MSR.addCallback(__updateTimeCb, param=None, delay=3600 * 3, perpetual=True)  # then every 3h
    dsp_on = True



    # main event loop
    running = True
    state = "init"
    alarmInterval = 0
    alarmHysteresis = False
    alarm_fade = 0
    try:
        while(running):

            #print state
            if state == "init":

                state = "idle"


            elif state == "idle":

                # do mostly nothing
                time.sleep(.3)

                MSR.pollCallbacks()
                event =  MSR.sys_hw.getEvent()
                if event:
                    if event[0] == "end":
                        state = "shutdown"
                    elif event[0] == "buttonClick":
                        state = "menu"

                now = datetime.datetime.now()
                #print now

                # alarm ?
                if now.hour == alarm_time_hour and now.minute == alarm_time_minute:
                    if alarm_enabled and not alarmHysteresis:
                        state = "start alarm"
                        alarmHysteresis = True
                else:
                    alarmHysteresis = False

                # debug
                if dbg_alarm_override:
                    dbg_alarm_override = False
                    state = "start alarm"
                    alarm_intermediate = alarm_length
                    alarm_length = 2



            elif state == "start alarm":

                alarmInterval = timeInterval(time.time(), alarm_length*60)
                MSR.reset_audioVideo()
                MSR.sys_hw.audio_on()
                if not dsp_on:
                    MSR.sys_hw.displayOn(True)
                    dsp_on = True
                    MSR.addCallback(__initDisplayCb, None, 20)
                state = "alarm"


            elif state == "alarm":

                elapsed = alarmInterval.elapsed(time.time())

                MSR.handle_audioVideo(elapsed)
                MSR.pollCallbacks()
                time.sleep(0.005)

                event = MSR.sys_hw.getEvent()
                if event:
                    if event[0] == 'end':
                        state = "shutdown"
                    elif event[0] == 'buttonClick':
                        state = 'end alarm'
                        alarm_fade = 0
                        MSR.sys_hw.audio_fadeout(1000)

                if elapsed.elapsedSeconds() >= (alarm_length+alarm_post)*60: # ramp up is done
                    print 'theme done.'
                    print 'elapsed %f s'%elapsed.elapsedSeconds()
                    state = "end alarm"
                    alarm_fade = 0
                    MSR.sys_hw.audio_fadeout(1000)


            elif state == "end alarm":

                if alarm_fade < 51:

                    MSR.fadeOut(alarm_fade/50.0)
                    time.sleep(0.02)
                    alarm_fade += 1
                else:

                    MSR.fadeOut(1.0)

                    if alarm_autothemes:
                        thm = config['autoThemes']
                        current = thm.index(alarm_currentTheme)
                        nextChoice = (current+1)%len(thm)
                        alarm_currentTheme = MSR.loadTheme( thm[nextChoice] )

                    if alarm_intermediate: # restore the alarm length
                        alarm_length = alarm_intermediate
                        alarm_intermediate = None
                        dbg_alarm_override = False

                    MSR.sys_hw.audio_off()
                    state = "idle"


            elif state == "menu":

                __handle_menu()
                state = "idle"

            elif state == "shutdown":

                break


    except KeyboardInterrupt:
        pass

    MSR.sys_hw.shutdown()






# cmd line
if __name__ == "__main__":

    themeName = None

    if "--PREVIEW" in sys.argv:
        dbg_alarm_override = True
        sys.argv.remove("--PREVIEW")
        print "entering demo mode"

    if len(sys.argv) > 1:
        themeName = sys.argv[1]

    main(themeName)


__author__ = "fhu"
