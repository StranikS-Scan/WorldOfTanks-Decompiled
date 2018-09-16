# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/ConfirmBoosterMeta.py
import math
from Event import EventManager, Event
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.framework import ScopeTemplates
from gui.shared import events
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.shared.money import Money, Currency, CurrencyCollection
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
MAX_BOOSTERS_FOR_OPERATION = 1000000

class BuyBoosterMeta(I18nConfirmDialogMeta):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, boosterID, balance):
        super(BuyBoosterMeta, self).__init__('buyConfirmation', scope=ScopeTemplates.LOBBY_SUB_SCOPE)
        self.__booster = self.goodiesCache.getBooster(boosterID)
        self.__balance = balance
        self._eManager = EventManager()
        self.onInvalidate = Event(self._eManager)
        g_clientUpdateManager.addCallbacks({'stats': self.__onStatsChanged})
        self.__boosterBuyPricesSum = self.__booster.buyPrices.getSum()

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_CONFIRM_BOOSTER

    def getBoosterID(self):
        return self.__booster.boosterID

    def getBooster(self):
        return self.__booster

    def destroy(self):
        self.__booster = None
        self.__balance = None
        self._eManager.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

    def getMaxAvailableItemsCount(self):
        buyPrice = self.__boosterBuyPricesSum.price
        return CurrencyCollection(*(self.__getMaxCount(buyPrice, currency) for currency in Currency.ALL))

    def getActionVO(self):
        return packActionTooltipData(ACTION_TOOLTIPS_TYPE.BOOSTER, str(self.__booster.boosterID), True, self.__boosterBuyPricesSum.price, self.__boosterBuyPricesSum.defPrice) if self.__boosterBuyPricesSum.isActionPrice() else None

    def getCurrency(self):
        return self.__booster.getBuyPrice(preferred=True).getCurrency(byWeight=True)

    def getPrices(self):
        return self.__booster.buyPrices

    def submit(self, count, currency):
        ActionsFactory.doAction(ActionsFactory.BUY_BOOSTER, self.__booster, count, currency)

    def __onStatsChanged(self, stats):
        newValues = Money.extractMoneyDict(stats)
        if newValues:
            self.__balance = self.__balance.replaceAll(newValues)
            self.onInvalidate()

    def __getMaxCount(self, boosterPrice, currency):
        result = 0
        if boosterPrice.get(currency, 0) > 0:
            result = math.floor(self.__balance.get(currency, 0) / boosterPrice.get(currency))
        return min(result, MAX_BOOSTERS_FOR_OPERATION)
