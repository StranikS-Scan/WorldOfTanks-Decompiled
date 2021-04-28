# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/weekend_brawl/stats_exchange.py
from gui.battle_control.arena_info.arena_vos import WeekendBrawlKeys
from gui.Scaleform.genConsts.WEEKEND_BRAWL_CONSTS import WEEKEND_BRAWL_CONSTS
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import DynamicVehicleStatsComponent
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import broker
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import createExchangeBroker
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import vehicle
from gui.Scaleform.daapi.view.meta.WBBattleStatisticDataControllerMeta import WBBattleStatisticDataControllerMeta

class WeekendBrawlVehicleStatsComponent(DynamicVehicleStatsComponent):
    __slots__ = ('_interestPointState',)

    def __init__(self):
        super(WeekendBrawlVehicleStatsComponent, self).__init__()
        self._interestPointState = WEEKEND_BRAWL_CONSTS.INTEREST_POINT_STATE_NONE

    def clear(self):
        self._interestPointState = WEEKEND_BRAWL_CONSTS.INTEREST_POINT_STATE_NONE
        super(WeekendBrawlVehicleStatsComponent, self).clear()

    def get(self, forced=False):
        data = super(WeekendBrawlVehicleStatsComponent, self).get(forced=True)
        data.update({'interestPointState': self._interestPointState})
        return data

    def addStats(self, vStatsVO):
        super(WeekendBrawlVehicleStatsComponent, self).addStats(vStatsVO)
        self._interestPointState = vStatsVO.gameModeSpecific.getValue(WeekendBrawlKeys.POINT_OF_INTEREST.value)


class WeekendBrawlStatisticsDataController(WBBattleStatisticDataControllerMeta):

    def startControl(self, ctx, arenaVisitor):
        super(WeekendBrawlStatisticsDataController, self).startControl(ctx, arenaVisitor)
        pointOfInterestCtrl = self.sessionProvider.dynamic.pointsOfInterest
        if pointOfInterestCtrl is not None:
            pointOfInterestCtrl.onArenaVehicleActivityUpdated += self.updateVehiclesStats
        return

    def stopControl(self):
        pointOfInterestCtrl = self.sessionProvider.dynamic.pointsOfInterest
        if pointOfInterestCtrl is not None:
            pointOfInterestCtrl.onArenaVehicleActivityUpdated -= self.updateVehiclesStats
        super(WeekendBrawlStatisticsDataController, self).stopControl()
        return

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(vehicle.VehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(), vehicle.TeamsCorrelationIDsComposer()), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(WeekendBrawlVehicleStatsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(vehicle.TeamsSortedIDsComposer(), vehicle.TeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker

    def as_setFragsS(self, data):
        self.as_setWBVehiclesStatsS(data)

    def as_updateVehiclesStatsS(self, data):
        self.as_updateWBVehiclesStatsS(data)
