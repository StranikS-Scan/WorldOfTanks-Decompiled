# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/confirm_customization_item_dialog_meta.py
import math
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.dialogs import IDialogMeta
from gui.Scaleform.framework import ScopeTemplates
from gui.shared import events
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from helpers import i18n
from gui import SystemMessages
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.shared.gui_items.processors.common import CustomizationsBuyer
from gui.shared.money import Currency, CurrencyCollection
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.utils.decorators import process
from items.components.c11n_constants import MAX_ITEMS_FOR_BUY_OPERATION
from skeletons.gui.shared import IItemsCache
from helpers import dependency

class ConfirmC11nBuyMeta(IDialogMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, itemCD, title=DIALOGS.BUYCONFIRMATION_TITLE, submitBtn=DIALOGS.BUYCONFIRMATION_SUBMIT, cancelBtn=DIALOGS.BUYCONFIRMATION_CANCEL):
        self.__item = self.itemsCache.items.getItemByCD(itemCD)
        self.__title = title
        self.__submitLabel = submitBtn
        self.__cancelLabel = cancelBtn

    def destroy(self):
        pass

    @process('buyItem')
    def submit(self, item, count, _):
        result = yield CustomizationsBuyer(g_currentVehicle.item, item, count).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_CONFIRM_C11N_BUY_DIALOG

    def getTitle(self):
        return i18n.makeString(self.__title)

    def getSubmitButtonLabel(self):
        return i18n.makeString(self.__submitLabel)

    def getCancelButtonLabel(self):
        return i18n.makeString(self.__cancelLabel)

    def getItem(self):
        return self.__item

    def getViewScopeType(self):
        return ScopeTemplates.DEFAULT_SCOPE

    def getActualPrices(self, item):
        return item.buyPrices.getSum().price

    def getCurrency(self, item):
        return self.getActualPrices(item).getCurrency(byWeight=True)

    def getDefaultPrices(self, item):
        return item.buyPrices.getSum().defPrice

    def getActionVO(self, item):
        prices = self.getActualPrices(item)
        defaultPrices = self.getDefaultPrices(item)
        return packActionTooltipData(ACTION_TOOLTIPS_TYPE.ITEM, str(item.intCD), True, prices, defaultPrices)

    def getDefaultValue(self, _):
        pass

    def getMaxAvailableItemsCount(self, item):
        balance = self.itemsCache.items.stats.money
        return CurrencyCollection(*(self.__getMaxCount(item, currency, balance) for currency in Currency.ALL))

    def __getMaxCount(self, item, currency, balance):
        result = 0
        modulePrice = self.getActualPrices(item)
        if modulePrice.get(currency, 0) > 0:
            result = math.floor(balance.get(currency, 0) / modulePrice.get(currency))
        return min(result, MAX_ITEMS_FOR_BUY_OPERATION)


class ConfirmC11nSellMeta(ConfirmC11nBuyMeta):

    def __init__(self, itemCD, count, handler, title=DIALOGS.SELLMODULECONFIRMATION_TITLE, submitBtn=DIALOGS.SELLMODULECONFIRMATION_SUBMIT, cancelBtn=DIALOGS.SELLMODULECONFIRMATION_CANCEL):
        super(ConfirmC11nSellMeta, self).__init__(itemCD, title, submitBtn, cancelBtn)
        self.__count = count
        self.__handler = handler

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_CONFIRM_C11N_SELL_DIALOG

    def getMaxAvailableItemsCount(self, _):
        return CurrencyCollection(*(self.__count for _ in Currency.ALL))

    def getDefaultValue(self, _):
        return self.__count

    def getActualPrices(self, item):
        return item.sellPrices.getSum().price

    def getDefaultPrices(self, item):
        return item.sellPrices.getSum().defPrice

    def submit(self, item, count, _):
        self.__handler(item.intCD, count)

    def getActionVO(self, item):
        prices = self.getActualPrices(item)
        defaultPrices = self.getDefaultPrices(item)
        return packActionTooltipData(ACTION_TOOLTIPS_TYPE.ITEM, str(item.intCD), False, prices, defaultPrices)
