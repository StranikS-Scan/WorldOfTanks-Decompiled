# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/personal_trade_in.py
import logging
import math
from Event import Event
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Money, MONEY_ZERO_GOLD
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import UNDEFINED_ITEM_CD
from skeletons.gui.game_control import IPersonalTradeInController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_EVENT_STATE_NAME = 'PersonalTradeIn'
_EVENT_STATE_IN_PROGRESS = 'In_Progress'
_EVENT_STATE_END = 'End'

class PersonalTradeInController(IPersonalTradeInController):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(PersonalTradeInController, self).__init__()
        self.__activeTradeInSaleCD = UNDEFINED_ITEM_CD
        self.__activeTradeInBuyCD = UNDEFINED_ITEM_CD
        self.onActiveSaleVehicleChanged = Event()
        self.onActiveBuyVehicleChanged = Event()

    def onDisconnected(self):
        self.__activeTradeInSaleCD = UNDEFINED_ITEM_CD
        self.__activeTradeInBuyCD = UNDEFINED_ITEM_CD

    def getActiveTradeInSaleVehicleCD(self):
        return self.__activeTradeInSaleCD

    def getActiveTradeInSaleVehicle(self):
        return self.__itemsCache.items.getItemByCD(self.__activeTradeInSaleCD)

    def getActiveTradeInBuyVehicle(self):
        return self.__itemsCache.items.getItemByCD(self.__activeTradeInBuyCD)

    def getActiveTradeInBuyVehicleCD(self):
        return self.__activeTradeInBuyCD

    def setActiveTradeInSaleVehicleCD(self, value):
        intCD = int(value)
        if self.__canSetActiveTradeInSaleVehicle(intCD):
            if self.__activeTradeInSaleCD != intCD:
                self.__activeTradeInSaleCD = intCD
                self.onActiveSaleVehicleChanged()
        else:
            _logger.error('%s, can not be set as active trade-in vehicle for sale compact descriptor', intCD)

    def setActiveTradeInBuyVehicleCD(self, value):
        intCD = int(value)
        if self.__canSetActiveTradeInBuyVehicle(intCD):
            self.__activeTradeInBuyCD = intCD
            self.onActiveBuyVehicleChanged()
        else:
            _logger.error('%s, can not be set as active trade-in vehicle for buy compact descriptor', intCD)

    def getSaleVehicleCDs(self):
        return [ vehCD for vehCD in self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.CAN_PERSONAL_TRADE_IN_SALE) ]

    def getBuyVehicleCDs(self):
        return [ vehCD for vehCD in self.__itemsCache.items.getVehicles(~REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.CAN_PERSONAL_TRADE_IN_BUY) ]

    def getPersonalTradeInPrice(self, veh):
        price = veh.buyPrices.itemPrice.price
        defPrice = veh.buyPrices.itemPrice.defPrice
        if veh.canPersonalTradeInBuy and self.__activeTradeInSaleCD != UNDEFINED_ITEM_CD:
            isFreeExchange, salePrice = self.__getSalePrice(veh)
            if isFreeExchange:
                price = MONEY_ZERO_GOLD
            else:
                price = defPrice - salePrice
            if price.gold < 0:
                price = MONEY_ZERO_GOLD
        return ItemPrice(price, defPrice)

    def __getSalePrice(self, veh):
        buyGroupIDs = veh.groupIDs
        saleGroupIDs = self.getActiveTradeInSaleVehicle().groupIDs
        conversionRuleIter = self.__itemsCache.items.shop.personalTradeIn['conversionRules'].iteritems()
        isFreeExchange = False
        for (saleGroup, buyGroup), (isFreeExchange, priceFactor) in conversionRuleIter:
            if saleGroup in saleGroupIDs and buyGroup in buyGroupIDs:
                salePriceFactor = priceFactor
                if isFreeExchange:
                    salePriceFactor = 1
                break

        return (isFreeExchange, Money(gold=int(math.ceil(salePriceFactor * self.getActiveTradeInSaleVehicle().buyPrices.itemPrice.defPrice.gold))))

    def __canSetActiveTradeInSaleVehicle(self, newTradeInSaleCD):
        return newTradeInSaleCD == UNDEFINED_ITEM_CD or newTradeInSaleCD in self.getSaleVehicleCDs()

    def __canSetActiveTradeInBuyVehicle(self, newTradeInBuyCD):
        return newTradeInBuyCD == UNDEFINED_ITEM_CD or newTradeInBuyCD in self.getBuyVehicleCDs()
