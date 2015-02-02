from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox

class Launcher(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.build()
    
    def build(self):
        self.master.title('NewSpades - Launcher')
        self.master.config(padx=70, pady=50)
        
        self.master.bind('<Escape>', self.close, True)
        self.master.bind('<Return>', self.connect, True)
        
        self.columnconfigure(0, weight=1)
        #self.columnconfigure(1, weight=0)
        #self.columnconfigure(2, weight=0)
        """self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)"""
        self.pack(expand=True, fill=BOTH)
        
        self.addr = Entry(self)
        self.addr.grid(column=0, row=0)
        self.addr.bind("<Return>", self.connect, True)
        
        self.port = Entry(self)
        self.port.grid(column=1, row=0)
        self.port.bind("<Return>", self.connect, True)
        
        self.connectbutton = Button(self, text='connect', command=self.connect)
        self.connectbutton.grid(column=2, row=0)
    
    def connect(self, *args):
        print('connect')
    
    def close(self, *args):
        self.master.destroy()

master = Tk()
launcher = Launcher(master)
launcher.mainloop()
