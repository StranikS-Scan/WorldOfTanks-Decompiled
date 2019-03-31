# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/InputHandler.py
# Compiled at: 2011-10-17 20:37:51
import Event
g_instance = None

class _InputHandler:
    onKeyDown = Event.Event()
    onKeyUp = Event.Event()

    def handleKeyEvent(self, event):
        if event.isKeyDown():
            self.onKeyDown(event)
        else:
            self.onKeyUp(event)


g_instance = _InputHandler()
