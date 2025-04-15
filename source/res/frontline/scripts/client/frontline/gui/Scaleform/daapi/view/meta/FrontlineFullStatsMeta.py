# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/meta/FrontlineFullStatsMeta.py
from gui.Scaleform.daapi.view.battle.shared.base_stats import StatsBase

class FrontlineFullStatsMeta(StatsBase):

    def as_initializeTextS(self, myLaneText, allLanesText):
        return self.flashObject.as_initializeText(myLaneText, allLanesText) if self._isDAAPIInited() else None

    def as_setIsInteractiveS(self, value):
        return self.flashObject.as_setIsInteractive(value) if self._isDAAPIInited() else None

    def as_setGeneralBonusS(self, value):
        return self.flashObject.as_setGeneralBonus(value) if self._isDAAPIInited() else None
