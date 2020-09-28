# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/stats_exchange.py
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController, DynamicVehicleStatsComponent
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import broker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import createExchangeBroker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import vehicle
from gui.battle_control.arena_info.settings import VEHICLE_STATUS
from gui.shared.gui_items.Vehicle import VEHICLE_EVENT_TYPE
from gui.Scaleform.genConsts.EVENT_CONSTS import EVENT_CONSTS
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class EventVehicleInfoComponent(vehicle.VehicleInfoComponent):

    def addVehicleInfo(self, vInfoVO, overrides):
        if not {'event_boss', 'event_hunter'} & vInfoVO.vehicleType.tags:
            return None
        else:
            super(EventVehicleInfoComponent, self).addVehicleInfo(vInfoVO, overrides)
            isBoss = VEHICLE_EVENT_TYPE.EVENT_BOSS in vInfoVO.vehicleType.tags
            isSpecialBoss = VEHICLE_EVENT_TYPE.EVENT_SPECIAL_BOSS in vInfoVO.vehicleType.tags
            vehicleIcon = EVENT_CONSTS.STATS_ICON_HUNTER
            if isBoss:
                if isSpecialBoss:
                    vehicleIcon = EVENT_CONSTS.STATS_ICON_BOSS_SPECIAL
                else:
                    vehicleIcon = EVENT_CONSTS.STATS_ICON_BOSS
            return self._data.update({'vehicleType': EVENT_CONSTS.VEHICLE_TYPE_BOSS if isBoss else EVENT_CONSTS.VEHICLE_TYPE_HUNTER,
             'vehicleLevel': 0,
             'vehicleIconName': vehicleIcon})


class EventVehicleStatusComponent(vehicle.VehicleStatusComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def addVehicleInfo(self, vInfoVO):
        if not {VEHICLE_EVENT_TYPE.EVENT_BOSS, VEHICLE_EVENT_TYPE.EVENT_HUNTER} & vInfoVO.vehicleType.tags:
            return
        else:
            super(EventVehicleStatusComponent, self).addVehicleInfo(vInfoVO)
            if VEHICLE_EVENT_TYPE.EVENT_HUNTER in vInfoVO.vehicleType.tags:
                respawn = self.__sessionProvider.dynamic.respawn
                if respawn is not None and respawn.teammatesLives.get(vInfoVO.vehicleID, 0) > 0:
                    self._status |= VEHICLE_STATUS.IS_ALIVE
            return


class EventStatisticsDataController(ClassicStatisticsDataController):

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(EventVehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(), vehicle.TeamsCorrelationIDsComposer()), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(DynamicVehicleStatsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(EventVehicleStatusComponent(idsComposers=(vehicle.TeamsSortedIDsComposer(), vehicle.TeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker
