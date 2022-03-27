# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/unified_trade_in.py
import typing
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from items import UNDEFINED_ITEM_CD
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.shared import IItemsCache
from web.web_client_api import W2CSchema, w2c, Field
from web.web_client_api.shop import formatters
from web.web_client_api.shop.formatters import Field as FormatterField
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, List
    from web.web_client_api.shop.formatters import Formatter

class _SelectedVehicleSchema(W2CSchema):
    vehicleCompactDescriptor = Field(required=True, type=int)


class TradeInFormatter(object):

    def __init__(self, formatter, additionalFields):
        self._formatter = formatter
        self._additionalFields = additionalFields

    def format(self, item):
        if item is None:
            return
        else:
            data = self._formatter.format(item)
            data.update({field.name:field.getter(item) for field in self._additionalFields})
            return data


class TradeInShopVehicleStates(object):
    OK = 'OK'
    IN_BATTLE = 'IN_BATTLE'
    UNSUITABLE = 'UNSUITABLE'
    DAMAGED = 'DAMAGED'
    IN_TACTICAL_UNIT = 'IN_TACTICAL_UNIT'


class UnifiedTradeInWebApiMixin(object):
    _tradeIn = dependency.descriptor(ITradeInController)
    _itemsCache = dependency.descriptor(IItemsCache)
    CLIENT_TO_SHOP_VEHICLE_STATES = {Vehicle.VEHICLE_STATE.DAMAGED: TradeInShopVehicleStates.DAMAGED,
     Vehicle.VEHICLE_STATE.EXPLODED: TradeInShopVehicleStates.DAMAGED,
     Vehicle.VEHICLE_STATE.DESTROYED: TradeInShopVehicleStates.DAMAGED,
     Vehicle.VEHICLE_STATE.BATTLE: TradeInShopVehicleStates.IN_BATTLE,
     Vehicle.VEHICLE_STATE.IN_PREBATTLE: TradeInShopVehicleStates.IN_TACTICAL_UNIT,
     Vehicle.VEHICLE_STATE.LOCKED: TradeInShopVehicleStates.UNSUITABLE}

    def __init__(self):
        super(UnifiedTradeInWebApiMixin, self).__init__()
        self.buyVehicleFormatter = None
        self.sellVehicleFormatter = None
        return

    @w2c(W2CSchema, 'get_unified_trade_in_enabled')
    def getUnifiedTradeInEnabled(self, cmd):
        enabled = bool(self._tradeIn.isEnabled() and self._tradeIn.hasAvailableOffer())
        return {'isEnabled': enabled}

    @w2c(W2CSchema, 'get_unified_trade_in_info')
    def getUnifiedTradeInInfo(self, cmd):
        fmtSell = self._getSellVehicleFormatter()
        fmtBuy = self._getBuyVehicleFormatter()
        vehiclesToBuy = [ fmtBuy.format(vehicle) for vehicle in self._tradeIn.getVehiclesToBuy(True).itervalues() ]
        if vehiclesToBuy:
            vehiclesToSell = [ fmtSell.format(vehicle) for vehicle in self._tradeIn.getVehiclesToSell(True).itervalues() ]
        else:
            vehiclesToSell = list()
        return {'expirationDate': self._tradeIn.getExpirationTime(),
         'selectedVehicleToSell': fmtSell.format(self._tradeIn.getSelectedVehicleToSell()),
         'selectedVehicleToBuy': fmtBuy.format(self._tradeIn.getSelectedVehicleToBuy()),
         'vehiclesToSell': vehiclesToSell,
         'vehiclesToBuy': vehiclesToBuy}

    @w2c(_SelectedVehicleSchema, 'set_unified_trade_in_vehicle_to_sell')
    def setUnifiedTradeInVehicleToSell(self, cmd):
        if not cmd.vehicleCompactDescriptor or cmd.vehicleCompactDescriptor == -1:
            vehicleCD = UNDEFINED_ITEM_CD
        else:
            vehicleCD = cmd.vehicleCompactDescriptor
        self._tradeIn.selectVehicleToSell(vehicleCD)

    @w2c(_SelectedVehicleSchema, 'set_unified_trade_in_vehicle_to_buy')
    def setUnifiedTradeInVehicleToBuy(self, cmd):
        if not cmd.vehicleCompactDescriptor or cmd.vehicleCompactDescriptor == -1:
            vehicleCD = UNDEFINED_ITEM_CD
        else:
            vehicleCD = cmd.vehicleCompactDescriptor
        self._tradeIn.selectVehicleToBuy(vehicleCD)

    @w2c(W2CSchema, 'execute_unified_trade_in')
    def executeUnifiedTradeIn(self, cmd):
        shared_events.showVehicleBuyDialog(self._tradeIn.getSelectedVehicleToBuy(), previousAlias=VIEW_ALIAS.LOBBY_STORE, returnAlias=VIEW_ALIAS.LOBBY_STORE, returnCallback=shared_events.showHangar)

    def _getBuyVehicleFormatter(self):
        if self.buyVehicleFormatter is None:
            self.buyVehicleFormatter = TradeInFormatter(formatters.makeVehicleFormatter(True), [FormatterField('tradeOffPrice', lambda i: i.tradeInBuyPrice.toDict() or None), FormatterField('discountPercentage', lambda i: i.discountPercentage)])
        return self.buyVehicleFormatter

    def _getSellVehicleFormatter(self):

        def formatState(vehicle):
            isReady = vehicle.isReadyToFight
            if isReady:
                return TradeInShopVehicleStates.OK
            reason, _ = vehicle.getState()
            return self.CLIENT_TO_SHOP_VEHICLE_STATES.get(reason, TradeInShopVehicleStates.OK)

        if self.sellVehicleFormatter is None:
            self.sellVehicleFormatter = TradeInFormatter(formatters.makeVehicleFormatter(True), [FormatterField('isFreeExchange', lambda i: i.isFreeExchange), FormatterField('state', formatState)])
        return self.sellVehicleFormatter
