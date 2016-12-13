"""
    Circadia Theme Editor - Tk color gradient widget class

    Author: fhu
"""

import Tkinter as tk
from TkColorEdit import ColorEdit
import MSR_OS.floatCanvas as FloatCanvas


class GradientEdit(tk.Frame):

    def __init__(self, parent, params, callback=None, colScheme={}):

        self.focusedKey = 0
        self.height = 250
        self.gradKeys = list()

        tk.Frame.__init__(self, parent, borderwidth=1, relief='sunken')
        ft = tk.Frame(self,pady = 8, **colScheme)
        ft.pack()

        self.gradCanvas = tk.Canvas(ft, width=40, height=250, **colScheme)
        self.gradCanvas.pack(anchor='nw', side='left')

        self.colorEdit = ColorEdit(ft, 0, 0, 0, slim=True, colScheme=colScheme, callback=self.__colorSwatchCb)
        self.colorEdit.pack(anchor='nw', side='left')

        #self.gradCanvas.create_rectangle(0, 0, 30, self.height+4, fill='#ffff00')
        self.gradCanvas.bind('<Shift-Button-1>', self.__mouseShiftClick)
        self.gradCanvas.bind('<Button-1>', self.__mouseClick)
        self.gradCanvas.bind('<Motion>', self.__mouseMove)
        self.gradCanvas.bind('<ButtonRelease-1>', self.__mouseRelease)
        self.gradCanvas.bind('<Delete>', self.__deleteKey)

        self.callback = callback
        self.setGradient(params)
        self.__drawGradient()


    def setGradient(self, params):

        for k in self.gradKeys:
            if k[0]:
                self.gradCanvas.delete(k[0])
        self.gradKeys = list()
        self.params = params
        self.mouseItem = None
        self.mouseAnchor = None
        self.focusedKey = 0
        self.__updateGradientKeys()
        self.__drawGradient()
        self.colorEdit.setColor(round(self.gradKeys[0][1][1][0]*255.0), round(self.gradKeys[0][1][1][1]*255), round(self.gradKeys[0][1][1][2]*255))



    def __drawGradient(self):

        self.gradCanvas.delete('grad_lines')
        keys = [k[1] for k in self.gradKeys]
        grad = FloatCanvas.Gradient3(keys)
        for i in xrange(self.height):
            c = grad.eval(float(i) / (self.height-1))
            self.gradCanvas.create_line(0, i+2, 30, i+2, fill='#%02x%02x%02x'%(c[0]*255, c[1]*255, c[2]*255), tags='grad_lines')
        self.gradCanvas.tag_lower('grad_lines')
        self.gradCanvas.update_idletasks()
        if self.callback:
            self.callback(self.params)


    def __updateGradientKeys(self):

        if len(self.gradKeys) == 0:
            for i, k in enumerate(self.params):
                y = k[0]*self.height + 2
                outline = 'yellow' if self.focusedKey == i else 'black'
                id = self.gradCanvas.create_polygon(30, y-6, 38, y-6, 38, y+6, 30, y+6, 26, y, activeoutline='#ffff00', outline=outline, fill='#%02x%02x%02x'%(k[1][0]*255, k[1][1]*255, k[1][2]*255))
                self.gradKeys.append( [id, k])
        else:
            for i, k in enumerate(self.gradKeys):
                y = k[1][0]*self.height + 2
                self.gradCanvas.coords(k[0], 30, y-6, 38, y-6, 38, y+6, 30, y+6, 26, y)
                outline = 'yellow' if self.focusedKey == i else 'black'
                fill='#%02x%02x%02x'%(k[1][1][0]*255, k[1][1][1]*255, k[1][1][2]*255)
                self.gradCanvas.itemconfig(k[0], outline=outline, fill=fill)


    def __mouseClick(self, event):

        self.gradCanvas.focus_set()
        xy = self.gradCanvas.canvasx(event.x), self.gradCanvas.canvasy(event.y)
        items = self.gradCanvas.find_withtag(tk.CURRENT)
        if len(items):
            for i,k in enumerate(self.gradKeys):
                if k[0] == items[0]:
                    self.mouseItem = [k[0], k[1][0], k[1]]
                    self.mouseAnchor = xy
                    self.focusedKey = i
                    self.colorEdit.setColor(round(k[1][1][0]*255.0), round(k[1][1][1]*255), round(k[1][1][2]*255))
                    self.__updateGradientKeys()
                    break


    def __mouseShiftClick(self, event):

        self.gradCanvas.focus_set()
        y =self.gradCanvas.canvasy(event.y)-2
        grad = FloatCanvas.Gradient3(self.params)
        pos = max(0, min(1.0, float(y)/self.height ))
        newCol = grad.eval( pos )
        print newCol, pos
        self.params.append( [pos, [newCol[0], newCol[1], newCol[2]] ] )
        #self.params.append( [pos, [0,0,0] ] )
        for g in self.gradKeys:
            self.gradCanvas.delete(g[0])
        self.gradKeys=list()
        self.__updateGradientKeys()


    def __mouseMove(self, event):

        if self.mouseItem:
            disty = self.gradCanvas.canvasx(event.y)-self.mouseAnchor[1]
            disty = disty / float(self.height)
            newvaly = max(0, min(1, self.mouseItem[1] + disty))

            self.mouseItem[2][0] = newvaly # change the actual values
            self.__updateGradientKeys()
            self.__drawGradient()


    def __mouseRelease(self, event):

        if not self.mouseAnchor:
            return

        self.mouseAnchor = None
        self.mouseItem = None


    def __deleteKey(self, event):

        if len(self.gradKeys) > 1 and self.focusedKey > -1:
            self.gradCanvas.delete(self.gradKeys[self.focusedKey][0])
            self.params.remove(self.gradKeys[self.focusedKey][1])
            del(self.gradKeys[self.focusedKey])
            self.focusedKey = min(len(self.gradKeys)-1, self.focusedKey)

    def __colorSwatchCb(self, r, g, b):

        if len(self.gradKeys) and self.focusedKey > -1:
            focused = self.gradKeys[self.focusedKey][1]
            focused[1][0] = r/255.0
            focused[1][1] = g/255.0
            focused[1][2] = b/255.0
            self.__updateGradientKeys()
            self.__drawGradient()



__author__ = 'fhu'
