#!/usr/bin/python3
import argparse
import logging, logging.handlers
import os, os.path

parser = argparse.ArgumentParser()
#parser.add_argument('host', nargs='?', help='Serverhost')
#parser.add_argument('-p', '--port', type=int, help='Serverport')
parser.add_argument('-l', '--loglevel', nargs='?', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the severity threshold of logged messages')
args = parser.parse_args()

if args.loglevel:
    loglevel = getattr(logging, args.loglevel)
else:
    loglevel = logging.WARNING

logger = logging.getLogger()
logger.setLevel(loglevel)

consolehandler = logging.StreamHandler()
consolehandler.setLevel(logging.WARNING)
fileformatter = logging.Formatter('%(name)s\t%(levelname)s\t%(message)s')
consolehandler.setFormatter(fileformatter)
logger.addHandler(consolehandler)

if not os.path.exists('logs'):
    try:
        os.mkdir('logs', 0o775)
    except OSError as e:
        logger.warn('Could not create logs directory - %s', e)
if os.path.exists('logs'):
    if not os.path.isdir('logs'):
        logger.warn('Can not add RotatingFileHandler - logs is not a directory')
    else:
        filehandler = logging.handlers.RotatingFileHandler('logs/server.log', maxBytes=10*1024**2, backupCount=3)
        filehandler.setLevel(logging.DEBUG)
        fileformatter = logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s')
        filehandler.setFormatter(fileformatter)
        logger.addHandler(filehandler)

from server.Registry import Registry

from server.Server import Server

registry = Registry()
registry('Server', Server)

# Load scripts here - give them the registry to read, inherit from and write their 'children' into
# TODO: give registry automatically (e.g. wrapper)

server = registry('Server')(registry)
server.start()
