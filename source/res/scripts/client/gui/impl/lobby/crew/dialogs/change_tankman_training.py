# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/change_tankman_training.py
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.customization.shared import getPurchaseGoldForCredits, getPurchaseMoneyState, MoneyForPurchase
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen.resources import R
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.lobby.crew.dialogs.price_cards_content.recruit_new_tankman_price_list import RecruitNewTankmanPriceList
from gui.shared import event_dispatcher
from gui.shop import showBuyGoldForCrew
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_LOC = R.strings.dialogs.tankmanRetraining

class ChangeTankmanTrainingDialog(BaseCrewDialogTemplateView):
    __slots__ = ('_priceListContent',)
    LAYOUT_ID = R.views.lobby.crew.dialogs.ChangeTankmanTrainingDialog()
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self._priceListContent = RecruitNewTankmanPriceList()
        super(ChangeTankmanTrainingDialog, self).__init__()

    def _getEvents(self):
        return ((self._priceListContent.onPriceChange, self._onPriceChange),)

    def _onLoading(self, *args, **kwargs):
        self.setSubView(DefaultDialogPlaceHolders.TOP_RIGHT, MoneyBalance())
        self.setChildView(self._priceListContent.layoutID, self._priceListContent)
        self.addButton(ConfirmButton(_LOC.submit(), isDisabled=True))
        self.addButton(CancelButton(_LOC.cancel()))
        super(ChangeTankmanTrainingDialog, self)._onLoading(*args, **kwargs)

    def _getAdditionalData(self):
        itemPrice, _, operationKey = self._priceListContent.selectedPriceData
        return (itemPrice, operationKey) if self._retrainTankmen() else None

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            if not self._retrainTankmen():
                return
        elif result == DialogButtons.CANCEL:
            self._priceListContent._priceData = []
        super(ChangeTankmanTrainingDialog, self)._setResult(result)

    def _retrainTankmen(self):
        itemPrice, _, _ = self._priceListContent.selectedPriceData
        if itemPrice is None:
            return False
        purchaseMoneyState = getPurchaseMoneyState(itemPrice.price)
        if purchaseMoneyState is MoneyForPurchase.NOT_ENOUGH:
            showBuyGoldForCrew(itemPrice.price.gold)
            return False
        elif purchaseMoneyState is MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
            purchaseGold = getPurchaseGoldForCredits(itemPrice.price)
            event_dispatcher.showExchangeCurrencyWindowModal(currencyValue=purchaseGold)
            return False
        else:
            return True

    def _onPriceChange(self, index=None):
        submitBtn = self.getButton(DialogButtons.SUBMIT)
        if submitBtn is not None:
            submitBtn.isDisabled = index is None
        return
