#! /usr/bin/python3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--no-sw', dest='no_shadow_window', action='store_true', help="Don't create pyglets shadow window")
parser.add_argument('-l', '--loglevel', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the severity threshold of logged messages')
args = parser.parse_args()

from shared import logging
logging.setup('newspades')
if args.loglevel:
    logging.setLogLevel(args.loglevel)

if args.no_shadow_window:
    import pyglet
    pyglet.options['shadow_window'] = False
    import logging
    logging.getLogger().info('Running without shadow window')

from client.NewSpades import NewSpades
newspades = NewSpades(width=800, height=600, caption='NewSpades', resizable=True)
newspades.set_exclusive_mouse(True)
newspades.start()
