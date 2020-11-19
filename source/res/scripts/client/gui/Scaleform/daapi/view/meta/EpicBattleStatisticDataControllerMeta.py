# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicBattleStatisticDataControllerMeta.py
from gui.Scaleform.daapi.view.battle.shared.stats_exchange.stats_ctrl import BattleStatisticsDataController

class EpicBattleStatisticDataControllerMeta(BattleStatisticsDataController):

    def as_updateEpicPlayerStatsS(self, data):
        return self.flashObject.as_updateEpicPlayerStats(data) if self._isDAAPIInited() else None

    def as_setEpicVehiclesStatsS(self, data):
        return self.flashObject.as_setEpicVehiclesStats(data) if self._isDAAPIInited() else None

    def as_updateEpicVehiclesStatsS(self, data):
        return self.flashObject.as_updateEpicVehiclesStats(data) if self._isDAAPIInited() else None
