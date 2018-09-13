# Embedded file name: scripts/client/gui/Scaleform/Postmortem.py
import BigWorld
from gui import DEPTH_OF_Postmortem
from gui.Scaleform.windows import ModalWindow
from debug_utils import LOG_DEBUG

class _Postmortem(ModalWindow):

    def __init__(self, continueCallback):
        ModalWindow.__init__(self, 'postmortem.swf')
        self.movie.backgroundAlpha = 0.0
        self.component.position.z = DEPTH_OF_Postmortem
        if hasattr(BigWorld.player(), 'setForcedGuiControlMode'):
            BigWorld.player().setForcedGuiControlMode(True)
        self.__continueCallback = continueCallback
        self.addFsCallbacks({'postmortem.Exit': self.onExit,
         'postmortem.Continue': self.onContinue})

    def close(self):
        self.__continueCallback = None
        ModalWindow.close(self)
        return

    def onExit(self, arg):
        LOG_DEBUG('onExitBattle')
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena:
            BigWorld.player().leaveArena()
        Postmortem.hide()
        return

    def onContinue(self, arg):
        if hasattr(BigWorld.player(), 'setForcedGuiControlMode'):
            BigWorld.player().setForcedGuiControlMode(False)
        self.__continueCallback()
        Postmortem.hide()


__waiting = None

class Postmortem:
    __window = None

    @staticmethod
    def show(continueCallback):
        if Postmortem.__window is None:
            Postmortem.__window = _Postmortem(continueCallback)
            Postmortem.__window.active(True)
        return

    @staticmethod
    def hide():
        if Postmortem.__window is not None:
            Postmortem.__window.close()
            Postmortem.__window = None
        return
