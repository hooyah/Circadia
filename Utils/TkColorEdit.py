"""
    Circadia Theme Editor - Tk color edit widget class

    Author: fhu
"""

import colorsys
import Tkinter as tk

class ColorEdit(tk.Frame):

    def __init__(self, parent, R, G, B, callback=None, slim=False, colScheme={}):

        tk.Frame.__init__(self, parent, borderwidth=1, relief='sunken')

        self.colorX = tk.IntVar()
        self.colorY = tk.IntVar()
        self.colorZ = tk.IntVar()
        self.colorModeVar = tk.IntVar()
        self.colorModeVar.set(0)
        self.colorModeLocal = 0
        self.colorX.set(R)
        self.colorX.set(G)
        self.colorX.set(B)
        self.cb = callback
        self.updateEnabled = True

        self.colorSwatch = None
        if not slim:
            self.colorSwatch = tk.Canvas(self, width=50, height=130)
            self.colorSwatch.pack(side='left', anchor='s')

        self.vt = tk.Frame(self, **colScheme)
        self.vt.pack()
        #self.colorSwatch.pack(side='left')

        self.radio = tk.Frame(self.vt, **colScheme)
        self.radio.pack(side='top')
        self.R1 = tk.Radiobutton(self.radio, text="RGB", variable=self.colorModeVar, value=0, command=self.__changeMode, **colScheme)
        self.R1.pack( side = 'left' )
        self.R2 = tk.Radiobutton(self.radio, text="HSV", variable=self.colorModeVar, value=1, command=self.__changeMode, **colScheme)
        self.R2.pack( side = 'left' )
        if slim:
            self.colorSwatch = tk.Canvas(self.radio, width=50, height=20)
            self.colorSwatch.pack(side='left', anchor='n')

        # X
        self.sliders = tk.Frame(self.vt, **colScheme)
        self.sliders.pack(side='top')
        self.frA = tk.Frame(self.sliders, **colScheme)
        self.frA.pack()
        self.frAd = tk.Button(self.frA, text="<", command=self.decX, **colScheme)
        self.frAd.pack(side='left')
        self.sampleSliderA = tk.Scale(self.frA, orient=tk.HORIZONTAL, length=(150 if slim else 200), to=255, variable=self.colorX, command=self.__updateColor, **colScheme)
        self.sampleSliderA.pack(side='left')
        self.frAi = tk.Button(self.frA, text=">", command=self.incX, **colScheme)
        self.frAi.pack(side='left')

        # Y
        self.frB = tk.Frame(self.sliders, **colScheme)
        self.frB.pack()
        self.frBd = tk.Button(self.frB, text="<", command=self.decY, **colScheme)
        self.frBd.pack(side='left')
        self.sampleSliderB = tk.Scale(self.frB, orient=tk.HORIZONTAL, length=(150 if slim else 200), to=255, variable=self.colorY, command=self.__updateColor, **colScheme)
        self.sampleSliderB.pack(side='left')
        self.frBi = tk.Button(self.frB, text=">", command=self.incY, **colScheme)
        self.frBi.pack(side='left')

        # Z
        self.frC = tk.Frame(self.sliders, **colScheme)
        self.frC.pack()
        self.frCd = tk.Button(self.frC, text="<", command=self.decZ, **colScheme)
        self.frCd.pack(side='left')
        self.sampleSliderC = tk.Scale(self.frC, orient=tk.HORIZONTAL, length=(150 if slim else 200), to=255, variable=self.colorZ, command=self.__updateColor, **colScheme)
        self.sampleSliderC.pack(side='left')
        self.frCi = tk.Button(self.frC, text=">", command=self.incZ, **colScheme)
        self.frCi.pack(side='left')

        self.crect = self.colorSwatch.create_rectangle(0, 0, 50, 130)
        self.__updateColor()

    def incX(self):
        self.sampleSliderA.set( min(255, self.colorX.get()+1) )
    def decX(self):
        self.sampleSliderA.set( max(0, self.colorX.get()-1) )
    def incY(self):
        self.sampleSliderB.set( min(255, self.colorY.get()+1) )
    def decY(self):
        self.sampleSliderB.set( max(0, self.colorY.get()-1) )
    def incZ(self):
        self.sampleSliderC.set( min(255, self.colorZ.get()+1) )
    def decZ(self):
        self.sampleSliderC.set( max(0, self.colorZ.get()-1) )


    def __changeMode(self, *args):

        newMode = self.colorModeVar.get()
        if newMode != self.colorModeLocal:
            x = self.colorX.get()
            y = self.colorY.get()
            z = self.colorZ.get()
            col=0
            if newMode == 0: # HSV->RGB
                col = [ int(round(x*255.0)) for x in colorsys.hsv_to_rgb(x/255.0, y/255.0, z/255.0)]
            else: # RGB -> HSV
                col = [ int(round(x*255.0)) for x in colorsys.rgb_to_hsv(x/255.0, y/255.0, z/255.0)]
            self.colorX.set(col[0])
            self.colorY.set(col[1])
            self.colorZ.set(col[2])
            self.colorModeLocal = newMode

    def getRGB(self):

        x = self.colorX.get()
        y = self.colorY.get()
        z = self.colorZ.get()
        if self.colorModeVar.get() == 0:
            return [ x, y, z ]
        else:
            return [ int(round(x*255.0)) for x in colorsys.hsv_to_rgb(x/255.0, y/255.0, z/255.0)]


    def __updateColor(self, *args):

        if self.updateEnabled:
            color = self.getRGB()
            self.colorSwatch.itemconfig(self.crect, fill='#%02x%02x%02x'%(color[0], color[1], color[2]))
            if self.cb:
                self.cb(color[0], color[1], color[2])


    def setColor(self, r, g, b):
        """
        :param r: red, integer 0-255
        :param g: green, integer 0-255
        :param b: blue, integer 0-255
        :return: None
        """

        self.updateEnabled = False
        if self.colorModeLocal == 1: # hsv
            col = [ int(round(x*255)) for x in colorsys.rgb_to_hsv(float(r)/255,float(g)/255,float(b)/255)]
            self.colorX.set(col[0])
            self.colorY.set(col[1])
            self.colorZ.set(col[2])
            self.colorSwatch.itemconfig(self.crect, fill='#%02x%02x%02x'%(r, g, b))
        else: # RGB
            self.colorX.set(r)
            self.colorY.set(g)
            self.colorZ.set(b)
            self.colorSwatch.itemconfig(self.crect, fill='#%02x%02x%02x'%(r, g, b))
        self.updateEnabled = True



__author__ = 'fhu'
