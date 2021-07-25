# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/buy_vehicle_slot_dialog_view.py
import typing
from frameworks.wulf import ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.auxiliary.detachment_helper import getDetachmentVehicleSlotMoney
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.buy_vehicle_slot_dialog_view_model import BuyVehicleSlotDialogViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.shared.money import Currency
from gui.shop import showBuyGoldForDetachmentVehicleSlot
from helpers.dependency import descriptor
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.loggers import DetachmentLogger
from uilogging.detachment.constants import GROUP, ACTION

class BuyVehicleSlotDialogView(FullScreenDialogView):
    __itemsCache = descriptor(IItemsCache)
    uiLogger = DetachmentLogger(GROUP.BUY_VEHICLE_SLOT_DIALOG)
    __slots__ = ('_slotID', '_detachmentInvID')

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.BuyVehicleSlotDialogView())
        settings.model = BuyVehicleSlotDialogViewModel()
        self._slotID = ctx['slotID']
        self._detachmentInvID = ctx['detInvID']
        super(BuyVehicleSlotDialogView, self).__init__(settings)

    def _addListeners(self):
        super(BuyVehicleSlotDialogView, self)._addListeners()
        g_clientUpdateManager.addMoneyCallback(self._onMoneyUpdate)
        g_clientUpdateManager.addCallbacks({'shop.detachmentPriceGroups': self._onMoneyUpdate})

    def _removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(BuyVehicleSlotDialogView, self)._removeListeners()

    def _onAcceptClicked(self):
        money = getDetachmentVehicleSlotMoney(self._detachmentInvID, self._slotID, default=False)
        currency = money.getCurrency(byWeight=True)
        price = money.get(currency)
        playerCurrencyAmount = self.__itemsCache.items.stats.money.get(currency)
        if playerCurrencyAmount < price:
            if currency == Currency.GOLD:
                self.uiLogger.log(ACTION.BUY_GOLD)
                showBuyGoldForDetachmentVehicleSlot(price)
        else:
            self.uiLogger.log(ACTION.DIALOG_CONFIRM)
            super(BuyVehicleSlotDialogView, self)._onAcceptClicked()

    def _onExitClicked(self):
        self.uiLogger.log(ACTION.DIALOG_EXIT)
        super(BuyVehicleSlotDialogView, self)._onExitClicked()

    def _onCancelClicked(self):
        self.uiLogger.log(ACTION.DIALOG_CANCEL)
        super(BuyVehicleSlotDialogView, self)._onCancelClicked()

    @property
    def viewModel(self):
        return super(BuyVehicleSlotDialogView, self).getViewModel()

    def _onMoneyUpdate(self, *args, **kwargs):
        self._setBaseParams(self.viewModel)

    def _setBaseParams(self, model):
        with model.transaction() as viewModel:
            money = getDetachmentVehicleSlotMoney(self._detachmentInvID, self._slotID, default=False)
            currencyType = money.getCurrency(byWeight=True)
            currencyQuantity = int(money.get(currencyType))
            model.priceModel.setType(currencyType)
            model.priceModel.setValue(currencyQuantity)
            isEnough = currencyQuantity <= self.__itemsCache.items.stats.money.get(currencyType)
            model.priceModel.setIsEnough(isEnough)
            viewModel.setIsAcceptDisabled(not isEnough)
            viewModel.setAcceptButtonText(R.strings.dialogs.detachment.buyVehicleSlot.submit())
            viewModel.setCancelButtonText(R.strings.dialogs.detachment.buyVehicleSlot.cancel())
            viewModel.setTitleBody(R.strings.dialogs.detachment.buyVehicleSlot.title())
        super(BuyVehicleSlotDialogView, self)._setBaseParams(model)
