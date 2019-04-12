# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/ranked/stats_exchange.py
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController, VehicleFragsComponent
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import broker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import createExchangeBroker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import vehicle
from gui.battle_control.arena_info import vos_collections
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedVehicleInfoComponent(vehicle.VehicleInfoComponent):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def addVehicleInfo(self, vInfoVO, overrides):
        super(RankedVehicleInfoComponent, self).addVehicleInfo(vInfoVO, overrides)
        rankID = vInfoVO.ranked.rank
        division = self.__rankedController.getDivision(rankID)
        division.getRankIdInDivision(rankID)
        return self._data.update({'rankLevel': division.getRankIdInDivision(rankID),
         'division': division.getID()})


class RankedStatisticsDataController(ClassicStatisticsDataController):

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(RankedVehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(sortKey=vos_collections.RankSortKey), vehicle.TeamsCorrelationIDsComposer()), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(VehicleFragsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(vehicle.TeamsSortedIDsComposer(sortKey=vos_collections.RankSortKey), vehicle.TeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker
