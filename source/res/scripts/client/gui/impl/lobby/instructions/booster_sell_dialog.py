# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/instructions/booster_sell_dialog.py
from gui import SystemMessages
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import MAX_ITEMS_FOR_OPERATION
from gui.impl.gen.view_models.views.lobby.common.buy_sell_items_dialog_model import BuySellItemsDialogModel
from gui.impl.lobby.common.buy_sell_item_base_dialog import DialogBuySellItemBaseView
from gui.impl.gen import R
from frameworks.wulf import ViewFlags, ViewSettings
from gui.shared.gui_items.processors.module import ModuleSeller
from adisp import process

class BoosterSellWindowView(DialogBuySellItemBaseView):

    def __init__(self, typeCompDescr, layoutID=R.views.lobby.instructions.SellWindow()):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.TOP_WINDOW_VIEW
        settings.model = BuySellItemsDialogModel()
        super(BoosterSellWindowView, self).__init__(settings, typeCompDescr)

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def isBuying(self):
        return False

    def _setBaseParams(self, model):
        itemCount = self._item.inventoryCount
        model.setTitleBody(R.strings.menu.boosterSellWindow.title())
        self._setTitleArgs(model.getTitleArgs(), (('name', R.strings.artefacts.dyn(self._item.name).name()),))
        model.setItemMaxCount(min(itemCount, MAX_ITEMS_FOR_OPERATION))
        model.setItemCount(itemCount)
        model.setSpecialType(self._item.getOverlayType())
        super(BoosterSellWindowView, self)._setBaseParams(model)

    @process
    def _onAcceptClicked(self):
        result = yield ModuleSeller(self._item, min(self.viewModel.getItemCount(), MAX_ITEMS_FOR_OPERATION)).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        super(BoosterSellWindowView, self)._onAcceptClicked()
