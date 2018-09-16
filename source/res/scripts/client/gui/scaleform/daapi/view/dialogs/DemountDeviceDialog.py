# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/DemountDeviceDialog.py
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.dialogs.IconPriceDialog import IconPriceDialog
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.ingame_shop import showBuyGoldForEquipment
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class DemountDeviceDialog(IconPriceDialog):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, meta, handler):
        super(IconPriceDialog, self).__init__(meta, handler)
        self.__price = self._meta.getMessagePrice().price

    def _populate(self):
        self._meta.onConfirmationStatusChanged += self.__handleConfirmationStatusChanged
        super(DemountDeviceDialog, self)._populate()
        self.__handleConfirmationStatusChanged(self.__operationAllowed())

    def __handleConfirmationStatusChanged(self, operationAllowed):
        self.as_setOperationAllowedS(operationAllowed)
        self.as_setButtonEnablingS(DIALOG_BUTTON_ID.SUBMIT, operationAllowed)
        if not operationAllowed:
            self.as_setButtonFocusS(DIALOG_BUTTON_ID.CLOSE)

    def __operationAllowed(self):
        goldEnough = self.__enoughCurrency(Currency.GOLD)
        crystalEnough = self.__enoughCurrency(Currency.CRYSTAL)
        return goldEnough and crystalEnough or crystalEnough and isIngameShopEnabled()

    def onButtonClick(self, buttonID):
        if buttonID != DIALOG_BUTTON_ID.SUBMIT:
            self.destroy()
            return
        if self.__enoughCurrency(Currency.GOLD):
            super(DemountDeviceDialog, self).onButtonClick(buttonID)
        elif isIngameShopEnabled():
            showBuyGoldForEquipment(self.__price.get(Currency.GOLD, 0))

    def __enoughCurrency(self, currency):
        return self.__price.get(currency, 0) <= self.itemsCache.items.stats.money.get(currency, 0)

    def _dispose(self):
        if self._meta is not None:
            self._meta.onConfirmationStatusChanged -= self.__handleConfirmationStatusChanged
            self._meta.dispose()
        super(IconPriceDialog, self)._dispose()
        return
