# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/Comp7BattleStatisticDataControllerMeta.py
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController

class Comp7BattleStatisticDataControllerMeta(ClassicStatisticsDataController):

    def as_removePointOfInterestS(self, vehicleID, type):
        return self.flashObject.as_removePointOfInterest(vehicleID, type) if self._isDAAPIInited() else None

    def as_updatePointOfInterestS(self, data):
        return self.flashObject.as_updatePointOfInterest(data) if self._isDAAPIInited() else None
