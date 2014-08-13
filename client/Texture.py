from OpenGL.GL import *
from OpenGL.GLU import *
import pygame

class Texture(object):
    def __init__(self, filename):
        self.filename = filename
        self.img = pygame.image.load("png/{}.png".format(self.filename))
        self.img.convert_alpha()
        self.texture_data = pygame.image.tostring(self.img, 'RGBA', True)
        self.texture_id = glGenTextures(1)
    
    def enable(self):
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.img.get_width(), self.img.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, self.texture_data)
        glEnable(GL_TEXTURE_2D)
    
    def disable(self):
        glDisable(GL_TEXTURE_2D)
