# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/stats_exchange.py
import logging
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import DynamicVehicleStatsComponent
from gui.Scaleform.daapi.view.battle.shared.stats_exchange.vehicle import BiSortedIDsComposer, VehiclesSortedIDsComposer
from gui.Scaleform.daapi.view.meta.EpicBattleStatisticDataControllerMeta import EpicBattleStatisticDataControllerMeta
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import createExchangeBroker
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import broker
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import vehicle
from gui.battle_control.arena_info import vos_collections
from epic_constants import EPIC_BATTLE_TEAM_ID
from gui.battle_control.arena_info.arena_vos import EPIC_BATTLE_KEYS
from gui.battle_control import avatar_getter
from supply_shared import Supply
_logger = logging.getLogger(__name__)

class EpicTeamsSortedIDsComposer(BiSortedIDsComposer):
    __slots__ = ()

    def __init__(self, sortKey=vos_collections.VehicleInfoSortKey):
        super(EpicTeamsSortedIDsComposer, self).__init__(left=EpicAllySortedIDsComposer(voField='leftItemsIDs', sortKey=sortKey), right=EpicEnemySortedIDsComposer(voField='rightItemsIDs', sortKey=sortKey))


class EpicVehicleInfoComponent(vehicle.VehicleInfoComponent):
    __slots__ = ()

    def addVehicleInfo(self, vInfoVO, overrides):
        return self._data if Supply.isSupply(vInfoVO.vehicleType.tags) else super(EpicVehicleInfoComponent, self).addVehicleInfo(vInfoVO, overrides)


class EpicVehiclesSortedIDsComposer(VehiclesSortedIDsComposer):
    __slots__ = ()

    def filterIDs(self, arenaDP):
        super(EpicVehiclesSortedIDsComposer, self).filterIDs(arenaDP)
        self.removeSupplyIDs(arenaDP)

    def removeSupplyIDs(self, arenaDP):
        self._items = [ vID for vID in self._items if not Supply.isSupply(arenaDP.getVehicleInfo(vID).vehicleType.tags) ]


class EpicAllySortedIDsComposer(EpicVehiclesSortedIDsComposer):
    __slots__ = ()

    def __init__(self, voField='vehiclesIDs', sortKey=vos_collections.VehicleInfoSortKey):
        super(EpicAllySortedIDsComposer, self).__init__(voField, sortKey)
        self._collectionClass = vos_collections.AllyItemsCollection

    def addSortIDs(self, isEnemy, arenaDP):
        super(EpicAllySortedIDsComposer, self).addSortIDs(isEnemy, arenaDP)


class EpicEnemySortedIDsComposer(EpicVehiclesSortedIDsComposer):
    __slots__ = ()

    def __init__(self, voField='vehiclesIDs', sortKey=vos_collections.VehicleInfoSortKey):
        super(EpicEnemySortedIDsComposer, self).__init__(voField, sortKey)
        self._collectionClass = vos_collections.EnemyItemsCollection

    def addSortIDs(self, isEnemy, arenaDP):
        super(EpicEnemySortedIDsComposer, self).addSortIDs(isEnemy, arenaDP)


class EpicStatsComponent(DynamicVehicleStatsComponent):
    __slots__ = ('_rank', '_lane', '_hasRespawns')

    def __init__(self):
        super(EpicStatsComponent, self).__init__()
        self._rank = 0
        self._lane = 0
        self._hasRespawns = False

    def clear(self):
        self._rank = 0
        self._lane = 0
        self._hasRespawns = True
        super(EpicStatsComponent, self).clear()

    def get(self, forced=False):
        stats = {'rank': self._rank,
         'lane': self._lane,
         'hasRespawns': self._hasRespawns}
        data = super(EpicStatsComponent, self).get(forced=True)
        data.update(stats)
        return data

    def addStats(self, vStatsVO):
        super(EpicStatsComponent, self).addStats(vStatsVO)
        self._lane = vStatsVO.gameModeSpecific.getValue(EPIC_BATTLE_KEYS.PLAYER_GROUP)
        self._rank = vStatsVO.gameModeSpecific.getValue(EPIC_BATTLE_KEYS.RANK)
        self._hasRespawns = vStatsVO.gameModeSpecific.getValue(EPIC_BATTLE_KEYS.HAS_RESPAWNS)
        if self._rank is None:
            self._rank = 0
        if self._lane is None:
            self._lane = 0
        if self._hasRespawns is None:
            self._hasRespawns = True
        return


class EpicStatisticsDataController(EpicBattleStatisticDataControllerMeta):

    def startControl(self, ctx, arenaVisitor):
        super(EpicStatisticsDataController, self).startControl(ctx, arenaVisitor)
        componentSystem = self._arenaVisitor.getComponentSystem()
        playerComp = getattr(componentSystem, 'playerDataComponent', None)
        if playerComp is not None:
            playerComp.onPlayerPhysicalLaneUpdated += self.__onPlayerStatsUpdated
            playerComp.onPlayerRankUpdated += self.__onPlayerStatsUpdated
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onPlayerRespawnLivesUpdated += self.__onPlayerStatsUpdated
        specCtrl = self.sessionProvider.dynamic.spectator
        if specCtrl is not None:
            specCtrl.onSpectatedVehicleChanged += self.__onSpectatedVehicleChanged
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
            specCtrl = self.sessionProvider.dynamic.spectator
            if specCtrl is not None:
                specCtrl.onSpectatedVehicleChanged -= self.__onSpectatedVehicleChanged
            super(EpicStatisticsDataController, self).stopControl()
            return

    def invalidateArenaInfo(self):
        super(EpicStatisticsDataController, self).invalidateArenaInfo()
        self.__onPlayerStatsUpdated()

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        isEnemy = arenaDP.isEnemyTeam(vo.team)
        exchange = self._exchangeBroker.getVehicleStatusExchange(isEnemy)
        exchange.addVehicleInfo(vo)
        if not self._shouldSkipVehicleInfo(vo):
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
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(EpicVehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(EpicTeamsSortedIDsComposer(sortKey=vos_collections.EpicRankSortKey),), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(EpicStatsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(EpicTeamsSortedIDsComposer(sortKey=vos_collections.EpicRankSortKey),), statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(EpicTeamsSortedIDsComposer(sortKey=vos_collections.EpicRankSortKey),), statsComposers=None))
        return exchangeBroker

    def _createExchangeCollector(self):
        return broker.NoCollectableStats()

    def _shouldSkipVehicleInfo(self, vInfoVO):
        isSupply = Supply.isSupply(vInfoVO.vehicleType.tags)
        return isSupply or super(EpicStatisticsDataController, self)._shouldSkipVehicleInfo(vInfoVO)

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

    def __onSpectatedVehicleChanged(self, vehicleID):
        if vehicleID is None:
            arenaDP = self._battleCtx.getArenaDP()
            previousID = self._personalInfo.changeSelected(-1)
            self.invalidatePlayerStatus(0, arenaDP.getVehicleInfo(previousID), arenaDP)
        return

    def as_setFragsS(self, data):
        self.as_setEpicVehiclesStatsS(data)

    def as_updateVehiclesStatsS(self, data):
        self.as_updateEpicVehiclesStatsS(data)
