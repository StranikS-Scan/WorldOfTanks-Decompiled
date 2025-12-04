# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/gui_items/processors/armory_yard_reroll_processors.py
import BigWorld
from gui.shared.gui_items.processors import Processor
from gui.shared.gui_items.processors.plugins import MoneyValidator, SyncValidator, WalletValidator, makeSuccess, makeError
from gui.shared.money import Money
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from armory_yard_constants import CURRENT_REROLL_PDATA_KEY, getConditionToken
from armory_yard.skeletons.armory_yard_reroll_controller import IArmoryYardRerollController
from armory_yard.gui.shared.gui_items.processors.armory_yard_processors import ArmoryYardEventValidator

class RerollCurrencyValidator(SyncValidator):
    __slots__ = ('__currency',)
    __armoryYardRerollCtrl = dependency.descriptor(IArmoryYardRerollController)

    def __init__(self, currency):
        super(RerollCurrencyValidator, self).__init__()
        self.__currency = currency

    def _validate(self):
        return makeError('invalid_currency: {}'.format(self.__currency)) if self.__currency not in self.__armoryYardRerollCtrl.getRerollCurrencies() else makeSuccess()


class AcceptRerollQuestValidator(SyncValidator):
    __slots__ = ('__conditionID', '__questID')
    __itemsCache = dependency.descriptor(IItemsCache)
    __armoryYardRerollCtrl = dependency.descriptor(IArmoryYardRerollController)

    def __init__(self, conditionID, questID):
        super(AcceptRerollQuestValidator, self).__init__()
        self.__conditionID = conditionID
        self.__questID = questID

    def _validate(self):
        questData = self.__itemsCache.items.armoryYard.data.get(CURRENT_REROLL_PDATA_KEY, None)
        if questData:
            conditions = questData.get(self.__questID, {}).get('conditions')
            if not conditions:
                return makeError('cannot accept reroll, questID not in current reroll : {}'.format(self.__questID))
            if self.__conditionID not in conditions and not self.__armoryYardRerollCtrl.getConditionQuestsByID(getConditionToken(self.__conditionID)):
                return makeError('cannot accept reroll, conditionID not in current reroll conditions: {}'.format(self.__conditionID))
        return makeSuccess()


class RerollQuest(Processor):
    __slots__ = ('__questID', '__rerollCurrency', '__rerollCost')
    __armoryYardRerollCtrl = dependency.descriptor(IArmoryYardRerollController)

    def __init__(self, questID, rerollCurrency='', plugins=None):
        super(RerollQuest, self).__init__(plugins)
        self.__questID = questID
        self.__rerollCurrency = rerollCurrency
        self.__rerollCost = self.__armoryYardRerollCtrl.getRerollCost(self.__rerollCurrency)
        self.addPlugin(ArmoryYardEventValidator())
        if self.__rerollCurrency:
            self.addPlugins((RerollCurrencyValidator(self.__rerollCurrency), WalletValidator()))
        if self.__rerollCost:
            rerollMoney = Money.makeFrom(self.__rerollCurrency, self.__rerollCost)
            self.addPlugin(MoneyValidator(rerollMoney))

    def _request(self, callback):
        if self.__rerollCurrency:
            BigWorld.player().AccountArmoryYardRerollComponent.rerollArmoryQuestPaid(self.__questID, self.__rerollCost, self.__rerollCurrency, lambda requestID, resultID, errorStr, ctx=None: self._response(resultID, callback, errorStr, ctx))
        else:
            BigWorld.player().AccountArmoryYardRerollComponent.rerollArmoryQuestFree(self.__questID, lambda requestID, resultID, errorStr, ctx=None: self._response(resultID, callback, errorStr, ctx))
        return


class AcceptReroll(Processor):
    __slots__ = ('__conditionID', '__questID')
    __armoryYardRerollCtrl = dependency.descriptor(IArmoryYardRerollController)

    def __init__(self, conditionID, questID, plugins=None):
        super(AcceptReroll, self).__init__(plugins)
        self.__conditionID = conditionID
        self.__questID = questID
        self.addPlugins((ArmoryYardEventValidator(), AcceptRerollQuestValidator(self.__conditionID, self.__questID)))

    def _request(self, callback):
        BigWorld.player().AccountArmoryYardRerollComponent.acceptReroll(self.__conditionID, self.__questID, lambda requestID, resultID, errorStr, ctx=None: self._response(resultID, callback, errorStr, ctx))
        return
