# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/stats_exchange.py
from __future__ import absolute_import
from past.builtins import cmp
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController, DynamicVehicleStatsComponent
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import broker, vehicle, createExchangeBroker
from gui.battle_control.arena_info.vos_collections import VehicleInfoSortKey
from gui.shared.gui_items.Vehicle import VEHICLE_BATTLE_TYPES_ORDER_INDICES
from gui.shared.utils import toUpper

class HWSortKey(VehicleInfoSortKey):
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


class HWEnemySortedIDsComposer(vehicle.EnemySortedIDsComposer):
    __slots__ = ()

    def addSortIDs(self, isEnemy, arenaDP):
        pass


class HWEnemySingleSideComposer(broker.SingleSideComposer):
    __slots__ = ()

    def compose(self, data):
        return data

    def addItem(self, _, data):
        pass


class HWTeamsSortedIDsComposer(vehicle.TeamsSortedIDsComposer):
    __slots__ = ()

    def __init__(self, sortKey=VehicleInfoSortKey):
        super(HWTeamsSortedIDsComposer, self).__init__(sortKey)
        self._right = HWEnemySortedIDsComposer()


class HWTeamsCorrelationIDsComposer(vehicle.TeamsCorrelationIDsComposer):
    __slots__ = ()

    def __init__(self):
        super(HWTeamsCorrelationIDsComposer, self).__init__()
        self._right = HWEnemySortedIDsComposer()


class HWBiDirectionComposer(broker.BiDirectionComposer):
    __slots__ = ()

    def __init__(self):
        super(HWBiDirectionComposer, self).__init__()
        self._right = HWEnemySingleSideComposer()


class HWStatisticsDataController(ClassicStatisticsDataController):

    def __init__(self):
        super(HWStatisticsDataController, self).__init__()
        self.__poiStatsController = None
        self.__arenaInfoComponent = None
        return

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(vehicle.VehicleInfoComponent(), positionComposer=HWBiDirectionComposer(), idsComposers=(HWTeamsSortedIDsComposer(sortKey=HWSortKey), HWTeamsCorrelationIDsComposer()), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(DynamicVehicleStatsComponent(), positionComposer=HWBiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(HWTeamsSortedIDsComposer(), HWTeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker
