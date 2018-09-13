# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseRallyMainWindowMeta.py
from gui.Scaleform.daapi.view.lobby.rally.AbstractRallyWindow import AbstractRallyWindow

class BaseRallyMainWindowMeta(AbstractRallyWindow):

    def onBackClick(self):
        self._printOverrideError('onBackClick')

    def getClientID(self):
        self._printOverrideError('getClientID')
