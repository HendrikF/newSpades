from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox

from client.NewSpades import NewSpades

import logging
logger = logging.getLogger(__name__)

class Launcher(Frame):
    def __init__(self, master=None, **kw):
        Frame.__init__(self, master)
        # http://stackoverflow.com/a/4140988/3447531
        # %P = value of the entry if the edit is allowed
        self._validatePort = (self.master.register(self.validatePort), '%P')
        # For Auto-connect
        self.presets = kw
        self.build()
    
    def build(self):
        self.master.title('NewSpades - Launcher')
        self.master.config(padx=20, pady=15)
        
        self.grid()
        
        Label(self, text='Adress').grid(column=0, row=0)
        Label(self, text='Port').grid(column=1, row=0)
        Label(self, text='Username').grid(column=0, row=2)
        
        self.addr = Entry(self, justify=CENTER)
        self.addr.insert(0, self.presets.get('host', 'localhost'))
        self.addr.grid(column=0, row=1)
        
        self.port = Entry(self, justify=CENTER, validate=ALL, validatecommand=self._validatePort)
        self.port.insert(0, self.presets.get('port', '55555'))
        self.port.grid(column=1, row=1)
        
        self.username = Entry(self, justify=CENTER)
        self.username.insert(0, self.presets.get('username', 'Greenhorn'))
        self.username.grid(column=1, row=2)
        
        self.progressbar = Progressbar(self, maximum=6)
        self.progressbar.grid(column=0, row=3, columnspan=3, sticky=E+W)
        
        self.master.bind('<Escape>', self.close, True)
        self.master.bind('<Return>', self.connect, True)
        self.addr.bind('<Return>', self.connect, True)
        self.port.bind('<Return>', self.connect, True)
        self.username.bind('<Return>', self.connect, True)
        
        self.connectbutton = Button(self, text='connect', command=self.connect)
        self.connectbutton.grid(column=2, row=1)
        
        self.offlinebutton = Button(self, text='start offline', command=self.offline)
        self.offlinebutton.grid(column=2, row=2)
    
    def connect(self, *args):
        self.connectbutton['state'] = 'disabled'
        self.offlinebutton['state'] = 'disabled'
        logger.info('Starting in online mode')
        newspades = NewSpades(progressbar=self.progressbar, width=800, height=600, caption='NewSpades', resizable=True, visible=False)
        host, port, username = self.addr.get().strip(), int(self.port.get()), self.username.get().strip()
        import socket
        try:
            newspades.connect(host, port, username)
        except socket.error as e:
            newspades.close()
            messagebox.showerror('NewSpades', "Can't connect to server: {}".format(e))
        else:
            newspades.set_visible()
            newspades.set_exclusive_mouse(True)
            self.close()
            newspades.start()
    
    def offline(self, *args):
        self.connectbutton['state'] = 'disabled'
        self.offlinebutton['state'] = 'disabled'
        logger.info('Starting in offline mode')
        newspades = NewSpades(progressbar=self.progressbar, width=800, height=600, caption='NewSpades', resizable=True, visible=False)
        newspades.set_exclusive_mouse(True)
        newspades.set_visible()
        self.close()
        newspades.start()
    
    def close(self, *args):
        self.master.destroy()
    
    def validatePort(self, P):
        if len(P) == 0:
            return True
        try:
            P = int(P)
        except ValueError:
            return False
        if 1 <= P <= 65535:
            return True
        return False
