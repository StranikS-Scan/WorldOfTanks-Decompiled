# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/gui_items/processors/armory_yard.py
import BigWorld
from gui.shared.gui_items.processors import Processor, makeSuccess, makeError
from gui.shared.gui_items.processors.plugins import MoneyValidator, SyncValidator, WalletValidator
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController

class ArmoryYardEventValidator(SyncValidator):
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def _validate(self):
        return makeError('event_is_not_active') if not self.__armoryYardCtrl.isActive() else makeSuccess()


class BuyStepTokenCountValidator(SyncValidator):
    __slots__ = ('__buyCount',)
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self, buyCount, plugins=None):
        super(BuyStepTokenCountValidator, self).__init__(plugins)
        self.__buyCount = buyCount

    def _validate(self):
        currencyTokenCount = self.__armoryYardCtrl.getCurrencyTokenCount()
        maximumTokenCount = self.__armoryYardCtrl.getTotalSteps()
        if self.__buyCount <= 0:
            return makeError('invalid_count')
        return makeError('result_token_count_more_than_max') if currencyTokenCount + self.__buyCount > maximumTokenCount else makeSuccess()


class CurrencyValidator(SyncValidator):
    __slots__ = ('__currency',)
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self, currency, plugins=None):
        super(CurrencyValidator, self).__init__(plugins)
        self.__currency = currency

    def _validate(self):
        return makeError('invalid_currency: {}'.format(self.__currency)) if self.__currency not in self.__armoryYardCtrl.getTokenCurrencies() else makeSuccess()


class CollectRewardsProcessor(Processor):

    def __init__(self, plugins=None):
        super(CollectRewardsProcessor, self).__init__(plugins)
        self.addPlugins((ArmoryYardEventValidator(),))

    def _request(self, callback):
        BigWorld.player().AccountArmoryYardComponent.collectAllRewards(lambda requestID, resultID, errStr, ctx=None: self._response(resultID, callback, errStr, ctx))
        return


class BuyStepTokens(Processor):
    __slots__ = ('__count', '__currency')
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self, count, currency, plugins=None):
        super(BuyStepTokens, self).__init__(plugins)
        self.__count = count
        self.__currency = currency
        price = self.__count * self.__armoryYardCtrl.getCurrencyTokenCost(self.__currency)
        self.addPlugins((ArmoryYardEventValidator(),
         BuyStepTokenCountValidator(self.__count),
         CurrencyValidator(self.__currency),
         WalletValidator(),
         MoneyValidator(price)))

    def _request(self, callback):
        BigWorld.player().AccountArmoryYardComponent.buyStepTokens(self.__currency, self.__count, lambda requestID, resultID, errorStr, ctx=None: self._response(resultID, callback, errorStr, ctx))
        return
