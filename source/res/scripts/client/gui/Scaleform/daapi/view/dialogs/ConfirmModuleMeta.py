# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/ConfirmModuleMeta.py
import math
from gui.Scaleform.daapi.view.dialogs import IDialogMeta
import Event
from gui.Scaleform.framework import ScopeTemplates
from gui.shared import events
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from helpers import i18n
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.utils.decorators import process
from gui.shared.gui_items.processors.module import ModuleBuyer, ModuleSeller
from gui.shared.money import MONEY_UNDEFINED, Currency, Money, CurrencyCollection
from gui.shared.tooltips.formatters import packActionTooltipData
from gui import SystemMessages
MAX_ITEMS_FOR_OPERATION = 1000000

class ConfirmModuleMeta(IDialogMeta):

    def __init__(self, typeCompactDescr, title, submitBtn, cancelBtn):
        self.__typeCompactDescr = typeCompactDescr
        self.__title = title
        self.__submitLabel = submitBtn
        self.__cancelLabel = cancelBtn
        self.onInvalidate = Event.Event()

    def destroy(self):
        self.onInvalidate.clear()

    def submit(self, item, count, currency):
        pass

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_CONFIRM_MODULE

    def getTitle(self):
        return i18n.makeString(self.__title)

    def getSubmitButtonLabel(self):
        return i18n.makeString(self.__submitLabel)

    def getCancelButtonLabel(self):
        return i18n.makeString(self.__cancelLabel)

    def getTypeCompDescr(self):
        return self.__typeCompactDescr

    def getMaxAvailableItemsCount(self, module):
        return CurrencyCollection(*(1 for _ in Currency.ALL))

    def getDefaultValue(self, module):
        pass

    def getActualPrices(self, module):
        """
        Get store module prices. Since currently compound prices are not supported, all item prices (original or
        alternative) are defined for only one currency. Therefore if an item has an alternative price, the method
        should return the original price + the alternative price to have all set currencies in one place.
        :param module:<FittingItem>
        :return:<Money>
        """
        return MONEY_UNDEFINED

    def getDefaultPrices(self, module):
        """
        Get default module prices. Since currently compound prices are not supported, all item prices (original or
        alternative) are defined for only one currency. Therefore if an item has an alternative price, the method
        should return the original price + the alternative price to have all set currencies in one place.
        :param module:<FittingItem>
        :return:<Money>
        """
        return MONEY_UNDEFINED

    def getCurrency(self, module):
        return self.getActualPrices(module).getCurrency(byWeight=True)

    def getActionVO(self, module):
        return None

    def getViewScopeType(self):
        return ScopeTemplates.DEFAULT_SCOPE


class SellModuleMeta(ConfirmModuleMeta):

    def __init__(self, typeCompactDescr):
        super(SellModuleMeta, self).__init__(typeCompactDescr, DIALOGS.SELLMODULECONFIRMATION_TITLE, DIALOGS.SELLMODULECONFIRMATION_SUBMIT, DIALOGS.SELLMODULECONFIRMATION_CANCEL)

    def getMaxAvailableItemsCount(self, module):
        """
        The maximum value is the value of items in inventory (no more then MAX_ITEMS_FOR_OPERATION)
        @param module: current item
        @return:
        """
        return CurrencyCollection(*(min(module.inventoryCount, MAX_ITEMS_FOR_OPERATION) for _ in Currency.ALL))

    def getDefaultValue(self, module):
        return module.inventoryCount

    @process('sellItem')
    def submit(self, item, count, currency):
        result = yield ModuleSeller(item, min(count, MAX_ITEMS_FOR_OPERATION)).request()
        if len(result.userMsg):
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def getActualPrices(self, module):
        return module.sellPrices.itemPrice.price

    def getDefaultPrices(self, module):
        return module.sellPrices.itemPrice.defPrice

    def getActionVO(self, module):
        prices = self.getActualPrices(module)
        defaultPrices = self.getDefaultPrices(module)
        return packActionTooltipData(ACTION_TOOLTIPS_TYPE.ITEM, str(module.intCD), False, prices, defaultPrices)


class LocalSellModuleMeta(SellModuleMeta):

    def getViewScopeType(self):
        return ScopeTemplates.LOBBY_SUB_SCOPE


class BuyModuleMeta(ConfirmModuleMeta):

    def __init__(self, typeCompactDescr, balance):
        super(BuyModuleMeta, self).__init__(typeCompactDescr, DIALOGS.BUYCONFIRMATION_TITLE, DIALOGS.BUYCONFIRMATION_SUBMIT, DIALOGS.BUYCONFIRMATION_CANCEL)
        self.__balance = balance
        g_clientUpdateManager.addCallbacks({'stats': self.__onStatsChanged})

    def __onStatsChanged(self, stats):
        newValues = Money.extractMoneyDict(stats)
        if newValues:
            self.__balance = self.__balance.replaceAll(newValues)
            self.onInvalidate()

    def __getMaxCount(self, module, currency):
        result = 0
        modulePrice = self.getActualPrices(module)
        if modulePrice.get(currency, 0) > 0:
            result = math.floor(self.__balance.get(currency, 0) / modulePrice.get(currency))
        return min(result, MAX_ITEMS_FOR_OPERATION)

    def destroy(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(BuyModuleMeta, self).destroy()

    def getMaxAvailableItemsCount(self, module):
        return CurrencyCollection(*(self.__getMaxCount(module, currency) for currency in Currency.ALL))

    def getDefaultValue(self, module):
        pass

    def getActualPrices(self, module):
        return module.buyPrices.getSum().price

    def getDefaultPrices(self, module):
        return module.buyPrices.getSum().defPrice

    def getActionVO(self, module):
        prices = self.getActualPrices(module)
        defaultPrices = self.getDefaultPrices(module)
        return packActionTooltipData(ACTION_TOOLTIPS_TYPE.ITEM, str(module.intCD), True, prices, defaultPrices)

    @process('buyItem')
    def submit(self, item, count, currency):
        result = yield ModuleBuyer(item, count, currency).request()
        if len(result.userMsg):
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
