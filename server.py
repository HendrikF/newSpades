#!/usr/bin/python3
import argparse
import sys
import os
from importlib import import_module

import shared.logging

###################
# Setup argparser

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--loglevel', nargs='?', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the severity threshold of logged messages')
parser.add_argument('-c', '--create-config', action='store_true', dest='create_config', help='Only create default config file and exit')
args = parser.parse_args()

#################
# Setup logging

shared.logging.setup('server')
if args.loglevel:
    shared.logging.setLogLevel(args.loglevel)

import logging
logger = logging.getLogger()

#########################
# Write and load config

from server import config

if args.create_config:
    # config created by importing config, we can exit
    sys.exit()

##########################
# Load core & scripts

from events.Events import Events
events = Events()

recorders = {}

@events.subscribe
def script_load(parent, name, module = 'scripts'):
    parts = '.'.join((module, name))
    error = None
    try:
        if parts in recorders:
            raise ImportError('Script already loaded')
        module = import_module(parts)
        recorder = events.recorder()
        module.applyScript(recorder)
    except ImportError as e:
        error = "Script '%s' not loaded: %r" % (parts, e)
    except (AttributeError, TypeError, Exception) as e:
        error = "Script '%s' not loaded: %r" % (parts, e)
        sys.modules.pop(parts, None)
    else:
        recorders[parts] = recorder
    if error:
        print(error)
        return error

@events.subscribe
def script_unload(parent, name, module = 'scripts'):
    parts = '.'.join((module, name))
    if parts in recorders:
        recorders[parts].unsubscribe_all()
        recorders.pop(parts, None)
        sys.modules.pop(parts, None)
    else:
        error = "Script '%s' not unloaded: it was not loaded" % (name)
        print(error)
        return error

# load all core scripts
for fname in os.listdir('./server/core'):
    if fname.endswith('.py') and fname != '__init__.py':
        events.invoke('script_load', fname[:-3], 'server.core')

# load scripts from config
for name in config.get('scripts', []):
    events.invoke('script_load', name)

events.invoke('scripts_loaded')

##########################
# Start server

from server.Server import Server

server = Server(events)

server.start()
