# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/dialogs/apply_player_card_dialog.py
from festivity.festival.constants import FestSyncDataKeys
from festivity.festival.item_info import FestivalItemInfo
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.currency_item_model import CurrencyItemModel
from gui.impl.gen.view_models.windows.simple_dialog_window_model import SimpleDialogWindowModel
from gui.impl.pub.dialog_window import DialogContent, DialogButtons, DialogWindow
from helpers import dependency
from skeletons.festival import IFestivalController
_UNION_DICT = {1: R.strings.festival.typeUnion.one(),
 2: R.strings.festival.typeUnion.two(),
 3: R.strings.festival.typeUnion.three()}

class ApplyPlayerCardDialogWindow(DialogWindow):
    __festController = dependency.descriptor(IFestivalController)
    __slots__ = ('__itemsInfo',)

    def __init__(self, itemIDs, parent=None):
        self.__itemsInfo = [ FestivalItemInfo(itemID) for itemID in itemIDs ]
        super(ApplyPlayerCardDialogWindow, self).__init__(bottomContent=DialogContent(R.views.lobby.festival.festival_components.FestivalBuyItemBottomContent(), CurrencyItemModel), content=DialogContent(R.views.common.dialog_view.simple_dialog_content.SimpleDialogContent(), SimpleDialogWindowModel), parent=parent, enableBlur=True, enableBlur3dScene=False)

    def _initialize(self):
        super(ApplyPlayerCardDialogWindow, self)._initialize()
        with self.viewModel.transaction() as model:
            self.__setTitle(model)
            self.__setContent()
            self.__setBottomContent(model)
            self._addButton(DialogButtons.PURCHASE, R.strings.festival.dialogs.applyItems.btnBuy(), isFocused=True)
            self._addButton(DialogButtons.CANCEL, R.strings.festival.dialogs.buyItems.btnCancel(), invalidateAll=True)
        self.__festController.onDataUpdated += self.__onUpdated

    def _finalize(self):
        self.__festController.onDataUpdated -= self.__onUpdated
        super(ApplyPlayerCardDialogWindow, self)._finalize()

    def __setBottomContent(self, model):
        bottomModel = model.getBottomContent().getViewModel()
        bottomModel.setValue(str(sum((item.getCost() for item in self.__itemsInfo))))

    def __setContent(self):
        contentModel = self.contentViewModel
        contentModel.setMessage(R.strings.festival.dialogs.applyItems.content())

    def __setTitle(self, model):
        model.setTitle(R.strings.festival.dialogs.applyItems.title())
        model.setIsTitleFmtArgsNamed(False)
        itemsName = []
        for itemInfo in self.__itemsInfo:
            itemsName.append(backport.text(R.strings.festival.dialogs.buyItems.type.dyn(itemInfo.getType())()))

        model.getTitleArgs().addString(backport.text(_UNION_DICT[len(itemsName)], *itemsName))
        model.getTitleArgs().invalidate()

    def __onUpdated(self, keys):
        if FestSyncDataKeys.TICKETS in keys:
            applyCost = sum((item.getCost() for item in self.__itemsInfo))
            isEnough = self.__festController.getTickets() >= applyCost
            self._setButtonEnabled(DialogButtons.PURCHASE, isEnough)
            self.bottomContentViewModel.setIsEnough(isEnough)
