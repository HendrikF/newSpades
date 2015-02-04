from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox

from client.NewSpades import NewSpades

import logging
logger = logging.getLogger(__name__)

class Launcher(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.build()
    
    def build(self):
        self.master.title('NewSpades - Launcher')
        self.master.config(padx=20, pady=15)
        
        self.master.bind('<Escape>', self.close, True)
        self.master.bind('<Return>', self.connect, True)
        
        self.grid()
        
        Label(self, text='Adress').grid(column=0, row=0)
        Label(self, text='Port').grid(column=1, row=0)
        
        self.addr = Entry(self)
        self.addr.grid(column=0, row=1)
        self.addr.bind('<Return>', self.connect, True)
        
        self.port = Entry(self)
        self.port.grid(column=1, row=1)
        self.port.bind('<Return>', self.connect, True)
        
        self.connectbutton = Button(self, text='connect', command=self.connect)
        self.connectbutton.grid(column=2, row=1)
        
        self.offlinebutton = Button(self, text='start offline', command=self.offline)
        self.offlinebutton.grid(column=2, row=2)
    
    def connect(self, *args):
        messagebox.showinfo('NewSpades', 'Not implemented')
    
    def offline(self, *args):
        logger.info('Starting in offline mode')
        newspades = NewSpades(width=800, height=600, caption='NewSpades', resizable=True)
        newspades.set_exclusive_mouse(True)
        self.close()
        newspades.start()
    
    def close(self, *args):
        self.master.destroy()
