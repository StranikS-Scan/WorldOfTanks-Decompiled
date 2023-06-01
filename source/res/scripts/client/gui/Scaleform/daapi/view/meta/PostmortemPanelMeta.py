# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PostmortemPanelMeta.py
from gui.Scaleform.daapi.view.meta.BasePostmortemPanelMeta import BasePostmortemPanelMeta

class PostmortemPanelMeta(BasePostmortemPanelMeta):

    def onDogTagKillerInPlaySound(self):
        self._printOverrideError('onDogTagKillerInPlaySound')

    def onDogTagKillerOutPlaySound(self):
        self._printOverrideError('onDogTagKillerOutPlaySound')

    def onVictimDogTagInPlaySound(self):
        self._printOverrideError('onVictimDogTagInPlaySound')

    def as_showDeadReasonS(self):
        return self.flashObject.as_showDeadReason() if self._isDAAPIInited() else None

    def as_setPlayerInfoS(self, playerInfo):
        return self.flashObject.as_setPlayerInfo(playerInfo) if self._isDAAPIInited() else None

    def as_showKillerDogTagS(self, data):
        return self.flashObject.as_showKillerDogTag(data) if self._isDAAPIInited() else None

    def as_showVictimDogTagS(self, data):
        return self.flashObject.as_showVictimDogTag(data) if self._isDAAPIInited() else None

    def as_preloadComponentsS(self, components):
        return self.flashObject.as_preloadComponents(components) if self._isDAAPIInited() else None

    def as_hideComponentsS(self):
        return self.flashObject.as_hideComponents() if self._isDAAPIInited() else None
