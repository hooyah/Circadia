"""
    Circadia Theme Editor - preview pane widget

    Hardware visualizer

    Author: fhu

"""

import Tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont


class CircadiaVisualizer(tk.Frame):


    def __init__(self, master, cfg):

        tk.Frame.__init__(self, master)

        img = Image.open('lamp.png')
        self.lampSrc = img.resize( (img.width/2, img.height/2), resample=Image.LANCZOS)
        self.lampImg = ImageTk.PhotoImage(self.lampSrc)
        self.backgroundLabel = tk.Label(master, image=self.lampImg, background='#252525')
        self.backgroundLabel.pack(side='left', anchor='sw', fill='y')

    def get_screenWidth(self):
        return 16

    def get_screenHeight(self):
        return 18


    def updateScreen(self, canvas):
        """ update the image with a new canvas"""

        w = canvas.width
        h = canvas.height

        img = Image.new('RGB', (w, h))
        drw = ImageDraw.Draw(img)
        for x in xrange(w):
            for y in xrange(h):
                col = canvas.getPixel(x, y)
                drw.point((x,y), fill=(int(col[0]*255), int(col[1]*255), int(col[2]*255)))

        scl = img.resize( (87, 324), resample=Image.BILINEAR )
        self.lampSrc.paste(scl, (55,227))
        self.lampImg = ImageTk.PhotoImage(self.lampSrc)
        self.backgroundLabel.config(image=self.lampImg)




__author__ = 'florian'
