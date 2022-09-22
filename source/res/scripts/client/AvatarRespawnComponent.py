# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarRespawnComponent.py
from script_component.DynamicScriptComponent import DynamicScriptComponent

class AvatarRespawnComponent(DynamicScriptComponent):

    def _onAvatarReady(self):
        self.entity.inputHandler.onPostmortemKillerVisionExit += self.showSelector

    def onDestroy(self):
        self.entity.inputHandler.onPostmortemKillerVisionExit -= self.showSelector
        self.hideSelector()
        super(AvatarRespawnComponent, self).onDestroy()

    @property
    def _uiCtrl(self):
        return self.entity.guiSessionProvider.dynamic.spawn

    def showSelector(self):
        if self._uiCtrl:
            points = [ {'guid': point['guid'],
             'position': (point['position'].x, point['position'].y)} for point in self.points ]
            self._uiCtrl.showSpawnPoints(points, self.pointGuid)

    def hideSelector(self):
        if self._uiCtrl:
            self._uiCtrl.closeSpawnPoints()
