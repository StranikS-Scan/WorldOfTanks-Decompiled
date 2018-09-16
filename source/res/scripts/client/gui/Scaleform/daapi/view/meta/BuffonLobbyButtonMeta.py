# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BuffonLobbyButtonMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BuffonLobbyButtonMeta(BaseDAAPIComponent):

    def buttonIsClicked(self):
        self._printOverrideError('buttonIsClicked')

    def as_initButtonS(self, data):
        return self.flashObject.as_initButton(data) if self._isDAAPIInited() else None

    def as_showBuffonS(self):
        return self.flashObject.as_showBuffon() if self._isDAAPIInited() else None

    def as_hideBuffonS(self):
        return self.flashObject.as_hideBuffon() if self._isDAAPIInited() else None

    def as_haveBuffonCardS(self):
        return self.flashObject.as_haveBuffonCard() if self._isDAAPIInited() else None

    def as_crewmanBuffonAssignedS(self):
        return self.flashObject.as_crewmanBuffonAssigned() if self._isDAAPIInited() else None
