# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/recruit_new_tankman_dialog.py
import typing
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui import SystemMessages
from gui.customization.shared import getPurchaseGoldForCredits, getPurchaseMoneyState, MoneyForPurchase
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.lobby.crew.dialogs.recruit_new_tankman_dialog_model import RecruitNewTankmanDialogModel
from gui.impl.lobby.crew.dialogs.price_cards_content.recruit_new_tankman_price_list import RecruitNewTankmanPriceList
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import event_dispatcher
from gui.shared.gui_items.Tankman import NO_TANKMAN
from gui.shared.gui_items.processors.tankman import TankmanRecruitAndEquip, TankmanRecruit
from gui.shared.utils import decorators
from gui.shop import showBuyGoldForCrew
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.gui_items.gui_item_economics import ItemPrice
_LOC = R.strings.dialogs.recruit

class RecruitNewTankmanDialog(BaseCrewDialogTemplateView):
    __slots__ = ('_vehicle', '_slotIdx', '_priceListContent', '_putInTank')
    LAYOUT_ID = R.views.lobby.crew.dialogs.RecruitNewTankmanDialog()
    VIEW_MODEL = RecruitNewTankmanDialogModel
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicleCD, slotIdx, putInTank):
        self._vehicle = self._itemsCache.items.getItemByCD(vehicleCD)
        self._slotIdx = slotIdx
        self._putInTank = putInTank
        self._priceListContent = RecruitNewTankmanPriceList()
        super(RecruitNewTankmanDialog, self).__init__()

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getCallbacks(self):
        return (('inventory.1.compDescr', self._onVehiclesInventoryUpdate),)

    def _getEvents(self):
        return ((self._priceListContent.onPriceChange, self._onPriceChange),)

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        self.setSubView(DefaultDialogPlaceHolders.TOP_RIGHT, MoneyBalance())
        self.setChildView(self._priceListContent.layoutID, self._priceListContent)
        self.addButton(ConfirmButton(_LOC.submit(), isDisabled=True))
        self.addButton(CancelButton(_LOC.cancel()))
        self._updateViewModel()
        super(RecruitNewTankmanDialog, self)._onLoading(*args, **kwargs)

    def _onPriceChange(self, index=None):
        submitBtn = self.getButton(DialogButtons.SUBMIT)
        if submitBtn is not None:
            submitBtn.isDisabled = index is None
        return

    def _onVehiclesInventoryUpdate(self, diff):
        if self._vehicle.invID in diff and diff[self._vehicle.invID] is None:
            self.destroyWindow()
        return

    def _updateViewModel(self):
        with self.viewModel.transaction() as vm:
            self._fillViewModel(vm)

    def _fillViewModel(self, vm):
        if self._vehicle:
            vm.setVehicleName(self._vehicle.descriptor.type.shortUserString)
            vm.setIsPremium(self._vehicle.isPremium)
            roles = self._vehicle.descriptor.type.crewRoles[self._slotIdx]
            vm.setRole(roles[0])

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            if not self._recruitTankman():
                return
        super(RecruitNewTankmanDialog, self)._setResult(result)

    def _recruitTankman(self):
        itemPrice, _, operationKey = self._priceListContent.selectedPriceData
        purchaseMoneyState = getPurchaseMoneyState(itemPrice.price)
        if purchaseMoneyState is MoneyForPurchase.NOT_ENOUGH:
            showBuyGoldForCrew(itemPrice.price.gold)
            return False
        if purchaseMoneyState is MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
            purchaseGold = getPurchaseGoldForCredits(itemPrice.price)
            event_dispatcher.showExchangeCurrencyWindowModal(currencyValue=purchaseGold)
            return False
        self._processRecruit(operationKey)
        return True

    def _processRecruit(self, operationKey):
        tankmen = self._vehicle.getTankmanIDBySlotIdx(self._slotIdx)
        if tankmen == NO_TANKMAN or self._putInTank:
            self._processBuyAndEquip(operationKey)
            return
        self._processBuy(operationKey)

    @decorators.adisp_process('recruiting')
    def _processBuy(self, operationKey):
        role = self._vehicle.descriptor.type.crewRoles[self._slotIdx][0]
        recruiter = TankmanRecruit(self._vehicle.nationID, self._vehicle.innationID, role, operationKey)
        _, msg, msgType, _, _, _ = yield recruiter.request()
        if msg:
            SystemMessages.pushI18nMessage(msg, type=msgType)

    @decorators.adisp_process('recruiting')
    def _processBuyAndEquip(self, operationKey):
        result = yield TankmanRecruitAndEquip(self._vehicle, self._slotIdx, operationKey).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            tankmen = self._vehicle.getTankmanIDBySlotIdx(self._slotIdx)
            if result.success and tankmen != NO_TANKMAN:
                SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.UNLOAD_TANKMAN_SUCCESS, type=SystemMessages.SM_TYPE.Information)
