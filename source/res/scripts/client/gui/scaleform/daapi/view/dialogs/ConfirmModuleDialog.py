# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/ConfirmModuleDialog.py
from PlayerEvents import g_playerEvents
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.meta.ConfirmItemWindowMeta import ConfirmItemWindowMeta
from gui.Scaleform.genConsts.CONFIRM_DIALOG_ALIASES import CONFIRM_DIALOG_ALIASES
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
            hasSeveralPrices = len(setCurrencies) > 1
            if hasSeveralPrices and Currency.CREDITS in setCurrencies:
                if item.itemTypeID == GUI_ITEM_TYPE.SHELL:
                    hasSeveralPrices = shop.isEnabledBuyingGoldShellsForCredits
                elif item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
                    hasSeveralPrices = shop.isEnabledBuyingGoldEqsForCredits
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
             'hasSeveralPrices': hasSeveralPrices,
             'moduleLabel': item.getGUIEmblemID(),
             'level': item.level,
             'linkage': CONFIRM_DIALOG_ALIASES.MODULE_ICON,
             EXTRA_MODULE_INFO: extraData,
             FIELD_HIGHLIGHT_TYPE: item.getHighlightType(),
             'overlayType': item.getOverlayType()}
            self.as_setDataS(resultData)
        else:
            LOG_ERROR("Couldn't find module with given compact:", self.meta.getTypeCompDescr())
            self.onWindowClose()
        return

    @staticmethod
    def __getIcon(item):
        return str(item.level) if item.itemTypeID not in (GUI_ITEM_TYPE.OPTIONALDEVICE,
         GUI_ITEM_TYPE.SHELL,
         GUI_ITEM_TYPE.EQUIPMENT,
         GUI_ITEM_TYPE.CREW_BOOKS) else item.icon

    def onWindowClose(self):
        self._callHandler(False)
        self.destroy()

    def submit(self, count, currency):
        item = self.itemsCache.items.getItemByCD(self.meta.getTypeCompDescr())
        self.meta.submit(item, count, currency)
        self._callHandler(True, self.meta.getTypeCompDescr(), count, currency)
        self.destroy()
