# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/ConfirmModuleDialog.py
from PlayerEvents import g_playerEvents
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.meta.ConfirmItemWindowMeta import ConfirmItemWindowMeta
from gui.Scaleform.genConsts.CONFIRM_DIALOG_ALIASES import CONFIRM_DIALOG_ALIASES
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.shared.formatters import getMoneyVO
from gui.shared.utils import EXTRA_MODULE_INFO, FIELD_HIGHLIGHT_TYPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class ConfirmModuleDialog(ConfirmItemWindowMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, meta, handler):
        super(ConfirmModuleDialog, self).__init__()
        self.meta = meta
        self.handler = handler

    def _populate(self):
        super(ConfirmModuleDialog, self)._populate()
        g_playerEvents.onShopResync += self._onShopResync
        self._prepareAndSendData()
        self.as_setSettingsS({'title': self.meta.getTitle(),
         'submitBtnLabel': self.meta.getSubmitButtonLabel(),
         'cancelBtnLabel': self.meta.getCancelButtonLabel()})
        self.meta.onInvalidate += self._prepareAndSendData

    def _dispose(self):
        g_playerEvents.onShopResync -= self._onShopResync
        if self.meta is not None:
            self.meta.onInvalidate -= self._prepareAndSendData
            self.meta.destroy()
            self.meta = None
        self.handler = self._data = None
        super(ConfirmModuleDialog, self)._dispose()
        return

    def _callHandler(self, success, *kargs):
        if self.handler is not None:
            self.handler((success, kargs))
        return

    def _onShopResync(self):
        self._prepareAndSendData()

    def _prepareAndSendData(self):
        items = self.itemsCache.items
        item = items.getItemByCD(self.meta.getTypeCompDescr())
        if item is not None:
            shop = self.itemsCache.items.shop
            actualPrices = self.meta.getActualPrices(item)
            defaultPrices = self.meta.getDefaultPrices(item)
            currency = self.meta.getCurrency(item)
            setCurrencies = actualPrices.toSignDict()
            hasAlternativePrice = len(setCurrencies) > 1
            if hasAlternativePrice and Currency.CREDITS in setCurrencies:
                if item.itemTypeID == GUI_ITEM_TYPE.SHELL:
                    hasAlternativePrice = shop.isEnabledBuyingGoldShellsForCredits
                elif item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
                    hasAlternativePrice = shop.isEnabledBuyingGoldEqsForCredits
            icon = self.__getIcon(item)
            extraData = item.getExtraIconInfo()
            action = None
            if actualPrices != defaultPrices:
                action = self.meta.getActionVO(item)
            resultData = {'id': self.meta.getTypeCompDescr(),
             'price': getMoneyVO(actualPrices),
             'actionPriceData': action,
             'icon': icon,
             'name': item.userName,
             'description': item.getShortInfo(),
             'currency': currency,
             'defaultValue': self.meta.getDefaultValue(item),
             'maxAvailableCount': self.meta.getMaxAvailableItemsCount(item),
             'isActionNow': hasAlternativePrice,
             'moduleLabel': item.getGUIEmblemID(),
             'level': item.level,
             'linkage': CONFIRM_DIALOG_ALIASES.MODULE_ICON,
             EXTRA_MODULE_INFO: extraData,
             FIELD_HIGHLIGHT_TYPE: self.__getHighlightType(item)}
            self.as_setDataS(resultData)
        else:
            LOG_ERROR("Couldn't find module with given compact:", self.meta.getTypeCompDescr())
            self.onWindowClose()
        return

    @staticmethod
    def __getIcon(item):
        return str(item.level) if item.itemTypeID not in (GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.SHELL, GUI_ITEM_TYPE.EQUIPMENT) else item.icon

    @staticmethod
    def __getHighlightType(item):
        if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            return SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER
        return SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and item.isDeluxe() else SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT

    def onWindowClose(self):
        self._callHandler(False)
        self.destroy()

    def submit(self, count, currency):
        item = self.itemsCache.items.getItemByCD(self.meta.getTypeCompDescr())
        self.meta.submit(item, count, currency)
        self._callHandler(True, self.meta.getTypeCompDescr(), count, currency)
        self.destroy()
