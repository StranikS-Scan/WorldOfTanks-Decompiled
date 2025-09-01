# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/stats_exchange.py
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController, DynamicVehicleStatsComponent
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import broker, vehicle, createExchangeBroker
from gui.battle_control.arena_info.vos_collections import VehicleInfoSortKey
from gui.shared.gui_items.Vehicle import VEHICLE_BATTLE_TYPES_ORDER_INDICES
from gui.shared.utils import toUpper

class LSSortKey(VehicleInfoSortKey):
    __slots__ = ()

    def _cmp(self, other):
        xvInfoVO = self.vInfoVO
        yvInfoVO = other.vInfoVO
        result = cmp(xvInfoVO.team, yvInfoVO.team)
        if result:
            return result
        result = cmp(yvInfoVO.isAlive(), xvInfoVO.isAlive())
        if result:
            return result
        result = cmp(VEHICLE_BATTLE_TYPES_ORDER_INDICES[xvInfoVO.vehicleType.classTag], VEHICLE_BATTLE_TYPES_ORDER_INDICES[yvInfoVO.vehicleType.classTag])
        if result:
            return result
        result = cmp(toUpper(xvInfoVO.vehicleType.guiName), toUpper(yvInfoVO.vehicleType.guiName))
        return result if result else cmp(toUpper(xvInfoVO.player.name), toUpper(yvInfoVO.player.name))


class LSEnemySortedIDsComposer(vehicle.EnemySortedIDsComposer):
    __slots__ = ()

    def addSortIDs(self, isEnemy, arenaDP):
        pass


class LSEnemySingleSideComposer(broker.SingleSideComposer):
    __slots__ = ()

    def compose(self, data):
        return data

    def addItem(self, _, data):
        pass


class LSTeamsSortedIDsComposer(vehicle.TeamsSortedIDsComposer):
    __slots__ = ('_right',)

    def __init__(self, sortKey=VehicleInfoSortKey):
        super(LSTeamsSortedIDsComposer, self).__init__(sortKey)
        self._right = LSEnemySortedIDsComposer()


class LSTeamsCorrelationIDsComposer(vehicle.TeamsCorrelationIDsComposer):
    __slots__ = ('_right',)

    def __init__(self):
        super(LSTeamsCorrelationIDsComposer, self).__init__()
        self._right = LSEnemySortedIDsComposer()


class LSBiDirectionComposer(broker.BiDirectionComposer):
    __slots__ = ('_right',)

    def __init__(self):
        super(LSBiDirectionComposer, self).__init__()
        self._right = LSEnemySingleSideComposer()


class LSStatisticsDataController(ClassicStatisticsDataController):

    def __init__(self):
        super(LSStatisticsDataController, self).__init__()
        self.__poiStatsController = None
        self.__arenaInfoComponent = None
        return

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(vehicle.VehicleInfoComponent(), positionComposer=LSBiDirectionComposer(), idsComposers=(LSTeamsSortedIDsComposer(sortKey=LSSortKey), LSTeamsCorrelationIDsComposer()), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(DynamicVehicleStatsComponent(), positionComposer=LSBiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(LSTeamsSortedIDsComposer(), LSTeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker
