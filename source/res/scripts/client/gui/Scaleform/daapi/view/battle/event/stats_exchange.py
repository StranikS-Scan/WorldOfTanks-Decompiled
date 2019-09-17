# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/stats_exchange.py
import BigWorld
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import VehicleFragsComponent
from gui.Scaleform.daapi.view.meta.FestRaceBattleStatisticDataControllerMeta import FestRaceBattleStatisticDataControllerMeta
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import createExchangeBroker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import broker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import vehicle
from gui.battle_control.arena_info.arena_vos import EVENT_FESTIVAL_RACE_KEYS
from gui.battle_control.arena_info import vos_collections

class EventVehicleInfoComponent(vehicle.VehicleInfoComponent):

    def addVehicleInfo(self, vInfoVO, overrides):
        super(EventVehicleInfoComponent, self).addVehicleInfo(vInfoVO, overrides)
        vehIconName = vInfoVO.vehicleType.iconName
        self._data['loadingVehicleIcon'] = vehIconName.split('-', 1)[-1]


class VehicleRaceComponent(VehicleFragsComponent):
    __slots__ = ('_racePosition', '_raceFinishTime')

    def __init__(self):
        super(VehicleRaceComponent, self).__init__()
        self._racePosition = 0
        self._raceFinishTime = 0.0

    def clear(self):
        self._racePosition = 0
        super(VehicleRaceComponent, self).clear()

    def get(self, forced=False):
        if forced or self._racePosition:
            data = super(VehicleRaceComponent, self).get(forced=True)
            data['racePosition'] = self._racePosition
            data['raceFinishTime'] = self._raceFinishTime
            return data
        return {}

    def addStats(self, vStatsVO):
        super(VehicleRaceComponent, self).addStats(vStatsVO)
        self._racePosition = vStatsVO.gameModeSpecific.getValue(EVENT_FESTIVAL_RACE_KEYS.PLAYER_RACE_POSITION)
        self._raceFinishTime = vStatsVO.gameModeSpecific.getValue(EVENT_FESTIVAL_RACE_KEYS.PLAYER_RACE_FINISH_TIME)


class EventStatisticsDataController(FestRaceBattleStatisticDataControllerMeta):
    RACE_LIST_COOL_DOWN = 2.0

    def __init__(self):
        super(EventStatisticsDataController, self).__init__()
        self.__raceListCooldownEnabled = False
        self.__raceListInvalidated = False
        self.__raceListData = None
        return

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(EventVehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(), vehicle.TeamsCorrelationIDsComposer()), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(VehicleRaceComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(vehicle.TeamsSortedIDsComposer(), vehicle.TeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
        self.__additionalExchange = vehicle.VehiclesExchangeBlock(EventVehicleInfoComponent(), positionComposer=broker.SingleSideComposer(), idsComposers=(vehicle.VehiclesSortedIDsComposer(sortKey=vos_collections.RacePositionSortKey),), statsComposers=None)
        return exchangeBroker

    def invalidateArenaInfo(self):
        super(EventStatisticsDataController, self).invalidateArenaInfo()
        BigWorld.player().arena.arenaInfo.updateRaceListStats()
        BigWorld.player().arena.arenaInfo.updateRaceFinishTimeStats()

    def updateVehiclesStats(self, updated, arenaDP):
        super(EventStatisticsDataController, self).updateVehiclesStats(updated, arenaDP)
        exchange = self.__additionalExchange
        exchange.addSortIDs(arenaDP, True)
        self.__raceListData = exchange.get(forced=True)
        if not self.__raceListData:
            return
        if not self.__raceListCooldownEnabled:
            self.as_setSingleSideVehiclesInfoS(self.__raceListData)
            self.__raceListCooldownEnabled = True
            BigWorld.callback(self.RACE_LIST_COOL_DOWN, self.__onCooldownExpired)
        else:
            self.__raceListInvalidated = True

    def as_updateVehiclesStatsS(self, data):
        self.as_updateFestRaceVehiclesStatsS(data)

    def __onCooldownExpired(self):
        if self.__raceListInvalidated:
            self.__raceListInvalidated = False
            self.as_setSingleSideVehiclesInfoS(self.__raceListData)
            BigWorld.callback(self.RACE_LIST_COOL_DOWN, self.__onCooldownExpired)
        else:
            self.__raceListCooldownEnabled = False
