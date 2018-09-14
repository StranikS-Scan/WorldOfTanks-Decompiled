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
from gui.shared.money import Money, Currency
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
        return (self.__getMaxCount(Currency.CREDITS), self.__getMaxCount(Currency.GOLD))

    def getActionVO(self):
        buyPrice = self.__booster.buyPrice
        defaultPrice = self.__booster.defaultPrice
        return packActionTooltipData(ACTION_TOOLTIPS_TYPE.BOOSTER, str(self.__booster.boosterID), True, buyPrice, defaultPrice) if buyPrice != defaultPrice else None

    def getCurrency(self):
        return self.__booster.getBuyPriceCurrency()

    def getPrice(self):
        return self.__booster.buyPrice

    @process('buyItem')
    def submit(self, count, currency):
        result = yield BoosterBuyer(self.__booster, count, currency == Currency.GOLD).request()
        if len(result.userMsg):
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __onStatsChanged(self, stats):
        newValues = Money.extractMoneyDict(stats)
        if newValues:
            self.__balance = self.__balance.replaceAll(newValues)
            self.onInvalidate()

    def __getMaxCount(self, currency):
        result = 0
        boosterPrice = self.__booster.buyPrice
        if boosterPrice.get(currency) > 0:
            result = math.floor(self.__balance.get(currency) / boosterPrice.get(currency))
        return min(result, MAX_BOOSTERS_FOR_OPERATION)
