# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/ConnectToSecureChannelWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ConnectToSecureChannelWindowMeta(DAAPIModule):

    def sendPassword(self, value):
        self._printOverrideError('sendPassword')

    def cancelPassword(self):
        self._printOverrideError('cancelPassword')

    def as_infoMessageS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_infoMessage(value)
