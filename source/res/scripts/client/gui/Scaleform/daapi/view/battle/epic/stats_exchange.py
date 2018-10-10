# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/stats_exchange.py
import logging
from gui.Scaleform.daapi.view.meta.EpicBattleStatisticDataControllerMeta import EpicBattleStatisticDataControllerMeta
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import createExchangeBroker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import broker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import vehicle
from gui.battle_control.arena_info import vos_collections
from epic_constants import EPIC_BATTLE_TEAM_ID
from gui.battle_control.arena_info.arena_vos import EPIC_BATTLE_KEYS
from gui.battle_control import avatar_getter
_logger = logging.getLogger(__name__)

class EpicStatsComponent(vehicle.VehicleStatsComponent):
    __slots__ = ('_rank', '_frags', '_lane', '_hasRespawns')

    def __init__(self):
        super(EpicStatsComponent, self).__init__()
        self._rank = 0
        self._frags = 0
        self._lane = 0
        self._hasRespawns = False

    def clear(self):
        self._rank = 0
        self._frags = 0
        self._lane = 0
        self._hasRespawns = True
        super(EpicStatsComponent, self).clear()

    def get(self, forced=False):
        stats = {'rank': self._rank,
         'frags': self._frags,
         'lane': self._lane,
         'hasRespawns': self._hasRespawns}
        data = super(EpicStatsComponent, self).get()
        data.update(stats)
        return data

    def addStats(self, vStatsVO):
        self._vehicleID = vStatsVO.vehicleID
        self._lane = vStatsVO.gameModeSpecific.getValue(EPIC_BATTLE_KEYS.PLAYER_GROUP)
        self._rank = vStatsVO.gameModeSpecific.getValue(EPIC_BATTLE_KEYS.RANK)
        self._hasRespawns = vStatsVO.gameModeSpecific.getValue(EPIC_BATTLE_KEYS.HAS_RESPAWNS)
        if self._rank is None:
            self._rank = 0
        if self._lane is None:
            self._lane = 0
        if self._hasRespawns is None:
            self._hasRespawns = True
        self._frags = vStatsVO.frags
        return


class EpicStatisticsDataController(EpicBattleStatisticDataControllerMeta):

    def startControl(self, battleCtx, arenaVisitor):
        super(EpicStatisticsDataController, self).startControl(battleCtx, arenaVisitor)
        componentSystem = self._arenaVisitor.getComponentSystem()
        playerComp = getattr(componentSystem, 'playerDataComponent', None)
        if playerComp is not None:
            playerComp.onPlayerPhysicalLaneUpdated += self.__onPlayerStatsUpdated
            playerComp.onPlayerRankUpdated += self.__onPlayerStatsUpdated
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onPlayerRespawnLivesUpdated += self.__onPlayerStatsUpdated
        return

    def stopControl(self):
        if not self._arenaVisitor:
            return
        else:
            componentSystem = self._arenaVisitor.getComponentSystem()
            playerComp = getattr(componentSystem, 'playerDataComponent', None)
            if playerComp is not None:
                playerComp.onPlayerPhysicalLaneUpdated -= self.__onPlayerStatsUpdated
                playerComp.onPlayerRankUpdated -= self.__onPlayerStatsUpdated
            ctrl = self.sessionProvider.dynamic.respawn
            if ctrl is not None:
                ctrl.onPlayerRespawnLivesUpdated -= self.__onPlayerStatsUpdated
            super(EpicStatisticsDataController, self).stopControl()
            return

    def invalidateArenaInfo(self):
        super(EpicStatisticsDataController, self).invalidateArenaInfo()
        self.__onPlayerStatsUpdated()

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        isEnemy = arenaDP.isEnemyTeam(vo.team)
        exchange = self._exchangeBroker.getVehicleStatusExchange(isEnemy)
        exchange.addVehicleInfo(vo)
        if not vo.isObserver():
            self._statsCollector.addVehicleStatusUpdate(vo)
        exchange.addTotalStats(self._statsCollector.getTotalStats(self._arenaVisitor, self.sessionProvider))
        data = exchange.get()
        if data:
            self.as_updateVehicleStatusS(data)

    def _populate(self):
        super(EpicStatisticsDataController, self)._populate()
        componentSystem = self._arenaVisitor.getComponentSystem()
        playerComp = getattr(componentSystem, 'playerDataComponent', None)
        playerComp.setPlayerLaneByPlayerGroups()
        return

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(vehicle.VehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(sortKey=vos_collections.EpicRankSortKey),), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(self.__getStatsComponentClass()(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(sortKey=vos_collections.EpicRankSortKey),), statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(vehicle.TeamsSortedIDsComposer(sortKey=vos_collections.EpicRankSortKey),), statsComposers=None))
        return exchangeBroker

    def _createExchangeCollector(self):
        return broker.NoCollectableStats()

    def __getStatsComponentClass(self):
        return EpicStatsComponent

    def __onPlayerStatsUpdated(self, *args):
        isAttacker = avatar_getter.getPlayerTeam() == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER
        componentSystem = self._arenaVisitor.getComponentSystem()
        playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
        if playerDataComp is None:
            _logger.error('Expected PlayerDataComponent not present!')
            return {}
        else:
            rank = 0
            if self._arenaVisitor.hasPlayerRanks():
                rank = playerDataComp.playerRank
            playerData = {'isAttacker': isAttacker,
             'lane': playerDataComp.physicalLane,
             'rank': rank}
            self.as_updateEpicPlayerStatsS(playerData)
            return

    def as_setFragsS(self, data):
        self.as_setEpicVehiclesStatsS(data)

    def as_updateVehiclesStatsS(self, data):
        self.as_updateEpicVehiclesStatsS(data)
