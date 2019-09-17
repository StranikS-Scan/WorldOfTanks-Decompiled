# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FestRaceBattleStatisticDataControllerMeta.py
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController

class FestRaceBattleStatisticDataControllerMeta(ClassicStatisticsDataController):

    def as_setSingleSideVehiclesInfoS(self, data):
        return self.flashObject.as_setSingleSideVehiclesInfo(data) if self._isDAAPIInited() else None

    def as_updateFestRaceVehiclesStatsS(self, data):
        return self.flashObject.as_updateFestRaceVehiclesStats(data) if self._isDAAPIInited() else None
