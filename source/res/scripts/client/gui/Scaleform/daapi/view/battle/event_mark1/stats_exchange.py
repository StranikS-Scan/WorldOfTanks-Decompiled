# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_mark1/stats_exchange.py
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import VehicleFragsComponent
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import createExchangeBroker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import broker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import vehicle

class _Mark1VehicleInfoComponent(vehicle.VehicleInfoComponent):

    def addVehicleInfo(self, vInfoVO, overrides):
        if vInfoVO.vehicleType.isMark1:
            return self._data
        else:
            return super(_Mark1VehicleInfoComponent, self).addVehicleInfo(vInfoVO, overrides)


class Mark1EventStatisticsDataController(ClassicStatisticsDataController):

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(_Mark1VehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.Mark1EventTeamsSortedIDsComposer(), vehicle.Mark1EventTeamsCorrelationIDsComposer()), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(VehicleFragsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(vehicle.Mark1EventTeamsSortedIDsComposer(), vehicle.Mark1EventTeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker
