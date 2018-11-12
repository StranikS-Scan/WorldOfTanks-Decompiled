# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/EULA.py
from gui.Scaleform.daapi.view.meta.EULAMeta import EULAMeta
from gui.shared.events import CloseWindowEvent, OpenLinkEvent
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gameplay import IGameplayLogic

class EULADlg(EULAMeta):
    connectionMgr = dependency.descriptor(IConnectionManager)
    gameplay = dependency.descriptor(IGameplayLogic)

    def __init__(self, ctx=None):
        super(EULADlg, self).__init__()
        self.__applied = False
        self.__eulaString = ctx.get('text', '')

    def _populate(self):
        super(EULADlg, self)._populate()
        self.connectionMgr.onDisconnected += self.__onDisconnected

    def _dispose(self):
        super(EULADlg, self)._dispose()
        self.connectionMgr.onDisconnected -= self.__onDisconnected
        self.__eulaString = None
        return

    def onWindowClose(self):
        if not self.__applied:
            self.gameplay.goToLoginByRQ()
        else:
            self.destroy()

    def requestEULAText(self):
        self.as_setEULATextS(self.__eulaString)

    def onApply(self):
        self.__applied = True
        self.__fireEulaClose()
        self.onWindowClose()

    def onLinkClick(self, url):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, url))

    def __fireEulaClose(self):
        self.fireEvent(CloseWindowEvent(CloseWindowEvent.EULA_CLOSED, self.__applied))

    def __onDisconnected(self):
        self.__fireEulaClose()
        self.destroy()
