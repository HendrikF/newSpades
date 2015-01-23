#!/usr/bin/python3

print("We're so sorry, but we found no time to fix the Editor.")
print("We will hopefully fix it in the next release :)")
import sys
sys.exit(1)

from tools.ModelEditor import ModelEditor

me = ModelEditor(width=800, height=600, caption='Model Editor - NewSpades', resizable=True)
me.start()
