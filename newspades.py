#!/usr/bin/python3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--no-sw', dest='no_shadow_window', action='store_true', help="Don't create pyglets shadow window")
parser.add_argument('-l', '--loglevel', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the severity threshold of logged messages')
parser.add_argument('host', nargs='?', help='Host to connect to (no port)')
parser.add_argument('-p', '--port', type=int, help='Port at host to connect to')
parser.add_argument('-u', '--username', help='Username to connect with')
parser.add_argument('-a', '--auto', action='store_true', help='Automatically connect to server')
args = parser.parse_args()

import shared.logging
shared.logging.setup('newspades')
if args.loglevel:
    shared.logging.setLogLevel(args.loglevel)

if args.no_shadow_window:
    import pyglet
    pyglet.options['shadow_window'] = False
    import logging
    logging.getLogger().info('Running without shadow window')

from client.Launcher import Launcher

kw = {}
if args.host:
    kw.update(host=args.host)
if args.port:
    kw.update(port=args.port)
if args.username:
    kw.update(username=args.username)

launcher = Launcher(**kw)

if args.auto:
    launcher.connect()

launcher.mainloop()
