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

dbg_alarm_override = True
alarm_intermediate = None

but_left = 1
but_middle = 2
but_right = 4


# Menu ------------------------------------------------------------------------------------
# minimal menu
# current behaviour: any button click will bring up the menu
# left button will enable/disable the alarm
# right button will run the current theme in demo mode (sped up to 2 minutes)
# holding any button while in the main menu will start rotating the display (pov display only)
# 5 seconds of inactivity will exit the menu

def __handle_menu():
    """
    poll this function to handle button clicks
    """

    global alarm_enabled, alarm_time_hour, alarm_time_minute
    menu = "top"
    MSR.sys_hw.switchClock(False, alarm_enabled) # switch to display

    while menu != "exit":

        if menu == "top":
            # main menu

            MSR.sys_hw.textOut("alrm tm prf", center=True)

            lasttime = time.clock()
            while True:

                event = MSR.sys_hw.getEvent()
                if event:
                    if event[0] == "end":
                        menu = "exit"
                        break
                    elif event[0] == "buttonClick" and (event[1] & but_left):
                        menu = "alarmToggle"
                        break
                    elif event[0] == "buttonClick" and (event[1] & but_right):
                        print "horray, alarm"
                        global dbg_alarm_override
                        dbg_alarm_override = True
                        menu = "exit"
                        break
                    elif event[0] == "buttonHold":
                        menu = "magLock"
                        break

                if time.clock() - lasttime > 5:
                    menu = "exit"
                    break

        elif menu == "magLock":
            # rotate the display one mag lock at a time until button is release

            MSR.sys_hw.textOut(".", center=True)
            lasttime = time.clock()
            while True:

                event = MSR.sys_hw.getEvent()
                if event:
                    if event[0] == "buttonHold" and time.clock() - lasttime > 0.5:
                        MSR.sys_hw.incMagLock()
                        lasttime = time.clock()
                        continue
                    elif event[0] == "buttonClick":
                        menu = "top"
                        break

                if time.clock() - lasttime > 5: # missed end of buttonHold
                    menu = "top"
                    break



        elif menu == "alarmToggle":

            MSR.sys_hw.textOut("alarm on" if alarm_enabled else "alarm off", center=True)
            lasttime = time.clock()
            while True:

                event = MSR.sys_hw.getEvent()
                if event:
                    if event[0] == "end":
                        menu = "exit"
                        break
                    elif event[0] == "buttonClick" and (event[1] & but_left):
                        alarm_enabled = not alarm_enabled
                        lasttime = time.clock()
                        MSR.sys_hw.textOut("alarm on" if alarm_enabled else "alarm off", center=True)
                    elif event[0] == "buttonClick" and not (event[1] & but_left):
                        menu = "top"
                        break

                if time.clock() - lasttime > 2.5:
                    if alarm_enabled:
                        MSR.sys_hw.textOut("alm ON % 2d:%02d"%(alarm_time_hour, alarm_time_minute), center=True)
                        time.sleep(2)
                    menu = "exit"
                    break



    MSR.sys_hw.switchClock(True, alarm_enabled) # return to clock display





def __setTime():
    """
    set display to clock mode and set the current time
    """
    now = datetime.datetime.now()
    MSR.sys_hw.setTime(now.hour, now.minute, now.second)




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
    alarm_autothemes = True
    alarm_currentTheme = None

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
    __setTime()



    # main event loop
    running = True
    state = "init"
    alarmInterval = 0
    alarmHysteresis = False
    idle_timer = 0
    alarm_fade = 0
    try:
        while(running):

            #print state
            if state == "init":

                state = "idle"


            elif state == "idle":

                # do mostly nothing
                time.sleep(.3)

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

                idle_timer += 1
                if idle_timer > 3600*3:
                    print 'setTime', datetime.datetime.now()
                    __setTime()
                    idle_timer = 0


            elif state == "start alarm":

                alarmInterval = timeInterval(time.time(), alarm_length*60)
                MSR.reset_audioVideo()
                MSR.sys_hw.audio_on()
                state = "alarm"


            elif state == "alarm":

                elapsed = alarmInterval.elapsed(time.time())

                MSR.handle_audioVideo(elapsed)
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
    print sys.argv
    if len(sys.argv) > 1:
        themeName = sys.argv[1]

    main(themeName)


__author__ = "fhu"
