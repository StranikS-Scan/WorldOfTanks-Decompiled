# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/ny_currency_controller.py
import logging
from new_year.gui.shared.ny_machine_helper import getMachineKeysCount, getMachineLootboxToken
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year_account_settings import getIsFirstMachineToken, setIsFirstMachineToken
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyGoldUrl
from new_year_common.items.components.ny_constants import TOKEN_MANDARIN
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.skeletons.new_year import INewYearCurrencyController
from gui.shared.notifications import NotificationPriorityLevel
from new_year.skeletons.new_year import INewYearController
from helpers.events_handler import EventsHandler
from gui.shared.event_dispatcher import showShop
from new_year.ny_constants import ViewAliases
from skeletons.gui.shared import IItemsCache
from gui.SystemMessages import SM_TYPE
from gui.shared.money import Currency
from gui.impl.gen.resources import R
from gui import SystemMessages
from helpers import dependency
from functools import partial
from gui.impl import backport
from Event import Event
_logger = logging.getLogger(__name__)

class NewYearCurrencyController(INewYearCurrencyController, EventsHandler):
    __slots__ = ('__currencyCountProviders', '__currencies')
    __itemsCache = dependency.descriptor(IItemsCache)
    __newYearController = dependency.descriptor(INewYearController)
    __DEFAULT_CURRENCIES = (NyCurrencyType.MANDARIN, NyCurrencyType.NYGIFTMACHINETOKEN, NyCurrencyType.CREDITS)

    def __init__(self, *args, **kwargs):
        super(NewYearCurrencyController, self).__init__(*args, **kwargs)
        self.onCurrencyUpdated = Event()
        self.onVisibleCurrenciesChanged = Event()
        self.__currencies = self.__DEFAULT_CURRENCIES
        self.__currencyCountProviders = {NyCurrencyType.MANDARIN: partial(self.__tokenProvider, TOKEN_MANDARIN),
         NyCurrencyType.NYGIFTMACHINETOKEN: getMachineKeysCount,
         NyCurrencyType.GOLD: partial(self.__currencyProvider, Currency.GOLD),
         NyCurrencyType.CREDITS: partial(self.__currencyProvider, Currency.CREDITS)}

    @property
    def getCurrencies(self):
        return self.__currencies

    @property
    def getGiftMachineTokenCount(self):
        return self.getCurrencyCount(NyCurrencyType.NYGIFTMACHINETOKEN)

    @property
    def getMandarinTokenCount(self):
        return self.getCurrencyCount(NyCurrencyType.MANDARIN)

    @property
    def getGoldCount(self):
        return self.getCurrencyCount(NyCurrencyType.GOLD)

    def getCurrencyClickHandler(self, currency):
        instantly = NewYearNavigation.getCurrentViewName() in (ViewAliases.PET_VIEW, ViewAliases.QUESTS_VIEW, ViewAliases.INFO_VIEW)
        handlers = {NyCurrencyType.NYGIFTMACHINETOKEN: partial(NewYearNavigation.switchToView, ViewAliases.SURPRISE_MACHINE_VIEW, instantly=instantly),
         NyCurrencyType.GOLD: partial(showShop, getBuyGoldUrl())}
        return handlers.get(currency)

    def getCurrencyCount(self, currency):
        if currency not in self.__currencyCountProviders:
            _logger.error('Unknown currency %s', currency)
            return 0
        return self.__currencyCountProviders[currency]()

    def setVisibleCurrencies(self, currencies=None):
        prev = self.__currencies
        if not currencies:
            newVal = self.__DEFAULT_CURRENCIES
        elif isinstance(currencies, (list, tuple)):
            newVal = tuple(currencies)
        else:
            newVal = (currencies,)
        if newVal != prev:
            self.__currencies = newVal
            self.onVisibleCurrenciesChanged()

    def init(self):
        self._subscribe()

    def fini(self):
        self._unsubscribe()
        self.onCurrencyUpdated.clear()
        self.onVisibleCurrenciesChanged.clear()

    def onDisconnected(self):
        self.__currencies = self.__DEFAULT_CURRENCIES

    def _getCallbacks(self):
        return (('stats.{}'.format(Currency.GOLD), self.__onGoldUpdated), ('stats.{}'.format(Currency.CREDITS), self.__onCreditsUpdated), ('tokens', self.__onTokensUpdated))

    @classmethod
    def __tokenProvider(cls, token):
        return cls.__itemsCache.items.tokens.getTokenCount(tokenID=token)

    @classmethod
    def __currencyProvider(cls, currency):
        return getattr(cls.__itemsCache.items.stats, currency)

    def __onGoldUpdated(self, diff):
        self.onCurrencyUpdated(Currency.GOLD, diff)

    def __onCreditsUpdated(self, diff):
        self.onCurrencyUpdated(Currency.CREDITS, diff)

    def __onTokensUpdated(self, diff):
        machineToken = getMachineLootboxToken()
        if machineToken in diff:
            machineTokenData = diff[machineToken]
            self.onCurrencyUpdated(NyCurrencyType.NYGIFTMACHINETOKEN, machineTokenData[1] if machineTokenData is not None else 0)
            if not getIsFirstMachineToken():
                SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.machine.text()), type=SM_TYPE.NewYearMachine, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.ny.notification.machine.header())})
                setIsFirstMachineToken(True)
        if TOKEN_MANDARIN in diff:
            mandarinToken = diff.get(TOKEN_MANDARIN, None)
            self.onCurrencyUpdated(NyCurrencyType.MANDARIN, mandarinToken[1] if mandarinToken is not None else 0)
        return
