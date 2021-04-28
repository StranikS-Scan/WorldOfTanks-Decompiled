# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WBBattleStatisticDataControllerMeta.py
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController

class WBBattleStatisticDataControllerMeta(ClassicStatisticsDataController):

    def as_setWBVehiclesStatsS(self, data):
        return self.flashObject.as_setWBVehiclesStats(data) if self._isDAAPIInited() else None

    def as_updateWBVehiclesStatsS(self, data):
        return self.flashObject.as_updateWBVehiclesStats(data) if self._isDAAPIInited() else None
