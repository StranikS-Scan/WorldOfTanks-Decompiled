# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/crew_member_role_change_dialog.py
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.customization.shared import getPurchaseMoneyState, MoneyForPurchase
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.footer.single_price_footer import SinglePriceFooter
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencySize
from gui.impl.gen.view_models.views.lobby.crew.dialogs.role_change_dialog_model import RoleChangeDialogModel
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.money import Money
from gui.shop import showBuyGoldForCrew
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from uilogging.crew.logging_constants import CrewDialogKeys, CrewRoleChangeDialogAdditionalInfo
_LOC = R.strings.dialogs.crewMemberRoleChange

class CrewMemberRoleChangeDialog(BaseCrewDialogTemplateView):
    __slots__ = ('_tankman', '_vehicleCurrent', '_vehicleNew', '_currentSpecializationVehicle', '_role', '_isTankChange', '_isSpecializationChange', '_priceSubView')
    LAYOUT_ID = R.views.lobby.crew.dialogs.RoleChangeDialog()
    VIEW_MODEL = RoleChangeDialogModel
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, tankmanId, vehicleCurrent, vehicleNew, role, **kwargs):
        self._tankman = self._itemsCache.items.getTankman(tankmanId)
        self._vehicleCurrent = vehicleCurrent
        self._vehicleNew = vehicleNew
        self._role = role
        self._isTankChange = self._vehicleCurrent and self._vehicleNew and self._vehicleCurrent.invID != self._vehicleNew.invID
        self._isSpecializationChange = self._vehicleCurrent and self._vehicleCurrent.intCD != self._tankman.vehicleNativeDescr.type.compactDescr
        self._currentSpecializationVehicle = self._itemsCache.items.getItemByCD(self._tankman.vehicleNativeDescr.type.compactDescr) if self._isSpecializationChange else None
        loggingAdditionalInfo = CrewRoleChangeDialogAdditionalInfo.ROLE_AND_TANK if self._isTankChange else CrewRoleChangeDialogAdditionalInfo.ONLY_ROLE
        super(CrewMemberRoleChangeDialog, self).__init__(loggingAdditionalInfo=loggingAdditionalInfo, loggingKey=CrewDialogKeys.ROLE_CHANGE, **kwargs)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getItemPrice(self):
        return ItemPrice(Money(gold=self._itemsCache.items.shop.changeRoleCost), Money(gold=self._itemsCache.items.shop.defaults.changeRoleCost))

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        self.setSubView(Placeholder.TOP_RIGHT, MoneyBalance())
        self._priceSubView = SinglePriceFooter(_LOC.price(), self._getItemPrice(), CurrencySize.BIG)
        self.setSubView(Placeholder.FOOTER, self._priceSubView)
        self.addButton(ConfirmButton(_LOC.change(), buttonType=ButtonType.MAIN, isDisabled=False))
        self.addButton(CancelButton())
        self._updateViewModel()
        super(CrewMemberRoleChangeDialog, self)._onLoading(*args, **kwargs)

    def _getEvents(self):
        return ((self._itemsCache.onSyncCompleted, self._onCacheResync),)

    def _onCacheResync(self, reason, _):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self._updateViewModel()
            self._priceSubView.updatePrice(self._getItemPrice())

    def _updateViewModel(self):
        with self.viewModel.transaction() as vm:
            self._fillViewModel(vm)

    def _fillViewModel(self, vm):
        self._setVehiclesInfo(vm)
        vm.setIconName(self._tankman.getExtensionLessIconWithSkin())
        vm.setIsSkin(self._tankman.isInSkin)
        vm.setCurrentRole(self._tankman.role)
        vm.setNewRole(self._role)
        vm.setIsTankChange(self._isTankChange)
        vm.setIsSpecializationChange(self._isSpecializationChange)

    def _setVehiclesInfo(self, vm):
        if self._vehicleCurrent:
            vm.currentVehicle.setName(self._vehicleCurrent.descriptor.type.shortUserString)
            vm.currentVehicle.setTier(self._vehicleCurrent.level)
            vm.currentVehicle.setIsPremium(self._vehicleCurrent.isPremium)
            vm.currentVehicle.setType(self._vehicleCurrent.type)
        if self._vehicleNew:
            vm.newVehicle.setName(self._vehicleNew.descriptor.type.shortUserString)
            vm.newVehicle.setTier(self._vehicleNew.level)
            vm.newVehicle.setIsPremium(self._vehicleNew.isElite or self._vehicleNew.isPremium)
            vm.newVehicle.setType(self._vehicleNew.type)
        if self._currentSpecializationVehicle:
            vm.currentSpecializationVehicle.setName(self._currentSpecializationVehicle.descriptor.type.shortUserString)
            vm.currentSpecializationVehicle.setTier(self._currentSpecializationVehicle.level)
            vm.currentSpecializationVehicle.setIsPremium(self._currentSpecializationVehicle.isElite or self._currentSpecializationVehicle.isPremium)
            vm.currentSpecializationVehicle.setType(self._currentSpecializationVehicle.type)

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            changeRoleCost = Money(gold=self._itemsCache.items.shop.changeRoleCost)
            purchaseMoneyState = getPurchaseMoneyState(changeRoleCost)
            if purchaseMoneyState is MoneyForPurchase.NOT_ENOUGH:
                showBuyGoldForCrew(changeRoleCost.gold)
                return False
        super(CrewMemberRoleChangeDialog, self)._setResult(result)
