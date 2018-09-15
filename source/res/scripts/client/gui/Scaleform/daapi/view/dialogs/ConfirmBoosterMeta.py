# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/ConfirmBoosterMeta.py
import math
from Event import EventManager, Event
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.framework import ScopeTemplates
from gui.shared import events
from gui.shared.gui_items.processors.goodies import BoosterBuyer
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.utils.decorators import process
from gui.shared.money import Money, Currency, CurrencyCollection
from gui.shared.tooltips.formatters import packActionTooltipData
from gui import SystemMessages
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
        """
        Returns tuple that contains max counts of booster that the user can buy for the current balance. Currency
        index in the tuple corresponds to the default order (see Currency.ALL).
        :return: CurrencyCollection(namedtuple)
        """
        buyPrice = self.__boosterBuyPricesSum.price
        return CurrencyCollection(*(self.__getMaxCount(buyPrice, currency) for currency in Currency.ALL))

    def getActionVO(self):
        return packActionTooltipData(ACTION_TOOLTIPS_TYPE.BOOSTER, str(self.__booster.boosterID), True, self.__boosterBuyPricesSum.price, self.__boosterBuyPricesSum.defPrice) if self.__boosterBuyPricesSum.isActionPrice() else None

    def getCurrency(self):
        """
        Returns the original buy currency, see Currency enum.
        :return: string
        """
        return self.__booster.getBuyPrice(preferred=True).getCurrency(byWeight=True)

    def getPrices(self):
        """
        Returns all set currencies(prices) for buying the booster.
        Right now booster's price can be defined only in one currency (in the same time any booster can have an
        alternative price). So sum the original and the alternative price to have all set currencies in one place.
        Note that such logic will not work with compound prices (multi-currency price).
        :return: ItemPrices
        """
        return self.__booster.buyPrices

    @process('buyItem')
    def submit(self, count, currency):
        result = yield BoosterBuyer(self.__booster, count, currency).request()
        if len(result.userMsg):
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

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
