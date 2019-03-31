# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Waiting.py
# Compiled at: 2011-12-09 14:12:38
from gui.Scaleform.windows import ModalWindow
from gui import InputHandler
from debug_utils import *
import BigWorld, inspect, Keys

class _Waiting(ModalWindow):

    def __init__(self, interruptCallback=lambda : None):
        ModalWindow.__init__(self, 'waiting.swf')
        self.component.position.z = 0.1
        self.callback = interruptCallback
        InputHandler.g_instance.onKeyUp += self.handleKeyUpEvent

    def setMessage(self, message):
        self.setMovieVariable('_root._level0.setMessage', ['#waiting:%s' % message])

    def __del__(self):
        pass

    def close(self):
        InputHandler.g_instance.onKeyUp -= self.handleKeyUpEvent
        ModalWindow.close(self)

    def handleKeyUpEvent(self, event):
        if event.key == Keys.KEY_ESCAPE:
            self.callback()


__waiting = None

class Waiting:
    __window = None
    __waitingStack = []

    @classmethod
    def isVisible(cls):
        return cls.__window is not None

    @staticmethod
    def show(message, isSingle=False, interruptCallback=lambda : None):
        BigWorld.Screener.setEnabled(False)
        if isSingle:
            if not message in Waiting.__waitingStack:
                Waiting.__waitingStack.append(message)
            Waiting.__window = Waiting.__window is None and _Waiting(interruptCallback)
            Waiting.__window.setMessage(message)
            Waiting.__window.active(True)
        else:
            Waiting.__window.setMessage(message)
        return

    @staticmethod
    def hide(message):
        if Waiting.__window is None:
            LOG_DEBUG('Waitin.hide without show: in %s line %d func %s' % inspect.stack()[1][1:4])
            return
        else:
            try:
                Waiting.__waitingStack.remove(message)
            except:
                LOG_DEBUG('Waitin.hide without show: ', message, inspect.stack()[1][1:4])

            if len(Waiting.__waitingStack) == 0:
                Waiting.close()
            return

    @staticmethod
    def close():
        BigWorld.Screener.setEnabled(True)
        if Waiting.__window:
            Waiting.__window.close()
            Waiting.__window = None
            Waiting.__waitingStack = []
        return
