#!/usr/bin/python3
from random import randrange
from math import sin, radians
import json

lenx = 20
leny = 15
height = 10

def rand(a=0):
    return round(a+randrange(-50, 50)/1000, 3)

data = []
for x in range(lenx):
    data.append([])
    h = round(sin(radians(x*30))*2+2)
    for y in range(leny):
        data[x].append([])
        for z in range(height):
            color = False
            if z == 0:
                color = (rand(0.5), rand(), rand())
            elif z <= h:
                color = (rand(), rand(0.65), rand())
            data[x][y].append(color)

f = open("map.map", "w")
json.dump(data, f)
f.close()
