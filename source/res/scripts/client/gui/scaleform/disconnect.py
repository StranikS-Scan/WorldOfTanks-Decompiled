# Embedded file name: scripts/client/gui/Scaleform/Disconnect.py
import BigWorld
from helpers.i18n import makeString
from gui import DEPTH_OF_Disconnect
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.windows import ModalWindow
from gui.Scaleform.CursorDelegator import g_cursorDelegator

class _Disconnect(ModalWindow):

    def __init__(self):
        ModalWindow.__init__(self, 'disconnect.swf')
        self.movie.backgroundAlpha = 0.0
        self.component.position.z = DEPTH_OF_Disconnect
        if hasattr(BigWorld.player(), 'setForcedGuiControlMode'):
            BigWorld.player().setForcedGuiControlMode(True)

    def show(self, reason = None, isBan = None, expiryTime = None):
        Waiting.close()
        g_cursorDelegator.syncMousePosition(self, None, None)
        params = {'reason': '',
         'expiryTime': ''}
        if reason:
            params['reason'] = makeString('#dialogs:disconnected/reason', makeString(reason))
        if expiryTime:
            from helpers.time_utils import makeLocalServerTime
            expiryTime = makeLocalServerTime(int(expiryTime))
            params['expiryTime'] = BigWorld.wg_getLongDateFormat(expiryTime) + ' ' + BigWorld.wg_getLongTimeFormat(expiryTime)
        message = 'messageKick' if not isBan else ('messageBanPeriod' if expiryTime else 'messageBan')
        message = makeString('#dialogs:disconnected/' + message) % params
        self.setMovieVariable('_root._level0.setMessage', [message])
        return

    def handleMouseEvent(self, comp, event):
        return self.movie.handleMouseEvent(event)


__waiting = None

class Disconnect:
    __window = None

    @staticmethod
    def show():
        if Disconnect.__window is None:
            Disconnect.__showParentCursor(False)
            Disconnect.__window = _Disconnect()
            Disconnect.__window.active(True)
            Waiting.close()
        return

    @staticmethod
    def showKick(reason, isBan, expiryTime):
        if Disconnect.__window is None:
            Disconnect.__showParentCursor(False)
            Disconnect.__window = _Disconnect()
            Disconnect.__window.show(reason, isBan, expiryTime)
            Disconnect.__window.active(True)
            Waiting.close()
        return

    @staticmethod
    def __showParentCursor(isShow):
        from gui.WindowsManager import g_windowsManager
        if g_windowsManager.battleWindow is not None:
            g_windowsManager.battleWindow.showCursor(isShow)
        return

    @staticmethod
    def hide():
        Disconnect.__showParentCursor(True)
        if Disconnect.__window is not None:
            Disconnect.__window.close()
            Disconnect.__window = None
        return

    @staticmethod
    def getWindow():
        return Disconnect.__window
