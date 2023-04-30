# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/gui_items/processors/armory_yard.py
import BigWorld
from gui.shared.gui_items.processors import Processor, makeSuccess, makeError
from gui.shared.gui_items.processors.plugins import MoneyValidator, SyncValidator, WalletValidator
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController

class ArmoryYardEventValidator(SyncValidator):
    __armoryYard = dependency.descriptor(IArmoryYardController)

    def _validate(self):
        return makeError('event_is_not_active') if not self.__armoryYard.isActive() else makeSuccess()


class BuyStepTokenCountValidator(SyncValidator):
    __slots__ = ('__buyCount',)
    __armoryYard = dependency.descriptor(IArmoryYardController)

    def __init__(self, buyCount, plugins=None):
        super(BuyStepTokenCountValidator, self).__init__(plugins)
        self.__buyCount = buyCount

    def _validate(self):
        currencyTokenCount = self.__armoryYard.getCurrencyTokenCount()
        maximumTokenCount = self.__armoryYard.getTotalSteps()
        if self.__buyCount <= 0:
            return makeError('invalid_count')
        return makeError('result_token_count_more_than_max') if currencyTokenCount + self.__buyCount > maximumTokenCount else makeSuccess()


class CollectRewardsProcessor(Processor):

    def __init__(self, plugins=None):
        super(CollectRewardsProcessor, self).__init__(plugins)
        self.addPlugins((ArmoryYardEventValidator(),))

    def _request(self, callback):
        BigWorld.player().AccountArmoryYardComponent.collectAllRewards(lambda requestID, resultID, errStr, ctx=None: self._response(resultID, callback, errStr, ctx))
        return


class BuyStepTokens(Processor):
    __slots__ = ('__count',)
    __armoryYard = dependency.descriptor(IArmoryYardController)

    def __init__(self, count, plugins=None):
        super(BuyStepTokens, self).__init__(plugins)
        self.__count = count
        price = self.__count * self.__armoryYard.getCurrencyTokenCost()
        self.addPlugins((ArmoryYardEventValidator(),
         BuyStepTokenCountValidator(self.__count),
         WalletValidator(),
         MoneyValidator(price)))

    def _request(self, callback):
        BigWorld.player().AccountArmoryYardComponent.buyStepTokens(self.__armoryYard.getCurrencyTokenCost().getCurrency(), self.__count, lambda requestID, resultID, errorStr, ctx=None: self._response(resultID, callback, errorStr, ctx))
        return
