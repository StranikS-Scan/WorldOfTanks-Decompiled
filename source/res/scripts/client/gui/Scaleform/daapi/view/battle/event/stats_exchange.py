# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/stats_exchange.py
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import BattleStatisticsDataController
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import createExchangeBroker
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import broker
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import vehicle

class WinPointsCollectableStats(broker.CollectableStats):

    def __init__(self):
        super(WinPointsCollectableStats, self).__init__()
        self.__winPoints = {}

    def clear(self):
        self.__winPoints.clear()
        super(WinPointsCollectableStats, self).clear()

    def addVehicleStatsUpdate(self, vInfoVO, vStatsVO):
        if vStatsVO.interactive:
            self.__winPoints.setdefault(vInfoVO.team, {})[vInfoVO.vehicleID] = vStatsVO.interactive.winPoints

    def addVehicleStatusUpdate(self, vInfoVO):
        pass

    def getTotalStats(self, arenaVisitor, sessionProvider):
        isEnemyTeam = sessionProvider.getArenaDP().isEnemyTeam
        allyScore = sum([ sum(scores.values()) for team, scores in self.__winPoints.iteritems() if not isEnemyTeam(team) ])
        enemyScore = sum([ sum(scores.values()) for team, scores in self.__winPoints.iteritems() if isEnemyTeam(team) ])
        self._setTotalScore(allyScore, enemyScore)
        return {'leftScope': allyScore,
         'rightScope': enemyScore}


class VehicleWinPointsComponent(vehicle.VehicleStatsComponent):

    def addStats(self, vStatsVO):
        pass


class EventStatisticsDataController(BattleStatisticsDataController):

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(VehicleWinPointsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker

    def _createExchangeCollector(self):
        return WinPointsCollectableStats()
