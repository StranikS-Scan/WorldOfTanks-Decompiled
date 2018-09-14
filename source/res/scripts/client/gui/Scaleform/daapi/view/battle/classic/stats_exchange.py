# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/stats_exchange.py
from collections import defaultdict
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import BattleStatisticsDataController
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import createExchangeBroker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import broker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import vehicle

class FragsCollectableStats(broker.CollectableStats):
    __slots__ = ('__teamsDeaths',)

    def __init__(self):
        super(FragsCollectableStats, self).__init__()
        self.__teamsDeaths = defaultdict(set)

    def clear(self):
        self.__teamsDeaths.clear()
        super(FragsCollectableStats, self).clear()

    def addVehicleStatsUpdate(self, vInfoVO, vStatsVO):
        self.addVehicleStatusUpdate(vInfoVO)

    def addVehicleStatusUpdate(self, vInfoVO):
        if not vInfoVO.isAlive():
            self.__teamsDeaths[vInfoVO.team].add(vInfoVO.vehicleID)

    def getTotalStats(self, arenaDP):
        isEnemyTeam = arenaDP.isEnemyTeam
        allyScope, enemyScope = (0, 0)
        for teamIdx, vehicleIDs in self.__teamsDeaths.iteritems():
            score = len(vehicleIDs)
            if isEnemyTeam(teamIdx):
                allyScope += score
            enemyScope += score

        self._setTotalScore(allyScope, enemyScope)
        if allyScope or enemyScope:
            return {'leftScope': allyScope,
             'rightScope': enemyScope}
        else:
            return {}


class VehicleFragsComponent(vehicle.VehicleStatsComponent):
    __slots__ = ('_frags', '_vehicleID')

    def __init__(self):
        super(VehicleFragsComponent, self).__init__()
        self._frags = 0

    def clear(self):
        self._frags = 0
        super(VehicleFragsComponent, self).clear()

    def get(self, forced=False):
        if forced or self._frags:
            data = super(VehicleFragsComponent, self).get()
            data['frags'] = self._frags
            return data
        else:
            return {}

    def addStats(self, vStatsVO):
        self._vehicleID = vStatsVO.vehicleID
        self._frags = vStatsVO.frags


class ClassicStatisticsDataController(BattleStatisticsDataController):

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(vehicle.VehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(), vehicle.TeamsCorrelationIDsComposer()), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(VehicleFragsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(vehicle.TeamsSortedIDsComposer(), vehicle.TeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker

    def _createExchangeCollector(self):
        return FragsCollectableStats()
