# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBasesPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventBasesPanelMeta(BaseDAAPIComponent):

    def as_setBase1IDS(self, id):
        return self.flashObject.as_setBase1ID(id) if self._isDAAPIInited() else None

    def as_setBase2IDS(self, id):
        return self.flashObject.as_setBase2ID(id) if self._isDAAPIInited() else None

    def as_setBase1StateS(self, owningTeam, attackingTeam):
        return self.flashObject.as_setBase1State(owningTeam, attackingTeam) if self._isDAAPIInited() else None

    def as_setBase2StateS(self, owningTeam, attackingTeam):
        return self.flashObject.as_setBase2State(owningTeam, attackingTeam) if self._isDAAPIInited() else None

    def as_setBase1ProgressS(self, progress, time):
        return self.flashObject.as_setBase1Progress(progress, time) if self._isDAAPIInited() else None

    def as_setBase2ProgressS(self, progress, time):
        return self.flashObject.as_setBase2Progress(progress, time) if self._isDAAPIInited() else None

    def as_setVisibilityS(self, vis):
        return self.flashObject.as_setVisibility(vis) if self._isDAAPIInited() else None

    def as_setColorBlindS(self, isBlind):
        return self.flashObject.as_setColorBlind(isBlind) if self._isDAAPIInited() else None
