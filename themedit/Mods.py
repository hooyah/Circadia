"""
    Circadia Theme Editor - graphics/sound module implementations

    Gradient, ImgShift, Wav

    Author: fhu

"""

import os, copy, shutil
import Tkinter as tk
import pygame
import tkFileDialog, ttk
from ModBase import Module_base
from Utils.TkGradientEdit import GradientEdit
from MSR_OS.floatCanvas import Gradient3, Gradient4
from MSR_OS.modbase import Envelope






########## ModGradient ############################################################################################
################################################################################################################
################################################################################################################

class ModGradient(Module_base):
    """
    Creates a simple gradient that can animate over time
    """

    def __init__(self, modParams, basepath, parentColors, hash, client=None):
        Module_base.__init__(self, modParams, basepath, parentColors, hash, client)
        self.colorScheme['background']='#68aa83'
        self.colorScheme['highlightbackground'] = '#3e664e'
        self.envelopeScheme = {'fill':'#4e8063', 'outline':'#2f4d3c'}
        self.addModKeys(self.params['params']['keys'])
        self.gradientParams = None

    @staticmethod
    def moduleCategory():

        return 'graphics'

    @staticmethod
    def defaults():

        return {    "mod" : "gradient",
                    "name": "gradient",
                    "params" : {
                        "keys" : [
                            { "time" : 0.0, "grad" : [ [ 0.0, [0.0,0.0,0.0] ] ]},
                        ]
                    },
                    "envelope" : {
                        "type" : "lin",
                        "keys" : [
                            {"time":0.0, "val":1.0},
                            {"time":1.0, "val":1.0}
                        ]
                    }
               }

    def saveInto(self, trgDict, trgPath):

        self.updateEnvKeys()
        trgDict.append( self.params )


    def supportsModKeys(self):

        return True


    def addModKey(self, atTime):

        key = { "time" : atTime, "grad" : [ [ 0.0, [0.0,0.0,0.0] ] ]}
        self.params['params']['keys'].append(key)
        return key

    def buildModKeyParams(self, parent, colScheme):

        grad = self.params['params']['keys'][0]['grad']
        self.gradientParams = GradientEdit(parent, grad, callback=self.__grad_cb, colScheme=colScheme)
        self.gradientParams.pack()

    def updateModKeyParams(self, key):

        if self.gradientParams:
            self.gradientParams.setGradient(key['grad'])

    def destroyModKeyParams(self):

        if self.gradientParams:
            self.gradientParams.destroy()
            self.gradientParams = None


    def updated(self):
        self.drawGradientBackdrop()


    def __grad_cb(self, params):

        if self.lampClient and self.lampClient.isConnected():

            grad = Gradient3(params)
            h = self.lampClient.canvasH
            prm = [ grad.eval(float(i) / (h-1)) for i in xrange(h) ]
            self.lampClient.sendGradient(prm)


    def drawGradientBackdrop(self):


        image = self.backDropImg
        w = image.width()
        h = image.height()/2

        grad = Gradient4( self.params['params']['keys'] )

        lines = list()
        for y in xrange(h):
            yvar = y/float(h-1)
            line = list()
            for x in xrange(w):
                xvar = x/float(w-1)
                col = grad.eval(xvar, yvar)
                line.append( '#%02x%02x%02x'%(col[0]*255, col[1]*255, col[2]*255) )
            lines.append("{"+ " ".join(line)+"}")

        self.backDropImg.put(" ".join(lines), (0,0))


    def updateCanvas(self, fc):

        w = fc.width
        h = fc.height
        grad = Gradient4( self.params['params']['keys'] )
        for y in xrange(h):
            r,g,b = grad.eval(self.time, float(y)/(h-1))
            fc.drawLineH(y, r,g,b)






########## ModShift ############################################################################################
################################################################################################################
################################################################################################################

class ModShift(Module_base):
    """
    Loads an image file and moves it across the screen.
    """

    def __init__(self, modParams, basepath, parentColors, hash, client=None):
        Module_base.__init__(self, modParams, basepath, parentColors, hash, client)
        self.colorScheme['background']='#68aa83'
        self.colorScheme['highlightbackground'] = '#3e664e'
        self.envelopeScheme = {'fill':'#4e8063', 'outline':'#2f4d3c'}
        self.paramFrame = None
        self.imgFullPath = basepath + os.sep + self.params['params']['file']
        self.img = None

    @staticmethod
    def moduleCategory():

        return 'graphics'

    @staticmethod
    def defaults():

        return {    "mod": "imgShift",
                    "name": "shifter",
                    "params": {
                        "file": "image.jpg",
                        "offset": [ 0.0, 0.0 ],
                        "speed" : [ 0.0, 0.0],
                        "oversampling": 4
                    },
                    "envelope" : {
                        "type" : "lin",
                        "keys" : [
                            {"time":0.0, "val":1.0},
                            {"time":1.0, "val":1.0}
                        ]
                    }
               }



    def buildParameters(self, parent, colScheme):

        Module_base.buildParameters(self, parent, colScheme)

        self.var_filePath = self.stringVar( self.params['params']['file'] )
        self.var_offMin = self.stringVar( self.params['params']['offset'][0] )
        self.var_offMax = self.stringVar( self.params['params']['offset'][1] )
        self.var_speedMin = self.stringVar( self.params['params']['speed'][0] )
        self.var_speedMax = self.stringVar( self.params['params']['speed'][1] )
        self.var_oversampling = self.stringVar( self.params['params']['oversampling'] )


        self.paramFrame = tk.LabelFrame(parent, text="Parameters", padx=8, pady=8, **colScheme)
        self.paramFrame.pack(anchor='nw', fill='x', expand='yes')


        helper = tk.Frame(self.paramFrame, **colScheme)
        helper.pack(fill='x', expand='yes')
        self.filePath = tk.Entry(helper, textvariable=self.var_filePath, **colScheme)
        self.filePath.pack(side='left', fill='x', expand='yes')
        browseFile = tk.Button(helper, text='..', command=self.selectFile, **colScheme)
        browseFile.pack(side='left')


        helper = tk.Frame(self.paramFrame, **colScheme)
        helper.pack(fill='x', pady=8)
        tk.Label(helper, text='offset X', **colScheme).pack(side='left')
        self.offsetMinWgt = tk.Entry(helper, width=6, textvariable=self.var_offMin, **colScheme)
        self.offsetMinWgt.pack(side='left')
        tk.Label(helper, text='Y', **colScheme).pack(side='left')
        self.offsetMaxWgt = tk.Entry(helper, width=6, textvariable=self.var_offMax, **colScheme)
        self.offsetMaxWgt.pack(side='left')


        helper = tk.Frame(self.paramFrame, **colScheme)
        helper.pack(fill='x', pady=8)
        tk.Label(helper, text='Speed X', **colScheme).pack(side='left')
        self.speedMinWgt = tk.Entry(helper, width=6, textvariable=self.var_speedMin, **colScheme)
        self.speedMinWgt.pack(side='left')
        tk.Label(helper, text='Y', **colScheme).pack(side='left')
        self.speedMaxWgt = tk.Entry(helper, width=6, textvariable=self.var_speedMax, **colScheme)
        self.speedMaxWgt.pack(side='left')

        helper = tk.Frame(self.paramFrame, **colScheme)
        #helper.pack(fill='x', pady=8, anchor='w')
        helper.pack(fill='x', pady=8)
        tk.Label(helper, text='oversampling', **colScheme).pack(side='left')
        self.oversamplingWgt = tk.Entry(helper, width=6, textvariable=self.var_oversampling, **colScheme)
        self.oversamplingWgt.pack(side='left')

        self.collectorCb = self.collectorShiftParams

    def destroyParameters(self):

        if self.paramFrame:
            self.paramFrame.destroy()
        Module_base.destroyParameters(self)

    def selectFile(self):

        file = tkFileDialog.askopenfilename(title='select image file', initialfile=self.params['params']['file'], filetypes=[('JPEG','*.jpg'),('PNG','*.png')])
        if file and os.path.isfile(file):
            self.imgFullPath = file
            self.var_filePath.set( os.path.basename(file) )


    def collectorShiftParams(self):

        Module_base.collector(self)

        if self.params['params']['file'] != self.var_filePath.get():
            self.params['params']['file'] = self.var_filePath.get()
            self.img = None
        ovr = self.toFloat(self.var_oversampling.get(), self.params['params']['oversampling'])
        if self.params['params']['oversampling'] != ovr:
            self.params['params']['oversampling'] = ovr
            self.img = None
        self.params['params']['offset'][0] = self.toFloat(self.var_offMin.get(), self.params['params']['offset'][0])
        self.params['params']['offset'][1] = self.toFloat(self.var_offMax.get(), self.params['params']['offset'][1])
        self.params['params']['speed'][0] = self.toFloat(self.var_speedMin.get(), self.params['params']['speed'][0])
        self.params['params']['speed'][1] = self.toFloat(self.var_speedMax.get(), self.params['params']['speed'][1])


    def saveInto(self, trgTheme, trgPath):

        params = copy.deepcopy(self.params)

        # migrate files into target folder, if not already there
        shortName = os.path.basename(self.imgFullPath)
        newFilePath = trgPath + os.sep + shortName
        print 'trg file',newFilePath
        if not os.path.isfile(newFilePath):
            print 'not there, copying'
            shutil.copy2(self.imgFullPath, trgPath)

        params['params']['file'] = shortName
        trgTheme.append( params )


    def updated(self):
        pass


    def updateCanvas(self, fc):

        ovrs = float(self.params['params']['oversampling'])
        offsetx = float(self.params['params']['offset'][0])
        offsety = float(self.params['params']['offset'][1])
        speedx = float(self.params['params']['speed'][0])
        speedy = float(self.params['params']['speed'][1])
        if not self.img:
            if os.path.isfile(self.imgFullPath):
                self.img = pygame.image.load(self.imgFullPath)
                w = self.img.get_width()
                h = self.img.get_height()
                if ovrs != 1.0:
                    self.img = pygame.transform.smoothscale(self.img, (int(w*ovrs), int(h*ovrs)))

        if self.img:

            gain = Envelope.fromJson(self.params['envelope']).eval(self.time)
            w = fc.width
            h = fc.height

            offx = offsetx + speedx * self.time
            offy = offsety + speedy * self.time

            fc.fill(0.0,0.0,0.0)

            imgw = self.img.get_width() - 1
            imgh = self.img.get_height() - 1

            for to_x in xrange(w):
                from_x = ( (imgw + to_x - offx)%imgw ) * ovrs
                for to_y in xrange(h):
                    from_y = ( (imgh + to_y*2 - offy)%imgh ) * ovrs
                    col = self.img.get_at( (int(from_x), int(from_y)) )
                    fc.drawPixel(to_x, to_y, gain*col[0]/255.0, gain*col[1]/255.0, gain*col[2]/255.0)






######## ModWav ################################################################################################
################################################################################################################
################################################################################################################


class ModWav(Module_base):
    """
    Loads a sound file and plays it back periodically, or continuously
    """

    def __init__(self, modParams, basepath, parentColors, hash, client=None):
        Module_base.__init__(self, modParams, basepath, parentColors, hash, client)
        self.colorScheme['background']='#687baa'
        self.colorScheme['highlightbackground']='#3e4965'
        self.envelopeScheme = {'fill':'#4f5d81', 'outline':'#2f384d'}
        self.soundFullPath = basepath + os.sep + self.params['params']['file']

        self.controlsFrame = None

        # parameter widgets
        self.fileLabel = None
        self.filePath = None
        self.level = None
        self.repeatLabel = None
        self.loopMode = None
        self.repMin = None
        self.repMax = None


    @staticmethod
    def moduleCategory():

        return 'sounds'


    @staticmethod
    def defaults():

        return {    "mod" : "wav",
                    "name": "sound",
                    "params": {
                        "file" : "file.ogg",
                        "mode" : "loop",
                        "maxLevel" : 1.0,
                        "repeatEvery" : {"min" : 5.0, "max" : 10.0 }
                    },
                    "envelope": {
                        "type" : "log",
                        "keys" : [
                            {"time":0.0, "val":0.0},
                            {"time":1.0, "val":1.0}
                        ]
                    }
                }


    def destroy(self):
        Module_base.destroy(self)
        self.controlsFrame.destroy()


    def updated(self):
        pass


    def saveInto(self, trgTheme, trgPath):

        self.updateEnvKeys()

        modParams = copy.deepcopy(self.params)

        # migrate files into target folder, if not already there
        shortName = os.path.basename(self.soundFullPath)
        newFilePath = trgPath + os.sep + shortName
        print 'trg file',newFilePath
        if not os.path.isfile(newFilePath):
            print 'not there, copying'
            shutil.copy2(self.soundFullPath, trgPath)

        modParams['params']['file'] = shortName
        trgTheme.append( modParams )



    def addModKey(self, atTime):

        pass


    def updateModKeyParams(self, keyNum):

        pass


    def destroyModKeyParams(self):
        pass


    def buildParameters(self, parent, colScheme):

        Module_base.buildParameters(self, parent, colScheme)


        self.var_filePath = self.stringVar( self.params['params']['file'] )
        self.var_level    = self.intVar( self.params['params']['maxLevel']*100 )
        self.var_loopMode = self.stringVar( self.params['params']['mode'] )
        self.var_repMin   = self.stringVar( self.params['params']['repeatEvery']['min'] )
        self.var_repMax   = self.stringVar( self.params['params']['repeatEvery']['max'] )
        if not 'randGain' in self.params['params']:
            self.params['params']['randGain'] = [1.0,1.0]
        self.var_randGainMin   = self.stringVar( self.params['params']['randGain'][0] )
        self.var_randGainMax   = self.stringVar( self.params['params']['randGain'][1] )
        if not 'xfade' in self.params['params']:
            self.params['params']['xfade'] = 1.0
        self.var_xfade    = self.stringVar( self.params['params']['xfade'] )


        self.fileLabel = tk.LabelFrame(parent, text='sound file', padx=8, pady=8, **colScheme)
        self.fileLabel.pack(anchor='nw', fill='x', expand='yes')

        helper = tk.Frame(self.fileLabel, **colScheme)
        helper.pack(fill='x', expand='yes')
        self.filePath = tk.Entry(helper, textvariable=self.var_filePath, **colScheme)
        self.filePath.pack(side='left', fill='x', expand='yes')
        browseFile = tk.Button(helper, text='..', command=self.selectFile, **colScheme)
        browseFile.pack(side='left')

        helper = tk.Frame(self.fileLabel, **colScheme)
        helper.pack(fill='x')
        tk.Label(helper, text='max level', **colScheme).pack(side='left', anchor='sw')
        self.level = tk.Scale(helper, variable=self.var_level, orient='horizontal', **colScheme )
        self.level.pack(fill='x', expand='yes', side='left')
        self.level.set(self.params['params']['maxLevel']*100)

        self.repeatLabel = tk.LabelFrame(parent, text='repeat', padx=8, pady=8, **colScheme)
        self.repeatLabel.pack(anchor='nw', fill='x', expand='yes')
        helper = tk.Frame(self.repeatLabel, pady=8, **colScheme)
        helper.pack()
        self.loopMode = ttk.Combobox(helper, state='readonly', textvariable=self.var_loopMode)
        self.loopMode['values'] = ('loop', 'xfade')
        self.loopMode.pack()

        helper = tk.Frame(self.repeatLabel, **colScheme)
        helper.pack(fill='x', pady=8)
        tk.Label(helper, text='Repeat min', **colScheme).pack(side='left')
        self.repMin = tk.Entry(helper, width=6, textvariable=self.var_repMin, **colScheme)
        self.repMin.pack(side='left')
        tk.Label(helper, text='max', **colScheme).pack(side='left')
        self.repMax = tk.Entry(helper, width=6, textvariable=self.var_repMax, **colScheme)
        self.repMax.pack(side='left')

        helper = tk.Frame(self.repeatLabel, **colScheme)
        helper.pack(fill='x', pady=8)
        tk.Label(helper, text='random gain min', **colScheme).pack(side='left')
        self.rgainMin = tk.Entry(helper, width=6, textvariable=self.var_randGainMin, **colScheme)
        self.rgainMin.pack(side='left')
        tk.Label(helper, text='max', **colScheme).pack(side='left')
        self.rgainMax = tk.Entry(helper, width=6, textvariable=self.var_randGainMax, **colScheme)
        self.rgainMax.pack(side='left')

        self.xfadeLabel = tk.LabelFrame(parent, text='xfade', padx=8, pady=8, **colScheme)
        self.xfadeLabel.pack(anchor='nw', fill='x', expand='yes')

        helper = tk.Frame(self.xfadeLabel, **colScheme)
        helper.pack(fill='x', pady=8)
        tk.Label(helper, text='duration', **colScheme).pack(side='left')
        self.xfade = tk.Entry(helper, width=6, textvariable=self.var_xfade, **colScheme)
        self.xfade.pack(side='left')

        self.collectorCb = self.collectorModWav


    def destroyParameters(self):

        Module_base.destroyParameters(self)

        if self.fileLabel:
            self.fileLabel.destroy()
            self.fileLabel = None
            self.filePath = None
            self.level = None
        if self.repeatLabel:
            self.repeatLabel.destroy()
            self.repeatLabel = None
            self.loopMode = None
            self.repMin = None
            self.repMax = None
        if self.xfadeLabel:
            self.xfadeLabel.destroy()
            self.xfade = None


    def addCanvasButtons(self, parent):

        self.playVar = tk.IntVar()
        self.controlsFrame = tk.Frame(parent)
        self.controlsFrame.pack(side='left', anchor='n')
        self.playImg = tk.PhotoImage(file='playIcon.gif')
        b = tk.Checkbutton(self.controlsFrame, image=self.playImg, indicatoron=False, command=self.playButtonCb, variable=self.playVar,  selectcolor='#707070', **self.parentCols)
        b.pack()



    def playButtonCb(self):

        state = self.playVar.get()
        if state:
            print self.params['params']['maxLevel']
            self.lampClient.startSoundLoop(self.hash, self.soundFullPath, self.params['params']['maxLevel'])
        else:
            self.lampClient.stopSoundLoop(self.hash)



    def setTime(self, val):

        Module_base.setTime(self, val)
        if self.playVar.get():
            env = Envelope.fromJson(self.params['envelope'])
            volume = env.eval(val) * self.params['params']['maxLevel']
            self.lampClient.setSoundVolume(self.hash, volume)

    def selectFile(self):

        file = tkFileDialog.askopenfilename(title='select sound file', initialfile=self.params['params']['file'], filetypes=[('sound file','*.wav'),('sound file','*.ogg')])
        if file and os.path.isfile(file):
            self.soundFullPath = file
            self.var_filePath.set( os.path.basename(file) )
            self.var_modName.set(os.path.basename(file))


    def collectorModWav(self):

        Module_base.collector(self)
        self.params['params']['file'] = self.var_filePath.get()
        self.params['params']['mode'] = self.var_loopMode.get()
        self.params['params']['repeatEvery']['min'] = self.toFloat(self.var_repMin.get(), self.params['params']['repeatEvery']['min'])
        self.params['params']['repeatEvery']['max'] = self.toFloat(self.var_repMax.get(), self.params['params']['repeatEvery']['max'])
        self.params['params']['randGain'][0] = self.toFloat(self.var_randGainMin.get(), self.params['params']['randGain'][0])
        self.params['params']['randGain'][1] = self.toFloat(self.var_randGainMax.get(), self.params['params']['randGain'][1])
        self.params['params']['xfade'] = self.toFloat(self.var_xfade.get(), self.params['params']['xfade'])
        if self.params['params']['maxLevel'] != self.var_level.get()/100.0:
            self.params['params']['maxLevel'] = self.var_level.get()/100.0
            self.setTime(self.time) # update sound volume
        #print 'collect'



__author__ = 'fhu'
