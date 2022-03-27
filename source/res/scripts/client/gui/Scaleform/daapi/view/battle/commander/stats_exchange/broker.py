# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/stats_exchange/broker.py
import weakref
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import DynamicVehicleStatsComponent
from gui.Scaleform.daapi.view.battle.commander.stats_exchange import supply
from gui.Scaleform.daapi.view.battle.commander.stats_exchange.commander_info import RTSCommanderInfoComposer
from gui.Scaleform.daapi.view.battle.commander.stats_exchange.commander_data import RTSCommanderDataExchangeBlock, RTSCommanderDataComponent
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import broker, player, vehicle
from gui.battle_control.controllers.commander.vos_collections import RTSVehicleInfoSortKey

class RTSExchangeBroker(broker.ExchangeBroker):

    def __init__(self, ctx):
        super(RTSExchangeBroker, self).__init__(ctx)
        self._rtsCommanderInfo = broker.NoExchangeBlock()
        self._rtsCommanderData = broker.NoExchangeBlock()
        self._rtsSupply = broker.NoExchangeBlock()

    def destroy(self):
        if self._rtsCommanderInfo is not None:
            self._rtsCommanderInfo.destroy()
            self._rtsCommanderInfo = None
        if self._rtsCommanderData is not None:
            self._rtsCommanderData.destroy()
            self._rtsCommanderData = None
        if self._rtsSupply is not None:
            self._rtsSupply.destroy()
            self._rtsSupply = None
        super(RTSExchangeBroker, self).destroy()
        return

    def getExchangeCtx(self):
        return self._ctx

    def getRTSCommanderInfoExchange(self):
        self._rtsCommanderInfo.clear()
        return self._rtsCommanderInfo

    def getRTSCommanderDataExchange(self):
        self._rtsCommanderData.clear()
        return self._rtsCommanderData

    def getRTSSupplyExchange(self):
        self._rtsSupply.clear()
        return self._rtsSupply

    def setRTSCommanderInfoExchange(self, exchange):
        self._rtsCommanderInfo = exchange
        self._rtsCommanderInfo.setCtx(weakref.proxy(self._ctx))

    def setRTSCommanderDataExchange(self, exchange):
        self._rtsCommanderData = exchange
        self._rtsCommanderData.setCtx(weakref.proxy(self._ctx))

    def setRTSSupplyExchange(self, exchange):
        self._rtsSupply = exchange


class RTSExchangeBlock(broker.ExchangeBlock):

    def addSortIDs(self, arenaDP, *flags):
        pass

    def addTotalStats(self, stats):
        pass


def createExchangeBroker(exchangeCtx):
    proxy = weakref.proxy(exchangeCtx)
    exchangeBroker = RTSExchangeBroker(exchangeCtx)
    exchangeBroker.setPlayerStatusExchange(player.PlayerStatusComponent())
    exchangeBroker.setUsersTagsExchange(player.UsersTagsListExchangeData(proxy))
    exchangeBroker.setInvitationsExchange(player.InvitationsExchangeBlock())
    exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(vehicle.VehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(RTSVehicleInfoSortKey), vehicle.TeamsCorrelationIDsComposer()), statsComposers=None))
    exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(DynamicVehicleStatsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
    exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(vehicle.TeamsSortedIDsComposer(RTSVehicleInfoSortKey), vehicle.TeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
    exchangeBroker.setRTSCommanderInfoExchange(RTSExchangeBlock(vehicle.VehicleInfoComponent(), composer=broker.BiDirectionComposer(left=RTSCommanderInfoComposer(voField='leftCommanderInfo'), right=RTSCommanderInfoComposer(voField='rightCommanderInfo'))))
    exchangeBroker.setRTSCommanderDataExchange(RTSCommanderDataExchangeBlock(RTSCommanderDataComponent(), composer=broker.BiDirectionComposer()))
    exchangeBroker.setRTSSupplyExchange(supply.SupplyExchangeBlock())
    return exchangeBroker
