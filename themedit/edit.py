"""
    Circadia Theme Editor - Main app

    Author: fhu
"""


from PIL import Image, ImageTk, ImageDraw, ImageFont
import Tkinter as tk
import tkMessageBox
import tkFileDialog
import json
import os, shutil, sys
import SClient
import time
import subprocess

if __name__ == '__main__':
    sys.path.append( os.path.abspath('..') ) # add ../ to the path

from MSR_OS import floatCanvas
from Mods import ModGradient, ModWav, ModShift
from circadiaPreview import CircadiaVisualizer
import editAbout

# list of supported modules
Modules = {'gradient': ModGradient, 'imgShift': ModShift, 'wav': ModWav}



class Application(tk.Frame):

    def __init__(self, master=None):

        tk.Frame.__init__(self, master)

        self.cfg = None
        self.loadSettings()

        self.poster = None
        self.posterTk = None
        self.posterCrop = None
        self.posterWidth = self.getSetting("posterWidth", 1000)
        self.posterHeight = self.getSetting("poserHeight", 150)
        self.modules = []
        self.highlightedModule = -1
        self.modHashCounter = 0

        self.lampClient = SClient.CircadiaSocketClient()
        self.clientTime = None

        self.time = 0.45
        self.timelineMouseCap = False
        self.duration = 60*30

        self.themeRootPath = self.getSetting("themeRootPath", "")
        self.themePath = None
        self.theme = None

        self.posterFont = self.getSetting("posterFont", "")
        self.pack(fill='both', expand='yes')

        self.colorScheme={
            'background':self.getSetting("color_background", "#444444"),
            'highlightbackground':self.getSetting("color_background", "#444444")
        }
        self.createWidgets()

        # main menu
        self.menubar = tk.Menu(master)
        self.createMenus()
        master.config(menu=self.menubar)

        # popup Menu
        self.popupMenu = tk.Menu(master, tearoff=0)
        self.popup_addMenu = tk.Menu(self.popupMenu, tearoff=0)
        self.popupMenu.add_cascade(label="New", menu=self.popup_addMenu)
        # add modules
        for k in Modules.items():
            self.popup_addMenu.add_command(label=k[0], command=(lambda x=k[0]: self.addModule(x)))

        self.popupMenu.add_command(label="Delete", command=self.deleteModule)


        startupTheme = self.getSetting("startupTheme", "")
        themeLoaded = False
        if startupTheme:
            themeLoaded = self.loadTheme(startupTheme)
            self.setTime(self.time)
        if not themeLoaded:
            self.newTheme()

        self.updateClock()


    def createMenus(self):
        """ build the main menu """

        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="New", command=self.menu_newTheme)
        self.filemenu.add_command(label="Open..", command=self.menu_loadTheme)
        self.filemenu.add_command(label="Save..", command=self.menu_overrideTheme)
        self.filemenu.add_command(label="Save As..", command=self.menu_saveThemeAs)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.toolsmenu = tk.Menu(self.menubar, tearoff=0)
        self.toolsmenu.add_command(label="run emulated", command=self.menu_runEmulator)
        self.menubar.add_cascade(label="Tools", menu=self.toolsmenu)

        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About", command=self.aboutDlg)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)



    def loadSettings(self):
        """ load settings from config file """

        self.cfg = dict()
        p,n = os.path.split(__file__)
        cfg_path = p+os.sep+'editor_cfg.json'
        try:
            cfg_file  = open(cfg_path, "r")
            self.cfg = json.load(cfg_file)
            cfg_file.close()
        except IOError:
            print "couldn't open settings file (editor_cfg.json)", cfg_path


    def getSetting(self, name, default):
        """
        convenience function to fish settings out of the config
        :param name (string): name of the parameter
        :param default (varying): default returned if parameter is not set
        :return (varying): parameter value
        """
        return self.cfg[name] if name in self.cfg else default



    def updateClock(self):
        """
        used as a periodic time event
        monitoring a few background tasks
        """

        self.time += 0.001
        self.after(100, self.updateClock)

        if self.clientTime:
            dt = time.time() - self.clientTime
            if dt > 2:
                if not self.lampClient.isConnected():
                    self.lampConnect.deselect()
                self.clientTime = time.time()



    def destroy(self):
        self.lampClient.disconnect()
        tk.Frame.destroy(self)


    def loadPoster(self):
        """ load the poster image and calculate a crop window if necessary """

        self.poster = None
        if 'poster' in self.theme:
            posterPath = self.theme['poster']

            if os.path.isfile(posterPath):

                w = self.posterWidth
                h = self.posterHeight
                image = Image.open(posterPath)
                aspect = float(w)/h
                if 'poster_crop' in self.theme:
                    crop = self.theme['poster_crop']
                else: # auto generate a box
                    iw = image.width
                    ih = image.height
                    x0 = 0
                    x1 = iw-1
                    y0 = 0
                    y1 = int(iw/aspect)-1
                    if y1 >= ih:
                        y1 = ih-1
                        x1 = ih*aspect-1
                        x0 += int((iw-(ih*aspect)/2))
                        x1 += int((iw-(ih*aspect)/2))
                    else:
                        y0 += int((ih-iw/aspect)/2)
                        y1 += int((ih-iw/aspect)/2)
                    crop = [x0,y0,x1,y1]
                    self.theme['poster_crop'] = crop

                cropped = image.crop((crop[0],crop[1],crop[2],crop[3]))
                self.poster = cropped
            else:
                print 'poster file not found', posterPath

        if not self.poster:
            self.poster = Image.new('RGB', (self.posterWidth, self.posterHeight), color=(52, 52, 52))


    def updatePosterLabel(self):
        """ resize the poster to the UI and overlay the theme name """

        if self.poster:
            thumb = self.poster.resize( (self.posterWidth, self.posterHeight), resample=Image.LANCZOS ) if (self.poster.width!=self.posterWidth or self.poster.height!=self.posterHeight) else self.poster
        else:
            thumb = Image.new('RGB', (self.posterWidth, self.posterHeight), (55,55,55))

        fnt = ImageFont.truetype(self.posterFont, 40) if self.posterFont else None
        txt = Image.new('RGBA', thumb.size, (255,255,255,0))
        dr = ImageDraw.Draw(txt)
        dr.text((8,8), self.theme['name'], font=fnt, fill=(0,0,0,128))
        dr.text((8,12), self.theme['name'], font=fnt, fill=(0,0,0,128))
        dr.text((12,12), self.theme['name'], font=fnt, fill=(0,0,0,128))
        dr.text((12,8), self.theme['name'], font=fnt, fill=(0,0,0,128))
        dr.text((10,10), self.theme['name'], font=fnt, fill=(255,255,255,180))
        thumb.paste(txt, (0,0), txt)

        self.posterTk = ImageTk.PhotoImage(thumb)
        self.posterLabel.config(image=self.posterTk)


    def selectPoster(self):
        """ open a file browser to choose an image """

        newPoster = tkFileDialog.askopenfilename(initialdir=self.themeRootPath, filetypes=[('image', '*.jpg'),('image', '*.png')], title='Select poster')
        if newPoster and os.path.isfile(newPoster):
            self.theme['poster'] = newPoster
            if 'poster_crop' in self.theme:
                del(self.theme['poster_crop'])
            self.loadPoster()
            self.updatePosterLabel()


    def menu_newTheme(self):
        """ callback for new_theme menu item """

        sure = tkMessageBox.askokcancel(title='New Theme', message='sure?')
        if sure:
            self.newTheme()


    def newTheme(self):
        """ clear the editor of the current theme """

        # tear down
        if self.highlightedModule > -1:
            self.modules[self.highlightedModule].destroyParameters()
            self.highlightedModule = -1
        for m in self.modules:
            m.destroy()
        self.modules = []

        self.poster = None
        self.themePath = ""
        self.theme = { 	"name" : "new theme",
                        "graphics" : [],
                        "sounds" : []
                     }
        self.updatePosterLabel()
        self.prog_themeName.delete(0, tk.END)
        self.prog_themeName.insert(0, self.theme['name'])
        self.master.title('Theme editor - untitled')

        self.createModuleWidgets(self.tracks)


    def menu_loadTheme(self):
        """ callback for load_theme menu item """

        newTheme = tkFileDialog.askopenfilename(initialdir=self.themeRootPath, filetypes=[('Theme', '*.json')], title='Open Theme')
        if newTheme and not newTheme.startswith(self.themeRootPath):
            tkMessageBox.showerror(message='Theme not in root folder: '+self.themeRootPath)
            print newTheme, self.themeRootPath
            return

        if not newTheme or (self.theme and not tkMessageBox.askokcancel(title='Loading theme', message='current theme will be lost. continue?')):
            return

        pathname, filename = os.path.split(newTheme)
        basename, themename = os.path.split(pathname)
        self.loadTheme(themename)



    def loadTheme(self, themename):
        """ load a theme from disk
        :param themename (string): name of the theme (not a full path)
        """

        self.newTheme()
        self.themePath = self.themeRootPath + os.sep + themename
        self.theme = None


        try:
            file = open(self.themePath + os.sep + 'theme.json', "r")
            self.theme = json.load(file)
        except:
            self.theme = None

        if not self.theme:
            print "couldn't open file", self.themePath + os.sep + 'theme.json'
            return False
        else:

            print 'loading theme "%s"...'%self.theme['name'],

            self.modules = list()

            for m in self.theme['graphics']:
                modClass = Modules[m['mod']]
                mod = modClass(m, self.themePath, self.colorScheme, self.modHashCounter, self.lampClient)
                self.modules.append(mod)
                self.modHashCounter += 1
            for m in self.theme['sounds']:
                modClass = Modules[m['mod']]
                mod = modClass(m, self.themePath, self.colorScheme, self.modHashCounter, self.lampClient)
                self.modules.append(mod)
                self.modHashCounter += 1


            if 'poster' in self.theme:
                self.theme['poster'] = self.themePath + os.sep + self.theme['poster']
            self.loadPoster()
            self.updatePosterLabel()

            self.prog_themeName.delete(0, tk.END)
            self.prog_themeName.insert(0, self.theme['name'])

            self.createModuleWidgets(self.tracks)
            self.master.title('Theme editor - ' + self.themePath)
            print 'done.'
            return True




    def menu_overrideTheme(self):
        """ callback for save menu item """

        if self.themePath == "":
            self.menu_saveThemeAs()
            return
        themebase, themename = os.path.split(self.themePath)
        if not tkMessageBox.askyesno(title='Save theme', message='Overwrite existing theme "%s"?'%themename):
            return
        self.saveTheme(self.themePath)


    def menu_saveThemeAs(self):
        """ callback for saveAs menu item """

        newTheme = tkFileDialog.askdirectory(mustexist=True, initialdir=self.themeRootPath, title='Open Theme')
        if newTheme and os.path.isdir(newTheme):
            if os.path.isfile(newTheme+os.path.sep+'theme.json'):
                if not tkMessageBox.askyesno(title='Save theme', message='Theme exists. Overwrite?'):
                    return
            self.saveTheme(newTheme)


    def saveTheme(self, path, replace=True):
        """
        saves the theme to disk. this includes migration of all referenced files into the theme folder.
        :param path (string): path to the theme directory
        :param replace (bool): updates the current theme to the new disk location. set to False to write a copy of the theme to a temp location.
        """

        newTheme = { 'name':self.theme['name'], 'graphics':[], 'sounds':[] }

        if 'LUT' in self.theme:
            newTheme['LUT'] = self.theme['LUT']

        if 'poster' in self.theme:
            posterName = os.path.basename(self.theme['poster'])
            newTheme['poster'] = posterName
            newTheme['posterCrop'] = self.theme['poster_crop']
            # migrate poster into target folder
            newPosterPath = path + os.sep + posterName
            print 'trg poster file',newPosterPath
            if not os.path.isfile(newPosterPath):
                print 'not there, copying'
                shutil.copy2(self.theme['poster'], path)

        for m in self.modules:
            if m.moduleCategory() == 'graphics':
                m.saveInto(newTheme['graphics'], path)
            elif m.moduleCategory() == 'sounds':
                m.saveInto(newTheme['sounds'], path)

        jpp = json.dumps(newTheme, indent=4, sort_keys=True)
        with open(path+os.path.sep+'theme.json', 'w') as outfile:
            outfile.write(jpp)

        if replace:
            self.themePath = path
            self.master.title('Theme editor - ' + self.themePath)



    def menu_runEmulator(self):
        """ saves the current theme to a temp location and calls the emulator. """

        # check if tmp folder exists. delete it if it does
        emPath = self.themeRootPath + os.sep + '_emulatedTheme_'
        if os.path.isdir( emPath ):
            shutil.rmtree(emPath)

        try:
            # create the tmp folder
            os.mkdir(emPath)
        except:
            print "counldn't create temp dir"
            return

        self.saveTheme(emPath ,replace=False)
        cmd = self.getSetting("emulator_cmd", "echo no emulator")
        p = subprocess.Popen( cmd.format(themeName="_emulatedTheme_"))
        p.wait()
        shutil.rmtree(emPath)


    #def dbg(self, *event):
    #    print self.posterLabel.winfo_width(), self.posterLabel.winfo_height()


    def connectToLamp(self):
        """ tries to connect to a running lamp server. """

        if self.connectVar and not self.lampClient.isConnected():
            self.lampClient.connect(self.srvAddressVar.get(), int(self.srvPortVar.get()))
            self.clientTime = time.time()
            print 'attempting to connect to lamp at', self.srvAddressVar.get(), int(self.srvPortVar.get())


    def createProgramParams(self, parentFrame):
        """ set up the general-parameter-area with widgets """

        self.prog_themeFrame = tk.LabelFrame(parentFrame, text='theme', padx=8, pady=8, **self.colorScheme)
        self.prog_themeFrame.pack(side='left')
        self.prog_themeName = tk.Entry(self.prog_themeFrame, **self.colorScheme)
        self.prog_themeName.pack(side='left', padx=8)
        self.prog_themeName.bind('<Return>', self.collectGeneralParams)
        img = tk.PhotoImage(file='loadImageIcon.gif')
        self.posterSelect = tk.Button(self.prog_themeFrame, image=img, command=self.selectPoster, borderwidth=0, activebackground='#333333', **self.colorScheme)
        self.posterSelect.image=img
        self.posterSelect.pack(side='left')

        frm = tk.LabelFrame(parentFrame, text='lamp server', padx=8, pady=8, **self.colorScheme )
        frm.pack(side='left')
        self.srvAddressVar = tk.StringVar()
        self.prog_srv_address = tk.Entry(frm, width=15, textvariable=self.srvAddressVar, **self.colorScheme)
        self.prog_srv_address.pack(side='left')
        self.srvPortVar = tk.StringVar()
        self.prog_srv_port = tk.Spinbox(frm, width=5, from_=0, to=9999, textvariable=self.srvPortVar, readonlybackground=self.colorScheme['background'], **self.colorScheme)
        self.prog_srv_port.pack(side='left')
        self.srvAddressVar.set('10.0.0.69')
        self.srvPortVar.set('9942')
        self.connectVar = tk.IntVar()
        self.lampConnect = tk.Checkbutton(frm, text='connected', height=1, indicatoron=False, variable=self.connectVar, command=self.connectToLamp, selectcolor='#00aa00', **self.colorScheme)
        self.lampConnect.pack()


    def createParamArea(self, parentFrame):
        """ set up the parameter-editor area """

        self.scrollY = tk.Scrollbar(parentFrame, width=20, **self.colorScheme)
        self.scrollY.pack(side='right', fill='y')

        #self.scrollX = tk.Scrollbar(parentFrame, width=20, orient='horizontal', **self.colorScheme)
        #self.scrollX.pack(side='bottom', fill='x')

        self.parameters = tk.Canvas(parentFrame, width=300, yscrollcommand=self.scrollY.set, **self.colorScheme) #xscrollcommand=self.scrollX.set,
        self.parameters.pack(side='left', fill='y', expand='yes')

        self.scr = tk.Frame(self.parameters, padx=8, pady=4, **self.colorScheme)
        self.scr.pack(fill='both', expand='yes')

        self.controlItems = list()
        gr = tk.LabelFrame(self.scr, text='parameters', padx=8, **self.colorScheme)
        gr.pack(fill='x', expand='yes')
        self.controlItems.append( gr )
        self.parameters.create_window(0,0, window=self.scr, width=300, anchor='nw')
        #self.scrollX.config(command=self.parameters.xview)
        self.scrollY.config(command=self.parameters.yview)
        self.scr.update_idletasks()
        self.parameters.config(scrollregion=self.parameters.bbox('all'))



    def popup(self, event):
        """ callback for right-click popup menu """
        self.popupMenu.post(event.x_root, event.y_root)


    def trackFocus(self, event):
        """ handles the connection between the highlighted module and it's parameter-editor area """

        for i, m in enumerate(self.modules):
            if event.widget == m.canvas:

                if i == self.highlightedModule: # nothing to do here
                    return

                if self.highlightedModule > -1:
                    self.modules[self.highlightedModule].destroyParameters()
                    self.modules[self.highlightedModule].setFocus(False)

                self.highlightedModule = i
                m.setFocus(True)
                m.buildParameters(self.scr, self.colorScheme)
                self.scr.update_idletasks()
                self.parameters.config(scrollregion=self.parameters.bbox('all'))
                event.widget.focus_set()
                break


    def createModuleWidgets(self, canvas):
        """ build the widgets for the theme's modules """

        for i, mod in enumerate(self.modules):

            c = mod.createWidgets(canvas, i*62, 800, 60)
            #canvas.create_window(0, i*62, window=c)
            c.bind('<Button-1>', self.trackFocus)
            c.bind('<Button-3>', self.popup)
            c.bind('<Prior>', self.moduleUp)
            c.bind('<Next>', self.moduleDown)

        canvas.bind('<Button-3>', self.popup)


    def setTime(self, val):
        """ updates various parts of the system to a new time. sends redraw requests, dispatches messages to the server, etc """

        self.time = val
        self.timeline.coords(self.cursor, self.time * 800, 0, self.time * 800, 30)

        fc = floatCanvas.Canvas(16, 18) # todo: <-- from cfg
        for m in self.modules:
            m.setTime(val)
            if m.moduleCategory() == 'graphics':
                m.updateCanvas(fc)

        if self.lampClient.isConnected():
            self.lampClient.sendCanvas(fc.data)

        self.previewFrame.updateScreen(fc)

        val *= self.duration
        self.statusBar.config(text='%dm%02ds'%(int(val/60),int(val%60)))




    def drawTimeline(self):

        w = 800 #self.timeline.width
        h = 30 # self.timeline.height
        #print 'w:',w
        for i in xrange(31):
            f = (float(i) / 30) * w
            b = (h/2) if (i%10) else h
            self.timeline.create_line(f, 0, f, b, fill='#606060')
        self.cursor = self.timeline.create_line(self.time * w, 0, self.time * w, h, fill='#C0C0C0')


    def timelineMouseClick(self, event):

        self.timelineMouseCap = True
        x,y = self.timeline.canvasx(event.x), self.timeline.canvasy(event.y)
        t = max(0, min(1, float(x)/800))
        self.setTime(t)


    def timelineMouseMove(self, event):

        if self.timelineMouseCap:
            x,y = self.timeline.canvasx(event.x), self.timeline.canvasy(event.y)
            t = max(0, min(1, float(x)/800))
            self.setTime(t)


    def timelineMouseRelease(self, event):
        self.timelineMouseCap = False


    def createModuleView(self, parentFrame):
        """ create module tracks, timeline and status bar """

        #create timeline
        self.timeline = tk.Canvas(parentFrame, width=800, height=30, **self.colorScheme)
        self.timeline.pack(anchor='w')
        self.drawTimeline()
        self.timeline.bind('<Button-1>', self.timelineMouseClick)
        self.timeline.bind('<Motion>', self.timelineMouseMove)
        self.timeline.bind('<ButtonRelease-1>', self.timelineMouseRelease)

        #create tracks
        self.tracksFrame = tk.Frame(parentFrame, **self.colorScheme)
        self.tracksFrame.pack(fill='both', expand='yes')

        self.tracks_subframe = tk.Frame(self.tracksFrame, **self.colorScheme)
        self.tracks_subframe.pack(anchor='w', fill='both', expand='yes')

        #self.tracks_scrollY = tk.Scrollbar(self.tracks_subframe, width=20, **self.colorScheme)
        #self.tracks_scrollY.pack(side='right', fill='y')
        #self.tracks_scrollX = tk.Scrollbar(self.tracks_subframe, width=20, orient='horizontal', **self.colorScheme)
        #self.tracks_scrollX.pack(side='bottom', fill='x')

        self.tracks = tk.Canvas(self.tracks_subframe, **self.colorScheme)
        self.tracks.pack(fill='both', expand='yes')

        #self.tracks.update_idletasks()
        #self.tracks_scrollX.config(command=self.tracks.xview)
        #self.tracks_scrollY.config(command=self.tracks.yview)
        #self.tracks.config(scrollregion=self.tracks.bbox('all'))
        #self.tracks.config(xscrollcommand=self.tracks_scrollX.set, yscrollcommand=self.tracks_scrollY.set)


        #create status bar
        f = tk.Frame(**self.colorScheme)
        f.pack(fill='x')
        self.statusBar = tk.Label(f, text='0:00', **self.colorScheme)
        self.statusBar.pack(side='right')


    def createWidgets(self):
        """ build the UI """

        # root frame
        self.mainFrame = tk.Frame(self, **self.colorScheme)
        self.mainFrame.pack(fill='both', expand='yes')

        # lamp preview
        self.previewFrame = CircadiaVisualizer(self.mainFrame, self.cfg)

        # frame everything right of lamp
        self.frame1 = tk.Frame(self.mainFrame, borderwidth=2, relief='groove', **self.colorScheme)
        self.frame1.pack(fill='both', expand = 'yes', anchor='n')

        # poster
        self.posterLabel = tk.Label(self.frame1, **self.colorScheme)
        self.posterLabel.pack(side='top', anchor='nw')

        # frame everthing under poster
        self.controlsFrame = tk.Frame(self.frame1, borderwidth=2, relief='groove', **self.colorScheme)
        self.controlsFrame.pack(side='right', fill='both', expand='yes')

        # parameter editor area
        self.paramFrame = tk.Frame(self.controlsFrame, width=250, borderwidth=1, relief='groove', **self.colorScheme)
        self.paramFrame.pack(anchor='e', side='right', fill='y', expand='no')
        self.createParamArea(self.paramFrame)

        # frame work area
        self.workFrame = tk.Frame(self.controlsFrame, **self.colorScheme)
        self.workFrame.pack(side='left', fill='both', expand='yes')

        # global params
        self.programParamsFrame = tk.Frame(self.workFrame, height=200, borderwidth=2, relief='sunken', **self.colorScheme)
        self.programParamsFrame.pack(fill='x')
        self.createProgramParams(self.programParamsFrame)

        # frame Module view
        self.moduleEd = tk.Frame(self.workFrame, **self.colorScheme)
        self.moduleEd.pack(fill='both', expand='yes')
        self.createModuleView(self.moduleEd)

        self.setTime(0.45)


    def moduleUp(self, event):
        """ move the highlighted module up on the stack. bound to PageUp key """

        if self.highlightedModule > 0:

            frm = self.highlightedModule - 1
            to  = self.highlightedModule

            # switch
            self.modules[frm], self.modules[to] = self.modules[to], self.modules[frm]
            for m in self.modules:
                m.canvasFrm.pack_forget()
            for m in self.modules:
                m.canvasFrm.pack(anchor='w')

            self.highlightedModule = frm


    def moduleDown(self, event):
        """ move the highlighted module down on the stack. bound to PageDown key """

        if self.highlightedModule < len(self.modules)-1:

            frm = self.highlightedModule
            to  = self.highlightedModule+1

            # switch
            self.modules[frm], self.modules[to] = self.modules[to], self.modules[frm]
            for m in self.modules:
                m.canvasFrm.pack_forget()
            for m in self.modules:
                m.canvasFrm.pack(anchor='w')

            self.highlightedModule = to


    def addModule(self, typeName):
        """
        :param typeName (string): type name of the module to add
        """

        print 'adding', typeName
        # create default params
        params = Modules[typeName].defaults()
        # add params to the theme
        self.theme[Modules[typeName].moduleCategory()].append(params)
        p = self.theme[Modules[typeName].moduleCategory()][-1]
        # create a new instance of the module
        self.modules.append( Modules[typeName](p, self.themePath, self.colorScheme, self.modHashCounter, self.lampClient) )
        mod = self.modules[-1]
        self.modHashCounter += 1

        c = mod.createWidgets(self.tracks, 0, 800, 60)
        c.bind('<Button-1>', self.trackFocus)
        c.bind('<Button-3>', self.popup)
        c.bind('<Prior>', self.moduleUp)
        c.bind('<Next>', self.moduleDown)


    def deleteModule(self):
        """ delete the highlighted module """

        ind = self.highlightedModule
        if ind > -1:

            self.modules[ind].destroyParameters()
            self.modules[ind].destroy()
            del(self.modules[ind])
            self.highlightedModule = -1


    def collectGeneralParams(self, event):
        """ general purpose callback to check unbound widgets for value changes """

        thName = self.prog_themeName.get()
        if thName != self.theme['name']:
            self.theme['name'] = thName
            self.updatePosterLabel()


    def aboutDlg(self):

        toplevel = tk.Toplevel()

        scrollbar = tk.Scrollbar(toplevel)
        scrollbar.pack(side='right', fill='y')

        aboutTxt = tk.Text(toplevel, height=40, width=100, yscrollcommand=scrollbar.set)
        aboutTxt.insert(tk.INSERT,editAbout.ABOUTTEXT)
        aboutTxt.config(state=tk.DISABLED)
        aboutTxt.pack()

        aboutTxt.master.title('Circadia Theme Editor - %s'%__version__)
        scrollbar.config(command=aboutTxt.yview)




##################################################################################################################
##################################################################################################################



__author__ = 'fhu'
__version__ = "0.9.0"



if __name__ == '__main__':

    root = tk.Tk()
    root.tk.call('tk', 'scaling', 1.0)
    root.title('Theme editor')
    app = Application(master=root)
    app.mainloop()
