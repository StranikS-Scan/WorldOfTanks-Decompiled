# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyMenuMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class LobbyMenuMeta(AbstractWindowView):

    def settingsClick(self):
        self._printOverrideError('settingsClick')

    def cancelClick(self):
        self._printOverrideError('cancelClick')

    def refuseTraining(self):
        self._printOverrideError('refuseTraining')

    def logoffClick(self):
        self._printOverrideError('logoffClick')

    def quitClick(self):
        self._printOverrideError('quitClick')

    def versionInfoClick(self):
        self._printOverrideError('versionInfoClick')

    def as_setVersionMessageS(self, message, showLinkButton):
        if self._isDAAPIInited():
            return self.flashObject.as_setVersionMessage(message, showLinkButton)
