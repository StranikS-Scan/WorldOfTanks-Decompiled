# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/shared/ny_currency_provider.py
from functools import partial
import logging
from Event import Event
from gui.shared.money import Currency
from gui.shared.notifications import NotificationPriorityLevel
from gui.impl.gen.resources import R
from gui.impl import backport
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from helpers import dependency
from helpers.events_handler import EventsHandler
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.shared.ny_machine_helper import getMachineKeysCount, getMachineLootboxToken
from new_year.skeletons.new_year import INewYearController
from new_year_common.items.components.ny_constants import TOKEN_NY25_MANDARIN
from new_year_account_settings import getIsFirstMachineToken, setIsFirstMachineToken
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class NyCurrencyProvider(EventsHandler):
    __slots__ = ('__currencyCountProviders', 'onCurrencyUpdated')
    __itemsCache = dependency.descriptor(IItemsCache)
    __newYearController = dependency.descriptor(INewYearController)

    def __init__(self):
        self.onCurrencyUpdated = Event()
        self.__currencyCountProviders = {NyCurrencyType.MANDARIN: partial(self.__tokenProvider, TOKEN_NY25_MANDARIN),
         NyCurrencyType.NYGIFTMACHINETOKEN: getMachineKeysCount,
         NyCurrencyType.GOLD: partial(self.__currencyProvider, Currency.GOLD)}

    def initialize(self):
        self._subscribe()

    def finalize(self):
        self.onCurrencyUpdated.clear()
        self._unsubscribe()

    def _getCallbacks(self):
        return (('stats.{}'.format(Currency.GOLD), self.__onCurrencyUpdated), ('tokens', self.__onTokensUpdated))

    @classmethod
    def __tokenProvider(cls, token):
        return cls.__itemsCache.items.tokens.getTokenCount(tokenID=token)

    @classmethod
    def __currencyProvider(cls, currency):
        return getattr(cls.__itemsCache.items.stats, currency)

    def getCurrencyCount(self, currency):
        if currency not in self.__currencyCountProviders:
            _logger.error('Unknown currency %s', currency)
            return 0
        return self.__currencyCountProviders[currency]()

    def __onCurrencyUpdated(self, diff):
        self.onCurrencyUpdated(Currency.GOLD, diff)

    def __onTokensUpdated(self, diff):
        machineToken = getMachineLootboxToken()
        if machineToken in diff:
            machineTokenData = diff[machineToken]
            self.onCurrencyUpdated(NyCurrencyType.NYGIFTMACHINETOKEN, machineTokenData[1] if machineTokenData is not None else 0)
            if not getIsFirstMachineToken():
                SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.machine.text()), type=SM_TYPE.NewYearMachine, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.ny.notification.machine.header())})
                setIsFirstMachineToken(True)
        if TOKEN_NY25_MANDARIN in diff:
            mandarinToken = diff.get(TOKEN_NY25_MANDARIN, None)
            self.onCurrencyUpdated(NyCurrencyType.MANDARIN, mandarinToken[1] if mandarinToken is not None else 0)
        return
