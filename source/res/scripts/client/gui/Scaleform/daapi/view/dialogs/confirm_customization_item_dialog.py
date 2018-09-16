# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/confirm_customization_item_dialog.py
from debug_utils import LOG_ERROR
from PlayerEvents import g_playerEvents
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.ConfirmItemWindowMeta import ConfirmItemWindowMeta
from gui.shared.formatters import getMoneyVO
from gui.shared.gui_items import GUI_ITEM_TYPE

class ConfirmCustomizationItemDialog(ConfirmItemWindowMeta):

    def __init__(self, meta, handler):
        super(ConfirmCustomizationItemDialog, self).__init__()
        self.meta = meta
        self.handler = handler

    def _populate(self):
        super(ConfirmCustomizationItemDialog, self)._populate()
        g_playerEvents.onShopResync += self.__onUpdate
        g_clientUpdateManager.addCallbacks({'stats': self.__onUpdate})
        self._prepareAndSendData()
        self.as_setSettingsS({'title': self.meta.getTitle(),
         'submitBtnLabel': self.meta.getSubmitButtonLabel(),
         'cancelBtnLabel': self.meta.getCancelButtonLabel()})

    def _dispose(self):
        g_playerEvents.onShopResync -= self.__onUpdate
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.meta is not None:
            self.meta.destroy()
            self.meta = None
        self.handler = None
        super(ConfirmCustomizationItemDialog, self)._dispose()
        return

    def onWindowClose(self):
        self._callHandler(False)
        self.destroy()

    def submit(self, count, currency):
        self.meta.submit(self.meta.getItem(), count, currency)
        self._callHandler(True, self.meta.getItem(), count, currency)
        self.destroy()

    def _callHandler(self, success, *kargs):
        if self.handler is not None:
            self.handler((success, kargs))
        return

    def _prepareAndSendData(self):
        item = self.meta.getItem()
        if item is not None:
            actualPrices = self.meta.getActualPrices(item)
            defaultPrices = self.meta.getDefaultPrices(item)
            currency = self.meta.getCurrency(item)
            setCurrencies = actualPrices.toSignDict()
            hasAlternativePrice = len(setCurrencies) > 1
            action = None
            if actualPrices != defaultPrices:
                action = self.meta.getActionVO(item)
            iconWidth = iconHeight = 59
            if item.isWide():
                iconWidth = 118 if item.itemTypeID == GUI_ITEM_TYPE.INSCRIPTION else 161
            smallSlotVO = {'itemIcon': item.icon,
             'isBgVisible': False,
             'isFrameVisible': True,
             'iconWidth': iconWidth,
             'iconHeight': iconHeight}
            resultData = {'id': item.intCD,
             'price': getMoneyVO(actualPrices),
             'actionPriceData': action,
             'name': item.userName,
             'currency': currency,
             'defaultValue': self.meta.getDefaultValue(item),
             'maxAvailableCount': self.meta.getMaxAvailableItemsCount(item),
             'hasSeveralPrices': hasAlternativePrice,
             'smallSlotVO': smallSlotVO}
            self.as_setDataS(resultData)
        else:
            LOG_ERROR("Couldn't find given customization item: ", self.meta.getItem())
            self.onWindowClose()
        return

    def __onUpdate(self, *_):
        self._prepareAndSendData()
