# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/retrain_dialog.py
from typing import TYPE_CHECKING, Any, Optional
import BigWorld
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.customization.shared import getPurchaseGoldForCredits, getPurchaseMoneyState, MoneyForPurchase
from gui.impl.auxiliary.tankman_operations import ITEM_PRICE_FREE
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.dialogs.widgets.single_price import SinglePriceWidget
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencySize
from gui.impl.gen.view_models.views.lobby.crew.dialogs.retrain_dialog_model import RetrainDialogModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.retrain_tankman_model import RetrainTankmanModel
from gui.impl.lobby.crew.dialogs.price_cards_content.retrain_price_list import RetrainPriceList
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import event_dispatcher
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.items_actions import factory
from gui.shared.money import Money
from gui.shop import showBuyGoldForCrew
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
_LOC = R.strings.dialogs.retrain

class RetrainDialog(BaseCrewDialogTemplateView):
    __slots__ = ('_tankmen', '_vehicle', '_selectedTankmenIds', '_priceListContent')
    LAYOUT_ID = R.views.lobby.crew.dialogs.RetrainDialog()
    VIEW_MODEL = RetrainDialogModel
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, tankmenIds, vehicleCD):
        super(RetrainDialog, self).__init__()
        self._tankmen = [ self._itemsCache.items.getTankman(tankmanId) for tankmanId in tankmenIds ]
        self._vehicle = self._itemsCache.items.getItemByCD(vehicleCD)
        self._selectedTankmenIds = []
        self._priceListContent = RetrainPriceList(tankmenIds, vehicleCD)

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def isMassive(self):
        return len(self._tankmen) > 1

    def _getCallbacks(self):
        return (('inventory.1.compDescr', self._onVehiclesInventoryUpdate),)

    def _getEvents(self):
        return ((self._priceListContent.onPriceChange, self._onPriceChange), (self.viewModel.onTransferChanged, self._onTransferChanged))

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        self.setSubView(DefaultDialogPlaceHolders.TOP_RIGHT, MoneyBalance())
        if self.isMassive:
            self.setChildView(SinglePriceWidget.LAYOUT_DYN_ACCESSOR(), SinglePriceWidget(R.strings.dialogs.retrain.price(), ItemPrice(Money(gold=0, credits=0), Money(gold=0, credits=0)), CurrencySize.BIG))
        self.setChildView(self._priceListContent.layoutID, self._priceListContent)
        self.addButton(ConfirmButton(_LOC.submit(), isDisabled=True))
        self.addButton(CancelButton(_LOC.cancel()))
        self._updateViewModel()
        super(RetrainDialog, self)._onLoading(*args, **kwargs)

    def _onPriceChange(self, index=None):
        submitBtn = self.getButton(DialogButtons.SUBMIT)
        if submitBtn is not None:
            submitBtn.isDisabled = index is None
        if self.isMassive:
            with self.viewModel.transaction() as vm:
                self._updateTankmen(vm)
                self._updatePrice(vm)
        return

    def _onTransferChanged(self):
        self.viewModel.setIsTransferChecked(not self.viewModel.getIsTransferChecked())

    def _onVehiclesInventoryUpdate(self, diff):
        if self._vehicle.invID in diff and diff[self._vehicle.invID] is None:
            self.destroyWindow()
        return

    def _updateViewModel(self):
        with self.viewModel.transaction() as vm:
            self._fillViewModel(vm)

    def _fillViewModel(self, vm):
        vm.setIsPriceVisible(False)
        vm.setIsMassive(self.isMassive)
        if self._vehicle:
            vm.setIsTransferSelectionVisible(RetrainDialog.tmanCanTransferToVehicle(self._tankmen, self._vehicle))
            vm.setVehicleName(self._vehicle.descriptor.type.shortUserString)
            vm.setIsPremium(self._vehicle.isPremium)
        self._updateTankmen(vm)

    def _updateTankmen(self, vm):
        _, operationData, _ = self._priceListContent.selectedPriceData
        if not operationData:
            isUselessForTankmen = None
        else:
            _, _, isUselessForTankmen = operationData
        tankmenVL = vm.getTankmen()
        tankmenVL.clear()
        self._selectedTankmenIds = []
        for idx, tankman in enumerate(self._tankmen):
            if not isUselessForTankmen or not isUselessForTankmen[idx]:
                tankmanModel = RetrainTankmanModel()
                tankmanModel.setRole(tankman.role)
                tankmanModel.setIconName(tankman.getExtensionLessIconWithSkin())
                tankmanModel.setIsInSkin(tankman.isInSkin)
                tankmanModel.setIsFemale(tankman.isFemale)
                tankmenVL.addViewModel(tankmanModel)
                self._selectedTankmenIds.append(tankman.invID)

        tankmenVL.invalidate()
        return

    def _updatePrice(self, vm):
        price = self.getChildView(SinglePriceWidget.LAYOUT_DYN_ACCESSOR())
        itemPrice, _, _ = self._priceListContent.selectedPriceData
        vm.setIsPriceVisible(itemPrice and itemPrice != ITEM_PRICE_FREE)
        if price is None or itemPrice is None:
            return
        else:
            price.updatePrice(itemPrice * len(self._selectedTankmenIds))
            return

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            if not self._retrainTankmen():
                return
        super(RetrainDialog, self)._setResult(result)

    def _retrainTankmen(self):
        itemPrice, _, retrainKey = self._priceListContent.selectedPriceData
        operationPrice = itemPrice * len(self._selectedTankmenIds)
        purchaseMoneyState = getPurchaseMoneyState(operationPrice.price)
        if purchaseMoneyState is MoneyForPurchase.NOT_ENOUGH:
            showBuyGoldForCrew(operationPrice.price.gold)
            return False
        elif purchaseMoneyState is MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
            purchaseGold = getPurchaseGoldForCredits(operationPrice.price)
            event_dispatcher.showExchangeCurrencyWindowModal(currencyValue=purchaseGold)
            return False
        else:
            moveToBarracksTankman = None
            doActions = []
            for tankmanInvID in self._selectedTankmenIds:
                tankman = self._itemsCache.items.getTankman(tankmanInvID)
                if tankman is None:
                    continue
                doActions.append((factory.RETRAIN_TANKMAN,
                 tankmanInvID,
                 self._vehicle.intCD,
                 retrainKey))
                if tankman.vehicleInvID == self._vehicle.invID:
                    continue
                if self.viewModel.getIsTransferChecked() and RetrainDialog.tmanCanTransferToVehicle(self._tankmen, self._vehicle):
                    vehicleSlotIdx = RetrainDialog.getSlotForTmanInVeh(tankman, self._vehicle)
                    doActions.append((factory.EQUIP_TANKMAN,
                     tankmanInvID,
                     self._vehicle.invID,
                     vehicleSlotIdx))
                if tankman.isInTank and tankman.vehicleNativeDescr.type.compactDescr != self._vehicle.intCD:
                    moveToBarracksTankman = tankman

            groupSize = len(doActions)
            groupID = int(BigWorld.serverTime())
            while doActions:
                factory.doAction(*(doActions.pop(0) + (groupID, groupSize)))

            if moveToBarracksTankman:
                factory.doAction(factory.UNLOAD_TANKMAN, moveToBarracksTankman.vehicleInvID, moveToBarracksTankman.vehicleSlotIdx)
            return True

    @staticmethod
    def tmanCanTransferToVehicle(tankmen, vehicle):
        if vehicle and vehicle.isInInventory:
            for tankman in tankmen:
                if tankman and tankman.isInTank and tankman.vehicleInvID == vehicle.invID:
                    return False
                slotIdx = RetrainDialog.getSlotForTmanInVeh(tankman, vehicle)
                if slotIdx is None:
                    return False

            return True
        else:
            return False

    @staticmethod
    def getSlotForTmanInVeh(tankman, vehicle):
        if tankman and vehicle and vehicle.isInInventory:
            for idx, roles in enumerate(vehicle.descriptor.type.crewRoles):
                if tankman.descriptor.role == roles[0]:
                    slotIdx, vehTankman = vehicle.crew[idx]
                    if idx != slotIdx:
                        slotIdx, vehTankman = vehicle.crew[slotIdx]
                    if vehTankman is None:
                        return slotIdx

        return
