# Embedded file name: scripts/client/gui/InputHandler.py
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
