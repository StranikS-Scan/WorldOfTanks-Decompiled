# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SquadWindowMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyMainWindow import BaseRallyMainWindow

class SquadWindowMeta(BaseRallyMainWindow):

    def as_setComponentIdS(self, componentId):
        return self.flashObject.as_setComponentId(componentId) if self._isDAAPIInited() else None

    def as_updateEventTitleS(self):
        return self.flashObject.as_updateEventTitle() if self._isDAAPIInited() else None
