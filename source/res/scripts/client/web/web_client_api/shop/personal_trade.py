# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/personal_trade.py
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import UNDEFINED_ITEM_CD
from skeletons.gui.game_control import IPersonalTradeInController
from skeletons.gui.shared import IItemsCache
from web.web_client_api import W2CSchema, w2c, Field
from gui.shared import event_dispatcher as shared_events
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

class _SetTradeInSelectedSchema(W2CSchema):
    id = Field(required=False, type=int)


class PersonalTradeWebApiMixin(object):
    _personalTradeInController = dependency.descriptor(IPersonalTradeInController)
    __itemsCache = dependency.descriptor(IItemsCache)

    @w2c(W2CSchema, 'get_personal_trade_in_info')
    def getPersonalTradeInInfo(self, _):
        return {'saleVehicles': self._getSaleVehicleCDsWithInformation(),
         'buyVehicles': self._getBuyVehicleCDs()}

    @w2c(_SetTradeInSelectedSchema, 'set_personal_trade_in_sale_selected')
    def setPersonalTradeInVehicleCDForSale(self, cmd):
        self._personalTradeInController.setActiveTradeInSaleVehicleCD(cmd.id)

    @w2c(W2CSchema, 'get_personal_trade_in_sale_selected')
    def getPersonalTradeInVehicleCDForSale(self, _):
        return {'id': self._personalTradeInController.getActiveTradeInSaleVehicleCD()}

    @w2c(_SetTradeInSelectedSchema, 'set_personal_trade_in_buy_selected')
    def setPersonalTradeInVehicleCDForBuy(self, cmd):
        self._personalTradeInController.setActiveTradeInBuyVehicleCD(cmd.id)

    @w2c(W2CSchema, 'get_personal_trade_in_buy_selected')
    def getPersonalTradeInVehicleCDForBuy(self, _):
        return {'id': self._personalTradeInController.getActiveTradeInBuyVehicleCD()}

    @w2c(W2CSchema, 'show_buy_vehicle_view')
    def showBuyVehicleView(self, _):
        if self._personalTradeInController.getActiveTradeInSaleVehicleCD() != UNDEFINED_ITEM_CD and self._personalTradeInController.getActiveTradeInBuyVehicleCD() != UNDEFINED_ITEM_CD:
            shared_events.showVehicleBuyDialog(self._personalTradeInController.getActiveTradeInBuyVehicle(), previousAlias=VIEW_ALIAS.LOBBY_STORE, returnAlias=VIEW_ALIAS.LOBBY_STORE, returnCallback=shared_events.showHangar)

    def _getSaleVehicleCDsWithInformation(self):
        saleVehicleCDsWithInformation = []
        criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.CAN_PERSONAL_TRADE_IN_SALE
        for vehCD, veh in self.__itemsCache.items.getVehicles(criteria).iteritems():
            conversionRuleIter = self.__itemsCache.items.shop.personalTradeIn['conversionRules'].iteritems()
            for (saleGroup, _), (isFreeExchange, priceFactor) in conversionRuleIter:
                if saleGroup in veh.groupIDs:
                    saleVehicleCDsWithInformation.append({'id': vehCD,
                     'isFreeExchange': isFreeExchange,
                     'priceFactor': priceFactor})
                    break

        return saleVehicleCDsWithInformation

    def _getBuyVehicleCDs(self):
        return [ {'id': vehCD} for vehCD in self.__itemsCache.items.getVehicles(~REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.CAN_PERSONAL_TRADE_IN_BUY) ]
