# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/ConfirmModuleMeta.py
import math
from gui.Scaleform.daapi.view.dialogs import IDialogMeta
import Event
from gui.Scaleform.framework import ScopeTemplates
from gui.shared import events
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE, ACTION_TOOLTIPS_STATE
from helpers import i18n
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.utils.decorators import process
from gui.shared.gui_items.processors.module import ModuleBuyer, ModuleSeller
from gui.shared.money import ZERO_MONEY, Currency
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
        pass

    def getDefaultValue(self, module):
        pass

    def getActualPrice(self, module):
        return ZERO_MONEY

    def getDefaultPrice(self, module):
        return ZERO_MONEY

    def getCurrency(self, module):
        return None

    def getActionVO(self, module):
        return None

    def getViewScopeType(self):
        return ScopeTemplates.DEFAULT


class SellModuleMeta(ConfirmModuleMeta):

    def __init__(self, typeCompactDescr):
        super(SellModuleMeta, self).__init__(typeCompactDescr, DIALOGS.SELLMODULECONFIRMATION_TITLE, DIALOGS.SELLMODULECONFIRMATION_SUBMIT, DIALOGS.SELLMODULECONFIRMATION_CANCEL)

    def getMaxAvailableItemsCount(self, module):
        """
        The maximum value is the value of items in inventory (no more then MAX_ITEMS_FOR_OPERATION)
        @param module: current item
        @return:
        """
        return (min(module.inventoryCount, MAX_ITEMS_FOR_OPERATION), min(module.inventoryCount, MAX_ITEMS_FOR_OPERATION))

    def getDefaultValue(self, module):
        return module.inventoryCount

    @process('sellItem')
    def submit(self, item, count, currency):
        result = yield ModuleSeller(item, min(count, MAX_ITEMS_FOR_OPERATION)).request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def getActualPrice(self, module):
        return module.sellPrice

    def getDefaultPrice(self, module):
        return module.defaultSellPrice

    def getActionVO(self, module):
        price = self.getActualPrice(module)
        defaultPrice = self.getDefaultPrice(module)
        return packActionTooltipData(ACTION_TOOLTIPS_TYPE.ITEM, str(module.intCD), False, price, defaultPrice)

    def getCurrency(self, module):
        return module.getSellPriceCurrency()


class LocalSellModuleMeta(SellModuleMeta):

    def getViewScopeType(self):
        return ScopeTemplates.LOBBY_SUB


class BuyModuleMeta(ConfirmModuleMeta):

    def __init__(self, typeCompactDescr, balance):
        super(BuyModuleMeta, self).__init__(typeCompactDescr, DIALOGS.BUYCONFIRMATION_TITLE, DIALOGS.BUYCONFIRMATION_SUBMIT, DIALOGS.BUYCONFIRMATION_CANCEL)
        self.__balance = balance
        g_clientUpdateManager.addCallbacks({'stats': self.__onStatsChanged})

    def __onStatsChanged(self, stats):
        if 'credits' in stats:
            self.__balance = self.__balance.replace(Currency.CREDITS, stats['credits'])
            self.onInvalidate()
        if 'gold' in stats:
            self.__balance = self.__balance.replace(Currency.GOLD, stats['gold'])
            self.onInvalidate()

    def __getMaxCount(self, module, currency):
        result = 0
        modulePrice = self.getActualPrice(module)
        if modulePrice.get(currency) > 0:
            result = math.floor(self.__balance.get(currency) / modulePrice.get(currency))
        return min(result, MAX_ITEMS_FOR_OPERATION)

    def destroy(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(BuyModuleMeta, self).destroy()

    def getMaxAvailableItemsCount(self, module):
        return (self.__getMaxCount(module, Currency.CREDITS), self.__getMaxCount(module, Currency.GOLD))

    def getDefaultValue(self, module):
        pass

    def getActualPrice(self, module):
        return module.altPrice or module.buyPrice

    def getDefaultPrice(self, module):
        return module.defaultAltPrice or module.defaultPrice

    def getActionVO(self, module):
        price = self.getActualPrice(module)
        defaultPrice = self.getDefaultPrice(module)
        return packActionTooltipData(ACTION_TOOLTIPS_TYPE.ITEM, str(module.intCD), True, price, defaultPrice)

    def getCurrency(self, module):
        return module.getBuyPriceCurrency()

    @process('buyItem')
    def submit(self, item, count, currency):
        result = yield ModuleBuyer(item, count, currency == Currency.CREDITS).request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
