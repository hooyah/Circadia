"""
    an app to quickly adjust LED gamma curves
    GUI, so needs to run in X
"""

import Tkinter as tk
import tkMessageBox
import json

from MSR_OS.engine import loadConfig
from MSR_OS.floatCanvas import Gradient3
from MSR_HAL import circadiahw


class Application(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.num_ctrl = 6
        self.drwCrv = None
        self.edit = 'red'
        self.sampleValue = 0.5
        self.editColorVar = tk.IntVar()
        self.editPntVar = tk.IntVar()

        self.sys_hw = circadiahw.CircadiaHw
        self.system = dict()
        self.sys_hw.init(self.system, loadConfig('circadia_cfg.json'))
        #self.system['canvas'] = pygame.Surface( (self.system['screen_width'], self.system['screen_height']) )

        self.pack()
        self.createWidgets()
        self.drwCrv = True
        self.gen_exp()


    def gen_exp(self):
        self.gamma_red = list()
        self.gamma_green = list()
        self.gamma_blue = list()
        for v in range(self.num_ctrl):
            vv = float(v)/(self.num_ctrl-1)
            vf = vv = pow(vv, 2)
            vv = int(vv*255)/255.0
            vf = int(pow(vf,2)*255)/255.0
            self.gamma_red.append([vv,vf])
            self.gamma_green.append([vv,vf])
            self.gamma_blue.append([vv,vf])
        self.update_curves()

    def gen_lin(self):
        self.gamma_red = list()
        self.gamma_green = list()
        self.gamma_blue = list()
        for v in range(self.num_ctrl):
            vv = float(v)/(self.num_ctrl-1)
            vv = int(vv*255)/255.0
            self.gamma_red.append([vv,vv])
            self.gamma_green.append([vv,vv])
            self.gamma_blue.append([vv,vv])
        self.update_curves()

    def gen_solo(self):
        self.gamma_red = list()
        self.gamma_green = list()
        self.gamma_blue = list()
        col = int(self.editColorVar.get())
        for v in range(self.num_ctrl):
            vv = float(v)/(self.num_ctrl-1)
            vv = int(vv*255)/255.0

            self.gamma_red.append([vv,vv] if col==0 else [vv,0])
            self.gamma_green.append([vv,vv] if col==1 else [vv,0])
            self.gamma_blue.append([vv,vv] if col==2 else [vv,0])
        self.update_curves()

    def canvas_generateLine(self, line, color):

        coords = list()
        w = 300
        h = 300
        for n,p in enumerate(line):
            x = p[0]*w
            y = h - p[1]*h
            coords.append(x)
            coords.append(y)
            self.canvas.create_oval(x-2, y-2, x+2, y+2, fill=('black' if not (int(self.editPntVar.get())==n) else 'yellow') )

        self.canvas.create_line(*coords, fill=color, smooth=True)


    def update_curves(self):
        if self.drwCrv:
            l = [ (self.gamma_red, 'red'), (self.gamma_green, 'green'), (self.gamma_blue, 'blue') ]
            if self.edit == 'red':
                l[0], l[2] = l[2], l[0]
            elif self.edit == 'green':
                l[1], l[2] = l[2], l[1]

            self.canvas.delete(tk.ALL)
            self.canvas.create_line(self.sampleValue*300+1, 1, self.sampleValue*300+1, 301, fill='grey')
            for i in l:
                self.canvas_generateLine(*i)

    def update_swatches(self):

        c1 = (self.sampleValue*255, self.sampleValue*255, self.sampleValue*255)

        keys = [ [self.gamma_red[x][0], (self.gamma_red[x][1], self.gamma_green[x][1], self.gamma_blue[x][1])] for x in range(self.num_ctrl)]
        grad = Gradient3(keys)
        c2 = grad.eval(self.sampleValue)

        self.colorSwatch.delete(tk.ALL)
        self.colorSwatch.create_rectangle(0, 0, 50, 50, fill='#%02x%02x%02x'%(c1[0], c1[1], c1[2]))
        self.colorSwatch.create_rectangle(51, 1, 100, 50, fill='#%02x%02x%02x'%(c2[0]*255, c2[1]*255, c2[2]*255))

        cn = self.system['canvas']
        cn.fill( c2[0], c2[1], c2[2] )
        self.sys_hw.update_screen(cn)


    def cb_colorRadioSel(self):
        selection = "You selected the option " + str(self.editColorVar.get())
        self.edit = ['red', 'green', 'blue'][self.editColorVar.get()]
        self.update_curves()
        self.cb_pntChanged(int(self.pntSlider.get()))


    def cb_valChanged(self, val):

        pnt = self.pntSlider.get()
        col = self.editColorVar.get()
        gamma = [self.gamma_red, self.gamma_green, self.gamma_blue]

        gamma[col][pnt][1] = (255-int(val))/255.0
        #print pnt, val, self.editColorVar.get()
        self.update_curves()
        self.update_swatches()

    def cb_pntChanged(self, val):
        col = self.editColorVar.get()
        gamma = [self.gamma_red, self.gamma_green, self.gamma_blue]
        self.valslider.set(255-gamma[col][int(val)][1]*255)
        self.update_curves()

    def cb_sampleChanged(self, val):

        self.sampleValue = float(val)/255.0
        self.update_swatches()
        self.update_curves()

    def shutdown(self):
        self.sys_hw.shutdown()
        root.destroy()

    def saveit(self):

        doit = tkMessageBox.askyesno("save gamma curve", "overwrite?")
        if doit:
            keys = [ [self.gamma_red[x][0], (self.gamma_red[x][1], self.gamma_green[x][1], self.gamma_blue[x][1])] for x in range(self.num_ctrl)]
            grad = { 'gamma':keys}
            with open('gamma_grad.json', 'w') as outfile:
                json.dump(grad, outfile)
                print 'written.'

    def loadit(self):

        with open('gamma_grad.json', 'r') as infile:
            grad = json.loads(infile.read())
            for i, k in enumerate(grad['gamma']):
                self.gamma_red[i][0] = k[0]
                self.gamma_green[i][0] = k[0]
                self.gamma_blue[i][0] = k[0]
                self.gamma_red[i][1] = k[1][0]
                self.gamma_green[i][1] = k[1][1]
                self.gamma_blue[i][1] = k[1][2]
            self.update_curves()
            self.cb_pntChanged(int(self.pntSlider.get()))




    def createWidgets(self):


        self.colorEditFrame = tk.LabelFrame(self, text='gamma curves')
        self.hori = tk.Frame(self.colorEditFrame)

        self.colorSel = tk.Frame(self.hori)
        self.R1 = tk.Radiobutton(self.colorSel, text="red", variable=self.editColorVar, value=0, command=self.cb_colorRadioSel)
        self.R1.pack( anchor = tk.W )
        self.R2 = tk.Radiobutton(self.colorSel, text="green", variable=self.editColorVar, value=1, command=self.cb_colorRadioSel)
        self.R2.pack( anchor = tk.W )
        self.R3 = tk.Radiobutton(self.colorSel, text="blue", variable=self.editColorVar, value=2, command=self.cb_colorRadioSel)
        self.R3.pack( anchor = tk.W)
        self.colorSel.pack(side=tk.LEFT)

        self.ec = tk.Frame(self.hori)
        self.canvas = tk.Canvas(self.ec, width=301, height=301)
        self.canvas.pack(side=tk.LEFT)
        self.update_curves()

        self.valslider = tk.Scale(self.ec, orient=tk.VERTICAL, length=300, to=255, showvalue=False, command=self.cb_valChanged)
        self.valslider.pack(side="right")

        self.ec.pack(side='left')
        self.hori.pack()

        self.pntSlider = tk.Scale(self.colorEditFrame, orient=tk.HORIZONTAL, to=self.num_ctrl-1, length=200, command=self.cb_pntChanged, variable=self.editPntVar)
        self.pntSlider.pack(side="bottom")

        self.colorEditFrame.pack()

        self.sampleFrame = tk.LabelFrame(self, text='color sample')

        self.colorSwatch = tk.Canvas(self.sampleFrame, width=100, height=50)
        self.colorSwatch.pack()
        self.sampleSlider = tk.Scale(self.sampleFrame, orient=tk.HORIZONTAL, length=300, to=255, command=self.cb_sampleChanged)
        self.sampleSlider.pack()

        self.sampleFrame.pack(fill='x')

        self.bot = tk.Frame(self)
        self.bot.pack(fill='x')
        self.QUIT = tk.Button(self.bot, text="QUIT", fg="red", command=self.shutdown)
        self.QUIT.pack(side="left")

        #self.spacer = tk.label(self.bot)
        #self.spacer.pack(fill='x')

        self.save = tk.Button(self.bot, text="Save", command=self.saveit)
        self.save.pack(side="right")

        self.save = tk.Button(self.bot, text="Load", command=self.loadit)
        self.save.pack(side="right")

        self.grp = tk.Frame(self.bot)
        self.bt1 = tk.Button(self.bot, text="lin", command=self.gen_lin)
        self.bt1.pack(side=tk.LEFT)
        self.bt2 = tk.Button(self.bot, text="exp", command=self.gen_exp)
        self.bt2.pack(side=tk.LEFT)
        self.bt3 = tk.Button(self.bot, text="solo", command=self.gen_solo)
        self.bt3.pack(side=tk.LEFT)
        self.grp.pack(fill='x')



root = tk.Tk()
app = Application(master=root)
app.mainloop()




__author__ = 'fhu'
