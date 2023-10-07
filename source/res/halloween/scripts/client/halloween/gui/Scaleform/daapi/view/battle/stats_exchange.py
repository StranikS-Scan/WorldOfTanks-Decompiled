# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/stats_exchange.py
from collections import defaultdict
from helpers import dependency
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import broker
from halloween.skeletons.gui.sound_controller import IHWSoundController

class TeamDamageCollectableStats(broker.CollectableStats):
    __slots__ = ('__damageDealt',)
    _hwSoundController = dependency.descriptor(IHWSoundController)

    def __init__(self):
        super(TeamDamageCollectableStats, self).__init__()
        self.__damageDealt = defaultdict(dict)
        self._hwSoundController.registerStatsController(self)

    def clear(self):
        self._hwSoundController.invalidateStatsController()
        self.__damageDealt.clear()
        super(TeamDamageCollectableStats, self).clear()

    def addVehicleStatsUpdate(self, vInfoVO, vStatsVO):
        self.__damageDealt[vInfoVO.team][vInfoVO.vehicleID] = vStatsVO.interactive.damageDealt

    def addVehicleStatusUpdate(self, vInfoVO):
        pass

    def getTotalStats(self, arenaVisitor, sessionProvider):
        arenaDP = sessionProvider.getArenaDP()
        allyScope, enemyScope = (0, 0)
        for teamID, teamVehicles in self.__damageDealt.iteritems():
            totalDamage = sum(teamVehicles.itervalues())
            if arenaDP.isEnemyTeam(teamID):
                enemyScope += totalDamage
            allyScope += totalDamage

        self._setTotalScore(allyScope, enemyScope)
        return {'leftScope': allyScope,
         'rightScope': enemyScope}


class EventStatisticsDataController(ClassicStatisticsDataController):

    def _createExchangeCollector(self):
        return TeamDamageCollectableStats()
