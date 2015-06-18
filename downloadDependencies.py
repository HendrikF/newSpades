#!/usr/bin/python3
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import os

def downloadZipFile(url, destPath, zipPath=''):
    if not destPath.endswith(':') and not os.path.exists(destPath):
        os.mkdir(destPath)

    print('Opening '+url)
    with urlopen(url) as data:
        zipfile = ZipFile(BytesIO(data.read()))
        
        print('creating directory structure')
        for name in zipfile.namelist():
            if name.startswith(zipPath) and name.endswith('/'):
                name = name.replace(zipPath, '')
                d = os.path.join(destPath, name)
                print(d)
                if not os.path.exists(d):
                    os.mkdir(d)
        
        print('writing files')
        for name in zipfile.namelist():
            if name.startswith(zipPath) and not name.endswith('/'):
                name2 = name.replace(zipPath, '')
                print(name2)
                with open(os.path.join(destPath, name2), 'wb') as outfile:
                    outfile.write(zipfile.read(name))

downloadZipFile(
    'https://github.com/HendrikF/transmitter/archive/v0.4.2.zip',
    'transmitter',
    'transmitter-0.4.2/transmitter/')

downloadZipFile(
    'https://github.com/HendrikF/events/archive/v0.1.2.zip',
    'events',
    'events-0.1.2/events/')
