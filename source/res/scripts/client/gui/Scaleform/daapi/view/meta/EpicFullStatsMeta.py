# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicFullStatsMeta.py
from gui.Scaleform.daapi.view.battle.classic.base_stats import StatsBase

class EpicFullStatsMeta(StatsBase):

    def as_initializeTextS(self, myLaneText, allLanesText):
        return self.flashObject.as_initializeText(myLaneText, allLanesText) if self._isDAAPIInited() else None

    def as_setIsInteractiveS(self, value):
        return self.flashObject.as_setIsInteractive(value) if self._isDAAPIInited() else None
