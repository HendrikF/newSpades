import pyglet

class Sounds(object):
    def __init__(self):
        pyglet.resource.path = ['client/resources', 'shared/resources']
        pyglet.resource.reindex()
        pyglet.options["audio"] = ("openal","directsound","alsa","silent")
        self.sounds = {
            "death": pyglet.resource.media("death.wav", streaming=False),
            "jump": pyglet.resource.media("jump.wav", streaming=False),
            "land": pyglet.resource.media("land.wav", streaming=False),
            "fallhurt": pyglet.resource.media("fallhurt.wav", streaming=False),
            "build": pyglet.resource.media("build.wav", streaming=False)
        }
    
    def play(self, name):
        self.sounds[name].play()
