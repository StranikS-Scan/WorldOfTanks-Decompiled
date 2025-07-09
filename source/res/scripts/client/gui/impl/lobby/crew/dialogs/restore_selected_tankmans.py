# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/restore_selected_tankmans.py
from gui.impl.gen.view_models.views.lobby.crew.dialogs.dismiss_or_restore_dialog_model import DismissOrRestoreDialogModel, DialogType
from gui.impl.gen import R
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from uilogging.crew.logging_constants import CrewDialogKeys
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.dialogs.sub_views.footer.simple_text_footer import SimpleTextFooter
from gui.impl.dialogs.sub_views.footer.single_price_footer import SinglePriceFooter
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencySize
from gui.game_control.restore_contoller import getTankmenRestoreInfo
from gui.shared.money import MONEY_UNDEFINED
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IRestoreController
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.customization.shared import getPurchaseGoldForCredits, getPurchaseMoneyState, MoneyForPurchase
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import event_dispatcher
from gui.shared.gui_items.items_actions import factory

class RestoreSelectedTankmans(BaseCrewDialogTemplateView):
    __slots__ = ('__tankmans', '__price')
    LAYOUT_ID = R.views.lobby.crew.dialogs.DismissOrRestoreTankmans()
    VIEW_MODEL = DismissOrRestoreDialogModel
    DIALOG_TYPE = DialogType.RESTORE
    _itemsCache = dependency.descriptor(IItemsCache)
    _restoreCtrl = dependency.descriptor(IRestoreController)

    def __init__(self, tankmans, **kwargs):
        super(RestoreSelectedTankmans, self).__init__(loggingKey=CrewDialogKeys.DISMISS_OR_RESTORE, **kwargs)
        self.__tankmans = self._setTankmans(tankmans)
        self.__price = self._setPrice()

    @property
    def viewModel(self):
        return super(RestoreSelectedTankmans, self).getViewModel()

    def _setTankmans(self, tankmanIDs):
        return [ t for t in (self._itemsCache.items.getTankman(ID) for ID in tankmanIDs) if t ]

    def _setPrice(self):
        total = MONEY_UNDEFINED
        for tman in self.__tankmans:
            price, _ = getTankmenRestoreInfo(tman)
            if price != MONEY_UNDEFINED:
                total += price

        return total

    def _onLoaded(self, *args, **kwargs):
        super(RestoreSelectedTankmans, self)._onLoaded(*args, **kwargs)
        g_clientUpdateManager.addMoneyCallback(self.__moneyChangeHandler)
        self._restoreCtrl.onTankmenBufferUpdated += self.__onTankmenBufferUpdated

    def _finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._restoreCtrl.onTankmenBufferUpdated -= self.__onTankmenBufferUpdated
        super(RestoreSelectedTankmans, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        if self.__price == MONEY_UNDEFINED:
            self.setSubView(Placeholder.FOOTER, SimpleTextFooter(R.strings.dialogs.restoreTankman.free()))
        else:
            self.setSubView(Placeholder.TOP_RIGHT, MoneyBalance())
            self.setSubView(Placeholder.FOOTER, SinglePriceFooter(R.strings.dialogs.restoreTankman.price(), ItemPrice(self.__price, self.__price), CurrencySize.BIG))
        state = getPurchaseMoneyState(self.__price)
        isBtnDisabled = state is MoneyForPurchase.NOT_ENOUGH
        self.addButton(ConfirmButton(label=R.strings.dialogs.dismissTankman.buttons.dyn(self.DIALOG_TYPE.value)(), isDisabled=isBtnDisabled))
        self.addButton(CancelButton())
        self._updateViewModel()
        super(RestoreSelectedTankmans, self)._onLoading(*args, **kwargs)

    def _updateViewModel(self):
        with self.viewModel.transaction() as vm:
            self._fillViewModel(vm)

    def _fillViewModel(self, vm):
        vm.setTankmans(len(self.__tankmans))
        vm.setDialogType(self.DIALOG_TYPE)

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT and not self._restoreTankmans():
            return
        super(RestoreSelectedTankmans, self)._setResult(result)

    def _restoreTankmans(self):
        if self.__price != MONEY_UNDEFINED:
            state = getPurchaseMoneyState(self.__price)
            if state is MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
                purchaseGold = getPurchaseGoldForCredits(self.__price)
                event_dispatcher.showExchangeCurrencyWindowModal(currencyValue=purchaseGold)
                return False
        factory.doAction(factory.RESTORE_TANKMANS, self.__tankmans)
        return True

    def __moneyChangeHandler(self, *_):
        isBtnDisabled = False
        if self.__price != MONEY_UNDEFINED:
            state = getPurchaseMoneyState(self.__price)
            isBtnDisabled = state is MoneyForPurchase.NOT_ENOUGH
        self.getButton(DialogButtons.SUBMIT).isDisabled = isBtnDisabled

    def __onTankmenBufferUpdated(self):
        self._updateViewModel()
