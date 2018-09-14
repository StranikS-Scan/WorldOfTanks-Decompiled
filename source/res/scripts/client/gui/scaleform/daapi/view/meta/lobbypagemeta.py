# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyPageMeta.py
from gui.Scaleform.framework.entities.View import View

class LobbyPageMeta(View):

    def moveSpace(self, x, y, delta):
        self._printOverrideError('moveSpace')

    def getSubContainerType(self):
        self._printOverrideError('getSubContainerType')

    def notifyCursorOver3dScene(self, isOver3dScene):
        self._printOverrideError('notifyCursorOver3dScene')

    def as_showHelpLayoutS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_showHelpLayout()

    def as_closeHelpLayoutS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_closeHelpLayout()
