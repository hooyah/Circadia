"""
    Circadia Sunrise Lamp - Sound module(s)

    Author: fhu
"""

import random
import os.path
import pygame
from MSR_OS import modbase




class wav_module(modbase.SModule):
    """ plays back a sound file, optionally at random intervals or cross fading infinitely """

    def __init__(self, basepath, moduleDef):

        modbase.SModule.__init__(self, moduleDef)
        params = moduleDef['params']
        self.filename = basepath+params['file']
        if not os.path.isfile(self.filename):
            print 'wav_module error: sound not found "%s"'%params['file']
        self.pg_sound = pygame.mixer.Sound(self.filename)
        self.soundLen = self.pg_sound.get_length()
        self.pg_channels = [None, None]
        self.mode = params['mode'] if 'mode' in params else 'loop'
        self.repeatTime = params['repeatEvery'] if 'repeatEvery' in params else [0.0,0.0]
        self.randGainMin = params['randGain'][0] if 'randGain' in params else 1.0
        self.randGainMax = params['randGain'][1] if 'randGain' in params else 1.0
        self.randGain = 1.0

        self.nextTime = -1
        self.clipTimes = [None, None]
        self.xfade = params['xfade'] if 'xfade' in params else 4
        self.xfade = min(self.xfade, self.soundLen/2.1)

        # build a crossfade envelope
        self.xfade_env = modbase.Envelope(keys=[(0.0,0.0),(self.xfade, 1.0), (self.soundLen-self.xfade, 1.0), (self.soundLen, 0)], logarithmic=False)


    def reset(self):
        modbase.SModule.reset(self)
        self.clipTimes = [None, None]
        self.nextTime = -1
        self.randGain = 1.0


    def dbg_sound(self, msg):
        print '-----------no channel returned---------------', msg
        print 'numchan:', pygame.mixer.get_num_channels()
        print 'mixer:', pygame.mixer.get_init()
        print 'mixer_busy:', pygame.mixer.get_busy()
        print 'file:', self.filename
        print self.pg_sound
        #lets_crash_here
        #raise("meh")

    def tick(self, timeInt):

        volume = self.envelope.eval(timeInt.elapsedNormalized()) * self.max_volume
        #self.pg_sound.set_volume(vol)

        stillPlaying = True
        if self.pg_channels[0] != None:
            snd = self.pg_channels[0].get_sound()
            if snd != self.pg_sound:
                stillPlaying = False
        else:
            stillPlaying = False


        if self.mode == 'loop':

            if not stillPlaying:
                if self.nextTime < 0 or volume == 0.0:
                    self.nextTime = timeInt.time + random.uniform(self.repeatTime['min'], self.repeatTime['max'])
                if timeInt.time > self.nextTime and volume > 0:
                    self.nextTime += self.soundLen + random.uniform(self.repeatTime['min'], self.repeatTime['max'])
                    #print self.repeatTime['min'], self.repeatTime['max']
                    self.pg_channels[0] = self.pg_sound.play()

                    if self.pg_channels[0] == None:
                        self.dbg_sound('xfadeA')
                    else:
                        self.randGain = random.uniform(self.randGainMin, self.randGainMax)
                        #print timeInt.elapsedSeconds()
                        stillPlaying = True

            if stillPlaying:
                self.pg_channels[0].set_volume(volume * self.randGain)

        elif self.mode == 'xfade':

            # noting is playing yet
            if not self.clipTimes[0]:
                self.pg_channels[0] = self.pg_sound.play()
                if self.pg_channels[0] == None:
                    self.dbg_sound('xfadeA')
                else:
                    self.clipTimes[0] = modbase.timeInterval(timeInt.time, self.soundLen)
                    self.pg_channels[0].set_volume(0)
                    #print 'playing channel A'

            else: # playing A channel

                elapsedA = self.clipTimes[0].elapsedSeconds(timeInt.time)
                if  elapsedA >= self.soundLen: # channel A is done
                    self.clipTimes[0] = self.clipTimes[1]
                    self.clipTimes[1] = None
                    self.pg_channels[0] = self.pg_channels[1]
                    self.pg_channels[1] = None

                elif not self.clipTimes[1] and (self.soundLen-elapsedA) <= self.xfade:

                    self.pg_channels[1] = self.pg_sound.play()
                    if self.pg_channels[1] == None:
                        self.dbg_sound('xfadeB')
                    else:
                        self.pg_channels[1].set_volume(0)
                        self.clipTimes[1] = modbase.timeInterval(timeInt.time, self.soundLen)
                        #print 'playing channel B'

                if self.pg_channels[0]:
                    self.pg_channels[0].set_volume( self.xfade_env.eval(elapsedA) * volume )
                if self.clipTimes[1]:
                    elapsedB = self.clipTimes[1].elapsedSeconds(timeInt.time)
                    self.pg_channels[1].set_volume( self.xfade_env.eval(elapsedB) * volume )

        return True



__author__ = 'florian'
