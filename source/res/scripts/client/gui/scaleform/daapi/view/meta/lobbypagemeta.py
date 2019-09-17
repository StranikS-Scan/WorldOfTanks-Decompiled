# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyPageMeta.py
from gui.Scaleform.framework.entities.View import View

class LobbyPageMeta(View):

    def moveSpace(self, x, y, delta):
        self._printOverrideError('moveSpace')

    def getSubContainerTypes(self):
        self._printOverrideError('getSubContainerTypes')

    def notifyCursorOver3dScene(self, isOver3dScene):
        self._printOverrideError('notifyCursorOver3dScene')

    def notifyCursorDragging(self, isDragging):
        self._printOverrideError('notifyCursorDragging')

    def as_showHelpLayoutS(self):
        return self.flashObject.as_showHelpLayout() if self._isDAAPIInited() else None

    def as_closeHelpLayoutS(self):
        return self.flashObject.as_closeHelpLayout() if self._isDAAPIInited() else None

    def as_showWaitingS(self, message):
        return self.flashObject.as_showWaiting(message) if self._isDAAPIInited() else None

    def as_hideWaitingS(self):
        return self.flashObject.as_hideWaiting() if self._isDAAPIInited() else None

    def as_switchLobbyDraggingS(self, value):
        return self.flashObject.as_switchLobbyDragging(value) if self._isDAAPIInited() else None
