# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/dialogs/buy_items_dialog.py
from festivity.festival.constants import FestSyncDataKeys
from festivity.festival.item_info import FestivalItemInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.festival.base_festival_item_renderer import BaseFestivalItemRenderer
from gui.impl.gen.view_models.ui_kit.currency_item_model import CurrencyItemModel
from gui.impl.pub.dialog_window import DialogContent, DialogButtons, DialogWindow
from helpers import dependency
from skeletons.festival import IFestivalController

class BuyItemsDialogWindow(DialogWindow):
    __festController = dependency.descriptor(IFestivalController)
    __slots__ = ('__itemInfo',)

    def __init__(self, itemID, parent=None):
        self.__itemInfo = FestivalItemInfo(itemID)
        super(BuyItemsDialogWindow, self).__init__(bottomContent=DialogContent(R.views.lobby.festival.festival_components.FestivalBuyItemBottomContent(), CurrencyItemModel), content=DialogContent(R.views.lobby.festival.festival_components.FestivalBuyItemMainContent(), BaseFestivalItemRenderer), parent=parent, enableBlur=True, enableBlur3dScene=False)

    def _initialize(self):
        super(BuyItemsDialogWindow, self)._initialize()
        with self.viewModel.transaction() as model:
            self.__setMainContent()
            self.__setBottomContent(model)
            self._addButton(DialogButtons.PURCHASE, R.strings.festival.dialogs.buyItems.btnBuy(), isFocused=True, soundDown=R.sounds.ev_fest_hangar_token_buy_button())
            self._addButton(DialogButtons.CANCEL, R.strings.festival.dialogs.buyItems.btnCancel(), invalidateAll=True)
        self.__festController.onDataUpdated += self.__onUpdated

    def _finalize(self):
        self.__festController.onDataUpdated -= self.__onUpdated
        super(BuyItemsDialogWindow, self)._finalize()

    def __setBottomContent(self, model):
        bottomContent = model.getBottomContent().getViewModel()
        bottomContent.setValue(str(self.__itemInfo.getCost()))

    def __setMainContent(self):
        with self.contentViewModel.transaction() as tx:
            tx.setId(self.__itemInfo.getID())
            tx.setResId(self.__itemInfo.getResId())
            tx.setType(self.__itemInfo.getType())

    def __onUpdated(self, keys):
        if FestSyncDataKeys.TICKETS in keys:
            isEnough = self.__festController.getTickets() >= self.__itemInfo.getCost()
            self._setButtonEnabled(DialogButtons.PURCHASE, isEnough)
            self.bottomContentViewModel.setIsEnough(isEnough)
