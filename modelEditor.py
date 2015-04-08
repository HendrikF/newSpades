#!/usr/bin/python3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--no-sw', dest='no_shadow_window', action='store_true', help="Don't create pyglets shadow window")
args = parser.parse_args()

if args.no_shadow_window:
    import pyglet
    pyglet.options['shadow_window'] = False
    import logging
    logging.getLogger().info('Running without shadow window')

from tools.ModelEditor import ModelEditor

me = ModelEditor(width=800, height=600, caption='Model Editor - NewSpades', resizable=True)
me.start()
