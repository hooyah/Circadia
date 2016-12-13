"""
    Circadia Theme Editor - graphics/sound module base class

    General UI interactions

    Author: fhu

"""


import Tkinter as tk



class Module_base():

    def __init__(self, modParams, basepath, parentColorScheme, hash, client=None):

        self.parentCols = parentColorScheme
        self.hash = hash
        self.basepath = basepath
        self.params = modParams
        self.colorScheme = {'background':'#a0a0a0', 'highlightcolor':'#ffff00', 'highlightbackground':'#101010'}
        self.envelopeScheme = {}
        self.var_modName = None

        self.canvasFrm = None
        self.canvas = None

        self.envItemId = None
        self.envItems = list()
        self.modItems = list()
        self.mouseAnchor = None
        self.mouseItem = None
        self.width = 0
        self.height= 0
        self.hasFocus = None
        self.focusedItem = 0
        self.labelId = None
        self.collectorCb = None

        self.var_keyNumber = self.stringVar( "9999" )
        self.var_modNumber = self.stringVar( "9999" )
        self.var_keyPos = tk.StringVar()
        self.var_keyVal = tk.StringVar()
        self.var_modPos = tk.StringVar()

        # parameter widgets
        self.genLabel = None
        self.envLabel = None
        self.nameEntry = None
        self.editEnvKeyId  = None
        self.editModKeyId  = None
        self.keyPos = None
        self.keyVal = None
        self.modPos = None
        self.modParamFrameKey = None
        self.modParamFrame = None
        self.modKeyParams = None

        self.time = 0
        self.lampClient = client



    def destroy(self):
        """ destroy the module's track widgets """
        self.canvasFrm.destroy()


    def updated(self):
        """ callback called if the UI changed values or key positions. implemented in derived classes """
        pass

    def setTime(self, val):
        """ informs the module that the current time has changed """

        self.time = val
        self.canvas.coords(self.cursor, self.width*self.time, 0, self.width*self.time, self.height)


    def __tkImgFill(self, image, color):

        line = "{"+ " ".join([color]*image.width())+"}"
        self.backDropImg.put(" ".join([line]*image.height()), (0,0))


    def createWidgets(self, parent, y, width, height):
        """ create the track widgets for this module """

        self.canvasFrm = tk.Frame(parent, **self.parentCols)
        self.canvasFrm.pack(anchor='w')
        self.canvas = tk.Canvas(self.canvasFrm, width=width, height=height, highlightthickness=1, **self.colorScheme)
        self.width = width
        self.height = height
        self.canvas.pack(side='left')

        self.addCanvasButtons(self.canvasFrm)

        envKeys=[ [k['time'], k['val']] for k in self.params['envelope']['keys']]

        for i in xrange(len(envKeys)):
            self.envItems.append( [None,'env', envKeys[i]] )

        self.updateKeyframes()

        self.backDropImg = tk.PhotoImage(width=self.width, height=self.height)
        self.__tkImgFill(self.backDropImg, self.colorScheme['background'])
        self.backdrop = self.canvas.create_image(0, 0, anchor='nw', image=self.backDropImg)
        self.canvas.tag_lower(self.backdrop)
        self.canvas.create_line(0,height/2,width,height/2, fill=self.envelopeScheme['outline'])
        self.labelId = self.canvas.create_text( (width/2, height/2), text=self.params['name'], state='disabled')

        self.cursor = self.canvas.create_line(self.time*self.width, 0, self.time*self.width, self.height, fill='#a0a0a0')

        self.canvas.bind('<Motion>', self.mouseMove)
        self.canvas.bind('<ButtonRelease-1>', self.mouseRelease)
        self.canvas.bind('<Shift-Button-1>', self.mouseShiftAdd)
        self.canvas.bind('<Delete>', self.deleteKey)

        return self.canvas

    def addCanvasButtons(self, parent):
        """ Overridden by derived classes to add additional controls to the track """
        pass


    def buildParameters(self, parent, colScheme):
        """ Builds common parameter widgets for this module """

        #print 'build params'
        self.var_modName = self.stringVar(self.params['name'])

        # general parameters, name
        self.genLabel = tk.LabelFrame(parent, text='general', padx=8, pady=8, **colScheme)
        self.genLabel.pack(anchor='nw', fill='x', expand='yes')
        tk.Label(self.genLabel, text='trackName', **colScheme).pack(side='left')
        self.nameEntry = tk.Entry(self.genLabel, textvariable=self.var_modName, **colScheme)
        self.nameEntry.pack(side='left', fill='x', expand='yes')

        # envelope editing
        self.envLabel = tk.LabelFrame(parent, text='Envelope', padx=8, pady=8, **colScheme)
        self.envLabel.pack(anchor='nw', fill='x', expand='yes')
        txt = tk.Label(self.genLabel, text='Key', **colScheme)
        txt.pack(side='left')
        self.editEnvKeyId = tk.Spinbox(self.envLabel, width=2, from_=1, to=len(self.envItems), textvariable=self.var_keyNumber, state='readonly', readonlybackground=colScheme['background'], **colScheme)
        self.editEnvKeyId.pack(side='left')
        txt = tk.Label(self.envLabel, text='pos', **colScheme)
        txt.pack(side='left')
        self.keyPos = tk.Entry(self.envLabel, width=6, textvariable=self.var_keyPos, **colScheme)
        self.keyPos.pack(side='left')
        txt = tk.Label(self.envLabel, text='value', **colScheme)
        txt.pack(side='left')
        self.keyVal = tk.Entry(self.envLabel, width=6, textvariable=self.var_keyVal, **colScheme)
        self.keyVal.pack(side='left')

        # some modules support parameter keyframes (modItems)
        if len(self.modItems):

            self.modParamFrameKey = tk.LabelFrame(parent, text='ModKey', padx=8, pady=8, **colScheme)
            self.modParamFrameKey.pack(anchor='nw', fill='x', expand='yes')

            hor = tk.Frame(self.modParamFrameKey, **colScheme)
            hor.pack(side='top')
            self.editModKeyId = tk.Spinbox(hor, width=2, from_=1, to=len(self.modItems), textvariable=self.var_modNumber, state='readonly', readonlybackground=colScheme['background'], **colScheme)
            self.editModKeyId.pack(side='left')
            txt = tk.Label(hor, text='pos', **colScheme)
            txt.pack(side='left')
            self.modPos = tk.Entry(hor, width=6, textvariable=self.var_modPos, **colScheme)
            self.modPos.pack(side='left')
            self.modPos.bind('<Return>', self.__acceptModVal)

            self.modParamFrame = tk.Frame(self.modParamFrameKey, pady=8, **colScheme)
            self.modParamFrame.pack(anchor='nw', fill='x', expand='yes')
            self.modKeyParams = self.buildModKeyParams(self.modParamFrame, colScheme)

        self.keyPos.bind('<Return>', self.__acceptEnvVal)
        self.keyVal.bind('<Return>', self.__acceptEnvVal)
        self.collectorCb = self.collector
        self.__updateKeyWidgets()


    def destroyParameters(self):
        """ Destroys the widgets for parameter editing """
        if self.genLabel:
            self.genLabel.destroy()
            self.genLabel = None
            self.nameEntry = None
        if self.envLabel:
            self.envLabel.destroy()
            self.envLabel = None
            self.editEnvKeyId  = None
            self.keyPos = None
            self.keyVal = None
        if self.modParamFrameKey:
            self.modParamFrameKey.destroy()
            self.modParamFrame.destroy()
            self.modParamFrameKey = None
            self.modKeyParams = None
        if self.supportsModKeys():
            self.destroyModKeyParams()
        self.collectorCb = self.collector


    def collectParameters(self, *args):
        """ callback to fetch values from widgets and transfer them into internal data structures """
        # deferred handler to avoid race conditions between base and derived class (weird)
        if self.collectorCb:
            self.collectorCb()


    def collector(self):
        """ fetch values from widgets and transfer them into internal data structures """

        if not self.var_modName:
            return

        self.params['name'] = self.var_modName.get()
        if self.canvas.itemcget(self.labelId, 'text') != self.params['name']:
            self.canvas.itemconfig(self.labelId, text=self.params['name'])


        if self.focusedItem > -1:
            if self.focusedItem < len(self.envItems):
                k = max(0, min(len(self.envItems)-1, int(self.var_keyNumber.get())-1))
                if k != self.focusedItem:
                    self.focusedItem = k
                    self.updateKeyframes()
                    self.__updateKeyWidgets()
            else:
                k = max(0, min(len(self.modItems)-1, int(self.var_modNumber.get())-1))
                if k != self.focusedItem-len(self.envItems):
                    self.focusedItem = k+len(self.envItems)
                    self.updateKeyframes()
                    self.__updateKeyWidgets()



    def setFocus(self, yesno):
        """ changes the focus of a track """

        if self.hasFocus != yesno:
            #print 'set focus'
            self.hasFocus = yesno
            if yesno:
                self.canvas.itemconfig(self.labelId, fill='#FFFF00')
            else:
                self.canvas.itemconfig(self.labelId, fill='#000000')
        self.updateKeyframes()


    def updateKeyframes(self):
        """ draws or updates the track """

        coords, sorted = self.__envelopeCoords()
        if not self.envItemId:
            #draw envelope
            self.envItemId = self.canvas.create_polygon(*sorted, **self.envelopeScheme)
            for i in xrange(len(self.envItems)):
                fillcol = '#FFFF00' if (i == self.focusedItem and self.hasFocus) else '#000000'
                it = self.canvas.create_rectangle(coords[i*2]-2, coords[i*2+1]-2, coords[i*2]+2, coords[i*2+1]+2, activeoutline='#FFFF00', fill=fillcol)
                self.canvas.tag_bind(it, '<Button-1>', self.mouseClick)
                self.envItems[i][0] = it
        else:
            self.canvas.coords(self.envItemId, *sorted)
            for i in xrange(len(self.envItems)):
                fillcol = '#FFFF00' if (i == self.focusedItem and self.hasFocus) else '#000000'
                self.canvas.itemconfig(self.envItems[i][0], fill=fillcol)
                self.canvas.coords(self.envItems[i][0], coords[i*2]-2, coords[i*2+1]-2, coords[i*2]+2, coords[i*2+1]+2)

        for i,k in enumerate(self.modItems):
            t = k[2]['time']
            x = t * self.width
            fillcol = '#FFFF00' if (i == self.focusedItem-len(self.envItems) and self.hasFocus) else self.colorScheme['background']
            if k[0] > -1:
                self.canvas.coords(k[0], x-4, 0, x+4, 0, x+4, 4, x, 12, x-4, 4)
                self.canvas.itemconfig(k[0], fill=fillcol)
            else:
                it = self.canvas.create_polygon(x-4, 0, x+4, 0, x+4, 4, x, 12, x-4, 4, activeoutline='#FFFF00', **self.envelopeScheme)
                self.canvas.tag_bind(it, '<Button-1>', self.mouseClick)
                k[0] = it




    def updateEnvKeys(self):
        """ updates the theme's dictionary with the widget's envelope values """
        keys = []
        for i, item in enumerate(self.envItems):
            if item[1] == 'env':
                keys.append( {'time':item[2][0], 'val':item[2][1]} )

        self.params['envelope']['keys'] = keys


    def supportsModKeys(self):
        """ Overridden in derived class. Signals whether the module supports keyframed parameters (in addition to the envelope) """
        return False


    def addModKeys(self, keys):
        """ add parameter keyframes to this track """
        for i, k in enumerate(keys):
            self.modItems.append( [None, 'mod', k] )


    def __envelopeCoords(self):

        coords = list()
        coords_sorted = list()
        csorted = sorted([x[2] for x in self.envItems])
        for k in [x[2] for x in self.envItems]:
            coords.append( k[0] * self.width )
            coords.append( self.height - k[1] * self.height / 2)
        for k in csorted:
            coords_sorted.append( k[0] * self.width )
            coords_sorted.append( self.height - k[1] * self.height / 2)
        if csorted[-1][0] < 1.0:
            coords_sorted.append( self.width )
            coords_sorted.append( self.height - csorted[-1][1] * self.height / 2)
        coords_sorted.append( self.width )
        coords_sorted.append( self.height)
        coords_sorted.append( 0 )
        coords_sorted.append( self.height)
        if csorted[0][0] > 0.0:
            coords_sorted.append( 0 )
            coords_sorted.append( self.height - csorted[0][1] * self.height / 2)

        return coords, coords_sorted



    def __updateKeyWidgets(self):
        """ updates the numeric envelope/key controls in case the highlighted key has changed """
        envlen = len(self.envItems)
        if self.focusedItem < envlen:
            self.var_keyPos.set( str(self.envItems[self.focusedItem][2][0]) )
            self.var_keyVal.set( str(self.envItems[self.focusedItem][2][1]) )
            if int(self.var_keyNumber.get())-1 != self.focusedItem: # prevent unnecessary collector call if nothing has changed
                self.var_keyNumber.set(str(self.focusedItem+1))
        else:
            self.var_modPos.set( str(self.modItems[self.focusedItem-envlen][2]['time']) )
            #if int(self.var_modNumber.get())-1 != self.focusedItem-envlen: # prevent unnecessary collector call if nothing has changed
            itNum = self.focusedItem-envlen
            self.var_modNumber.set(str(itNum+1))
            self.updateModKeyParams(self.modItems[self.focusedItem-envlen][2])



    def __acceptEnvVal(self, event):

        p = self.toFloat(self.var_keyPos.get(), self.envItems[self.focusedItem][2][0])
        v = self.toFloat(self.var_keyVal.get(), self.envItems[self.focusedItem][2][1])
        self.var_keyPos.set( str(p) )
        self.var_keyVal.set( str(v) )
        self.envItems[self.focusedItem][2][0] = p
        self.envItems[self.focusedItem][2][1] = v
        self.updateKeyframes()


    def __acceptModVal(self, event):

        id = self.focusedItem-len(self.envItems)

        p = self.toFloat(self.var_modPos.get(), self.modItems[id][2])
        self.var_modPos.set( str(p) )
        self.modItems[id][2]['time'] = p
        self.updateKeyframes()


    def mouseClick(self, event):
        """ handle mouse events """

        self.canvas.focus_set()
        xy = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        item = self.canvas.find_withtag(tk.CURRENT)
        for n, it in enumerate(self.envItems):
            #print 'it=',it, 'item=',item[0]
            if it[0] == item[0]:
                self.mouseItem = [it[0], it[1], it[2], it[2][:]] # copy
                self.mouseAnchor = xy
                self.focusedItem = n
                self.__updateKeyWidgets()
                self.updateKeyframes()
                return

        for n, it in enumerate(self.modItems):
            if it[0] == item[0]:
                print n
                self.mouseItem = [it[0], it[1], it[2], it[2]['time']] # copy
                self.mouseAnchor = xy
                self.focusedItem = n+len(self.envItems)
                self.__updateKeyWidgets()
                self.updateKeyframes()
                return


    def mouseShiftAdd(self, event):
        """ handle SHIFT+mouse events """

        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        items = self.canvas.find_withtag(tk.CURRENT)

        if y > self.height / 2:
            newvalx = max(0, min(1,   x / float(self.width)   ))
            newvaly = max(0, min(1,  (self.height - y) / (self.height/2.0) ))

            self.canvas.delete(self.envItemId) # delete polygon
            self.envItemId = None
            for i in self.envItems: # delete keys
                self.canvas.delete(i[0])
                i[0] = None

            self.envItems.append( [ None, 'env', [newvalx, newvaly ] ] )
            self.focusedItem = len(self.envItems)-1
            self.updateKeyframes()
            if self.editEnvKeyId:
                self.editEnvKeyId.config(to=len(self.envItems))
        else:
            if self.supportsModKeys():
                newvalx = max(0, min(1,   x / float(self.width)   ))
                k = self.addModKey(newvalx)
                self.modItems.append( [ None, 'mod', k ] )
                self.focusedItem = len(self.modItems)-1+len(self.envItems)
                self.updateKeyframes()
                if self.editModKeyId:
                    self.editModKeyId.config(to=len(self.modItems))


    def deleteKey(self, event):
        """ handle delete key events """

        if self.focusedItem > -1:
            if self.focusedItem < len(self.envItems):
                if len(self.envItems) <= 1: # need at least one key
                    return

                self.canvas.delete(self.envItemId) # delete polygon
                self.envItemId = None
                for i in self.envItems: # delete keys
                    self.canvas.delete(i[0])
                    i[0] = None

                del(self.envItems[self.focusedItem])
                self.focusedItem = max(0, self.focusedItem - 1)
                self.updateKeyframes()
                if self.var_modName:
                    self.editEnvKeyId.config(to=len(self.envItems))
            else:
                if len(self.modItems) <= 1: # need at least one key
                    return

                itId = self.focusedItem-len(self.envItems)
                self.params['params']['keys'].remove(self.modItems[itId][2])
                self.canvas.delete(self.modItems[itId][0])
                del(self.modItems[itId])

                self.focusedItem = max(len(self.envItems), self.focusedItem - 1)
                self.updateKeyframes()
                if self.var_modName:
                    self.editModKeyId.config(to=len(self.modItems))



    def mouseMove(self, event):
        """ handle mouse events """

        if self.mouseItem:
            distx, disty = self.canvas.canvasx(event.x)-self.mouseAnchor[0], self.canvas.canvasx(event.y)-self.mouseAnchor[1]
            if self.mouseItem[1] == 'env':
                distx = distx / float(self.width)
                disty = -disty / float(self.height/2)
                newvalx = max(0, min(1, self.mouseItem[3][0] + distx))
                newvaly = max(0, min(1, self.mouseItem[3][1] + disty))
                self.mouseItem[2][0] = newvalx # change the actual values
                self.mouseItem[2][1] = newvaly
                self.updateKeyframes()
                self.__updateKeyWidgets()
            else:
                distx = distx / float(self.width)
                newvalx = max(0, min(1, self.mouseItem[3] + distx))
                self.mouseItem[2]['time'] = newvalx # change the actual values
                self.updateKeyframes()
                self.__updateKeyWidgets()


    def mouseRelease(self, event):
        """ handle mouse events """

        if not self.mouseAnchor:
            return

        self.mouseAnchor = None
        self.mouseItem = None

        if self.focusedItem < len(self.envItems):
            # sort items by position
            oldFocus = self.envItems[self.focusedItem][0]
            self.envItems.sort(key=lambda item: item[2][0])
            for i, item in enumerate(self.envItems):
                if item[0] == oldFocus:
                    self.focusedItem = i
                    self.__updateKeyWidgets()
                    break
        else:
            # sort items by position
            oldFocus = self.modItems[self.focusedItem-len(self.envItems)][0]
            self.modItems.sort(key=lambda item: item[2]['time'])
            for i, item in enumerate(self.modItems):
                if item[0] == oldFocus:
                    self.focusedItem = i+len(self.envItems)
                    self.__updateKeyWidgets()
                    break
            self.updated()



    def stringVar(self, val):
        """ convenience function to create a tk.StringVar and bind it to the collector callback """
        var = tk.StringVar()
        var.set(val)
        var.trace('w', self.collectParameters)
        return var

    def intVar(self, val):
        """ convenience function to create a tk.IntVar and bind it to the collector callback """
        var = tk.IntVar()
        var.set(val)
        var.trace('w', self.collectParameters)
        return var

    def doubleVar(self, val):
        """ convenience function to create a tk.DoubleVar and bind it to the collector callback """
        var = tk.DoubleVar()
        var.set(val)
        var.trace('w', self.collectParameters)
        return var

    def toFloat(self, var, default):
        """ convenience function to convert a value/string to a reliable float """
        try:
            return float(var)
        except ValueError:
            return default




__author__ = 'fhu'
