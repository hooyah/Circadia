"""
    Simple color widget to change the screen color of the sunrise lamp

    Run in X on the hardware, or on windows
"""

import Tkinter as tk

from MSR_OS import engine
from MSR_HAL import circadiahw
from Utils import TkColorEdit



class Application(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.sys_hw = circadiahw.CircadiaHw
        self.system = dict()
        self.sys_hw.init(self.system, engine.loadConfig('circadia_cfg.json'))

        self.pack()
        self.createWidgets()


    def shutdown(self):
        self.sys_hw.shutdown()
        root.destroy()


    def update(self, r, g, b):
        cn = self.system['canvas']
        cn.fill( r/255.0, g/255.0, b/255.0 )
        self.sys_hw.update_screen(cn)


    def createWidgets(self):


        self.colorEdit = TkColorEdit.ColorEdit(self, 0,0,0, self.update)
        self.colorEdit.pack()


        self.QUIT = tk.Button(self, text="QUIT", fg="red", command=self.shutdown)
        self.QUIT.pack()




root = tk.Tk()
app = Application(master=root)
app.mainloop()











__author__ = 'fhu'
