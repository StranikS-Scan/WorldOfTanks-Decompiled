# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/restore_tankman_dialog.py
import BigWorld
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.customization.shared import getPurchaseGoldForCredits, getPurchaseMoneyState, MoneyForPurchase
from gui.game_control.restore_contoller import getTankmenRestoreInfo
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.sub_views.footer.simple_text_footer import SimpleTextFooter
from gui.impl.dialogs.sub_views.footer.single_price_footer import SinglePriceFooter
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencySize
from gui.impl.gen.view_models.views.lobby.crew.dialogs.restore_tankman_dialog_model import RestoreTankmanDialogModel
from gui.impl.lobby.crew.crew_helpers.model_setters import setTankmanModel, setTmanSkillsModel
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import event_dispatcher
from gui.shared.gui_items.Tankman import Tankman, NO_SLOT
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.items_actions import factory
from gui.shared.money import MONEY_UNDEFINED
from helpers import dependency
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.shared import IItemsCache
from uilogging.crew.logging_constants import CrewDialogKeys

class RestoreTankmanDialog(BaseCrewDialogTemplateView):
    __slots__ = ('_tankman', '_vehicle', '_vehicleSlotIdx')
    LAYOUT_ID = R.views.lobby.crew.dialogs.RestoreTankmanDialog()
    VIEW_MODEL = RestoreTankmanDialogModel
    _itemsCache = dependency.descriptor(IItemsCache)
    _restoreCtrl = dependency.descriptor(IRestoreController)

    def __init__(self, tankmanId, vehicleId, slotIdx, **kwargs):
        super(RestoreTankmanDialog, self).__init__(loggingKey=CrewDialogKeys.RESTORE_TANKMAN, **kwargs)
        self._tankman = self._itemsCache.items.getTankman(tankmanId)
        self._vehicle = self._itemsCache.items.getVehicle(vehicleId)
        self._vehicleSlotIdx = slotIdx

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def restoreInfo(self):
        return getTankmenRestoreInfo(self._tankman)

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        isBtnDisabled = False
        price, _ = self.restoreInfo
        if price == MONEY_UNDEFINED:
            self.setSubView(Placeholder.FOOTER, SimpleTextFooter(R.strings.dialogs.restoreTankman.free()))
        else:
            self.setSubView(Placeholder.TOP_RIGHT, MoneyBalance())
            self.setSubView(Placeholder.FOOTER, SinglePriceFooter(R.strings.dialogs.restoreTankman.price(), ItemPrice(price, price), CurrencySize.BIG))
            state = getPurchaseMoneyState(price)
            isBtnDisabled = state is MoneyForPurchase.NOT_ENOUGH
        self.addButton(ConfirmButton(R.strings.dialogs.restoreTankman.buttons.recover(), isDisabled=isBtnDisabled))
        self.addButton(CancelButton())
        self._updateViewModel()
        super(RestoreTankmanDialog, self)._onLoading(*args, **kwargs)

    def _onLoaded(self, *args, **kwargs):
        super(RestoreTankmanDialog, self)._onLoaded(*args, **kwargs)
        g_clientUpdateManager.addMoneyCallback(self.__moneyChangeHandler)
        self._restoreCtrl.onTankmenBufferUpdated += self.__onTankmenBufferUpdated

    def _finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._restoreCtrl.onTankmenBufferUpdated -= self.__onTankmenBufferUpdated
        super(RestoreTankmanDialog, self)._finalize()

    def _updateViewModel(self):
        with self.viewModel.transaction() as vm:
            self._fillViewModel(vm)

    def _fillViewModel(self, vm):
        _, time = self.restoreInfo
        if time <= 0:
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.RESTORE_TANKMAN_ERROR, tankman=self._tankman.fullUserName, type=SystemMessages.SM_TYPE.Error)
            self._setResult(DialogButtons.CANCEL)
        tm = vm.tankman
        setTankmanModel(tm, self._tankman, tmanNativeVeh=self._itemsCache.items.getItemByCD(self._tankman.vehicleNativeDescr.type.compactDescr))
        setTmanSkillsModel(tm.getSkills(), self._tankman)
        tm.setTimeToDismiss(time)

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            if not self._restoreTankman():
                return
        super(RestoreTankmanDialog, self)._setResult(result)

    def _restoreTankman(self):
        price, _ = self.restoreInfo
        if price != MONEY_UNDEFINED:
            state = getPurchaseMoneyState(price)
            if state is MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
                purchaseGold = getPurchaseGoldForCredits(price)
                event_dispatcher.showExchangeCurrencyWindowModal(currencyValue=purchaseGold)
                return False
        self.__restoreTankman()
        return True

    def __restoreTankman(self):
        isTransfer = self._vehicle and self._vehicleSlotIdx != NO_SLOT
        berthsNeeded = 0 if isTransfer else 1
        doActions = [(factory.RESTORE_TANKMAN, self._tankman.invID, berthsNeeded)]
        if isTransfer:
            requiredRole = self._vehicle.descriptor.type.crewRoles[self._vehicleSlotIdx][0]
            if requiredRole != self._tankman.role:
                dialogs.showRetrainSingleDialog(self._tankman.invID, self._vehicle.intCD, targetSlotIdx=self._vehicleSlotIdx, beforeActions=doActions)
                return
            doActions.append((factory.EQUIP_TANKMAN,
             self._tankman.invID,
             self._vehicle.invID,
             self._vehicleSlotIdx))
        BigWorld.player().doActions(doActions)

    def __onTankmenBufferUpdated(self):
        self._updateViewModel()

    def __moneyChangeHandler(self, *_):
        isBtnDisabled = False
        price, _ = self.restoreInfo
        if price != MONEY_UNDEFINED:
            state = getPurchaseMoneyState(price)
            isBtnDisabled = state is MoneyForPurchase.NOT_ENOUGH
        self.getButton(DialogButtons.SUBMIT).isDisabled = isBtnDisabled
