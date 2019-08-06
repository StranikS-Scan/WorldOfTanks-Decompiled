# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/festival_random_congratulation_view.py
from festivity.festival.item_info import FestivalItemInfo
from frameworks.wulf import ViewModel
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.festival.festival_random_congratulation_view_model import FestivalRandomCongratulationViewModel
from gui.impl.gen.view_models.windows.animated_dialog_window_model import AnimatedDialogWindowModel
from gui.impl.lobby.festival.festival_helper import FestivalRandomGeneratorBalanceContent
from gui.impl.lobby.festival.festival_where_earn_tickets_view import showFestivalWhereEarnTickets
from gui.impl.pub.dialog_window import DialogContent, DialogButtons
from gui.impl.pub.animated_dialog_window import AnimatedDialogWindow
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from helpers import dependency
from items.components.festival_constants import FEST_ITEM_TYPE
from skeletons.festival import IFestivalController
from async import await, async

class FestivalRandomCongratulationView(DialogContent):
    __slots__ = ()

    def __init__(self, festItemID):
        super(FestivalRandomCongratulationView, self).__init__(R.views.lobby.festival.festival_random_congratulation_view.FestivalRandomCongratulationView(), FestivalRandomCongratulationViewModel, festItemID)

    @property
    def viewModel(self):
        return super(FestivalRandomCongratulationView, self).getViewModel()

    def _initialize(self, festItemID):
        super(FestivalRandomCongratulationView, self)._initialize()
        with self.viewModel.transaction() as tx:
            festItem = FestivalItemInfo(festItemID)
            tx.setId(festItem.getID())
            tx.setName(festItem.getResId())
            tx.setType(festItem.getType())


class FestivalRandomCongratulationWindow(AnimatedDialogWindow):
    _festController = dependency.descriptor(IFestivalController)
    __slots__ = ('__needToShowEarnTickets',)

    def __init__(self, festItemID, needToShowEarnTickets=False, parent=None, parentDialogWindow=None):
        super(FestivalRandomCongratulationWindow, self).__init__(content=FestivalRandomCongratulationView(festItemID), parent=parent, parentDialogWindow=parentDialogWindow, enableBlur=False, balanceContent=FestivalRandomGeneratorBalanceContent())
        self.__needToShowEarnTickets = needToShowEarnTickets

    def _initialize(self):
        super(FestivalRandomCongratulationWindow, self)._initialize()
        self._festController.onDataUpdated += self.__updateBalance
        self.__updateBalance()
        isEnabled = any((not item.isInInventory() for item in self._festController.getCommonItems(FEST_ITEM_TYPE.ANY).itervalues())) and self._festController.getTickets() >= self._festController.getRandomCost(FEST_ITEM_TYPE.ANY)
        if not self.__needToShowEarnTickets:
            self.viewModel.setPreset(DialogPresets.FESTIVAL_RANDOM_CONGRAT)
            self._addButton(DialogButtons.SUBMIT, R.strings.festival.dogtagView.again(), isFocused=True, isEnabled=isEnabled)
            self._getButton(DialogButtons.SUBMIT).setTooltipOnDisabled(R.strings.festival.tooltip.notEnoughMoney())
            self._addButton(DialogButtons.CANCEL, R.strings.festival.dialogs.buyItems.btnReturnToDogtag(), invalidateAll=True)
        else:
            self.viewModel.setPreset(DialogPresets.FESTIVAL_RANDOM_CONGRAT)
            self._setBottomContent(DialogContent(R.views.lobby.festival.festival_random_congratulation_bottom.FestivalRandomCongratulationBottom(), ViewModel))
            self._addButton(DialogButtons.SUBMIT, R.strings.festival.dogtagView.whereEarnTickets(), isFocused=True, isEnabled=True, invalidateAll=True)

    def _finalize(self):
        self._festController.onDataUpdated -= self.__updateBalance
        super(FestivalRandomCongratulationWindow, self)._finalize()

    def _onButtonClick(self, item):
        if item.getIsEnabled() and item.getName() == DialogButtons.SUBMIT:
            if self.__needToShowEarnTickets:
                self.__showWhereEarnTickets()
            else:
                self.processAnimatedAction(AnimatedDialogWindowModel.ACTION_RETURN, item)
            return
        if item.getName() == DialogButtons.CANCEL:
            self.processAnimatedAction(AnimatedDialogWindowModel.ACTION_CLOSE, item)
            return
        super(FestivalRandomCongratulationWindow, self)._onButtonClick(item)

    @async
    def __showWhereEarnTickets(self):
        result = yield await(showFestivalWhereEarnTickets(self))
        if result:
            self._onClosed()

    def __updateBalance(self, _=None):
        self.viewModel.getBalanceContent().getViewModel().setValue(backport.getIntegralFormat(self._festController.getTickets()))
