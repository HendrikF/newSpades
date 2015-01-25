New Spades
===========
This game is developed by KingEik and HendrikF.
It consists of a client and a server and is inspired by the old Beta version (0.75) of [Ace of Spades](http://buildandshoot.com/).
It is in pre-alpha state.
Dependencies may change or be included in future.

Running the game
-----------------
To run the client use:

    ./newspades.py

To run the server use:

    ./server.py

Keep in mind, that this is in pre-alpha state! We cannot guarantee that every commit is stable or that the version of the client matches the server.

Requirements
-------------
To run the game you need to install:

* Python 3.2 or newer: https://www.python.org/download/

(We tested with 3.2 and 3.4)

Known problems
---------------

### Shadow window / Shared Context
When you encounter errors like the following, try to run `./newspades.py --no-sw`.
This disables pyglets shadow window and should solve the problem.
If it doesn't, please run `./newspades.py --loglevel DEBUG` and mail us the contents of the `logs/` folder.

    Traceback (most recent call last):
      File "_________\newspades.py", line 19, in <module>
        newspades = NewSpades(width=800, height=600, caption='NewSpades', resizable=True)
      File "_________\client\NewSpades.py", line 24, in __init__
        super(NewSpades, self).__init__(*args, **kw)
      File "_________\shared\BaseWindow.py", line 8, in __init__
        super(BaseWindow, self).__init__(*args, **kw)
      File "_________\pyglet\window\win32\__init__.py", line 131, in __init__
        super(Win32Window, self).__init__(*args, **kwargs)
      File "_________\pyglet\window\__init__.py", line 558, in __init__
        self._create()
      File "_________\pyglet\window\win32\__init__.py", line 261, in _create
        self.context.attach(self.canvas)
      File "_________\pyglet\gl\win32.py", line 263, in attach
        super(Win32ARBContext, self).attach(canvas)
      File "_________\pyglet\gl\win32.py", line 208, in attach
        raise gl.ContextException('Unable to share contexts')
    pyglet.gl.ContextException: Unable to share contexts

Thanks
-------
* https://github.com/fogleman/Minecraft (MIT-License)

License
--------
NewSpades is released under the GNU GPLv3. See `LICENSE.md` and `GPLv3.md` for Details.

Legal stuff
------------
NewSpades comes with a few libraries included.

Library | License
--------|--------
[pyglet](http://pyglet.org/) | [3-clause-BSD](https://code.google.com/p/pyglet/source/browse/LICENSE)
[AVbin](http://avbin.github.io/AVbin/Home/Home.html) | [GNU LGPL](https://github.com/AVbin/AVbin/blob/master/COPYING.LESSER)
[transmitter](https://github.com/HendrikF/transmitter) | [3-clause-BSD](https://github.com/HendrikF/transmitter/blob/master/LICENSE)
[The Ubuntu Font](http://font.ubuntu.com/) | http://font.ubuntu.com/licence/
