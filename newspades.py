#! /usr/bin/python3
import argparse
from client.NewSpades import NewSpades
from shared import logging

parser = argparse.ArgumentParser()
#parser.add_argument('host', nargs='?', help='Serverhost')
#parser.add_argument('-p', '--port', type=int, help='Serverport')
parser.add_argument('-l', '--loglevel', nargs='?', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the severity threshold of logged messages')
args = parser.parse_args()

logging.setup('newspades')
if args.loglevel:
    logging.setLogLevel(args.loglevel)

newspades = NewSpades(width=800, height=600, caption='NewSpades', resizable=True)
newspades.set_exclusive_mouse(True)
newspades.start()
