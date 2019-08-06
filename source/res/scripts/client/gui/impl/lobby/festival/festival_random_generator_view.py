# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/festival_random_generator_view.py
import logging
from async import async, await
from BWUtil import AsyncReturn
from festivity.festival.constants import FestSyncDataKeys
from festivity.festival.processors import FestivalBuyRandomItemProcessor
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.festival.festival_random_generator_view_model import FestivalRandomGeneratorViewModel
from gui.impl.gen.view_models.windows.animated_dialog_window_model import AnimatedDialogWindowModel
from gui.impl.gen.view_models.views.lobby.festival.festival_random_renderer import FestivalRandomRenderer
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.lobby.festival.festival_helper import FestivalRandomGeneratorBalanceContent
from gui.impl.lobby.festival.festival_random_congratulation_view import FestivalRandomCongratulationWindow
from gui.impl.pub.dialog_window import DialogContent, DialogButtons
from gui.impl.pub.animated_dialog_window import AnimatedDialogWindow
from gui.shared.utils import decorators
from helpers import dependency
from items.components.festival_constants import FEST_ITEM_TYPE
from skeletons.festival import IFestivalController
from gui.impl.gen.view_models.ui_kit.currency_item_model import CurrencyItemModel
_logger = logging.getLogger(__name__)

@async
def showFestivalRandomGenerator(parent=None):
    dialog = FestivalRandomGeneratorWindow(parent)
    dialog.load()
    result = yield await(dialog.wait())
    dialog.destroy()
    raise AsyncReturn(result.data)


class FestivalRandomGeneratorView(DialogContent):
    __festController = dependency.descriptor(IFestivalController)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(FestivalRandomGeneratorView, self).__init__(R.views.lobby.festival.festival_random_generator_view.FestivalRandomGeneratorView(), FestivalRandomGeneratorViewModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(FestivalRandomGeneratorView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(FestivalRandomGeneratorView, self)._initialize()
        self.__festController.onDataUpdated += self.__onDataUpdated
        with self.viewModel.transaction() as tx:
            self.__updateRandomPacks(tx, init=True)

    def _finalize(self):
        self.__festController.onDataUpdated -= self.__onDataUpdated

    def __updateRandomPacks(self, model, init=False):
        currentRandomName = None
        canBuyAnyRandomPack = self.__festController.canBuyAnyRandomPack()
        needUpdateRandomName = init
        randomPacks = model.randomPacks.getItems()
        randomPacks.clear()
        for randomName in FEST_ITEM_TYPE.RANDOM:
            if randomName == FEST_ITEM_TYPE.ANY and not canBuyAnyRandomPack:
                if model.getCurrentRandomName() == randomName:
                    needUpdateRandomName = True
                continue
            randomModel = FestivalRandomRenderer()
            randomModel.setName(randomName)
            randomCost = self.__festController.getRandomCost(randomName)
            randomModel.setCost(randomCost)
            randomItems = self.__festController.getCommonItems(randomName)
            receivedCount = sum((1 for item in randomItems.itervalues() if item.isInInventory()))
            totalCount = len(randomItems)
            randomModel.setReceivedCount(receivedCount)
            randomModel.setTotalCount(totalCount)
            if currentRandomName is None and receivedCount < totalCount:
                currentRandomName = randomName
            if model.getCurrentRandomName() == randomName and receivedCount == totalCount:
                needUpdateRandomName = True
            randomPacks.addViewModel(randomModel)

        randomPacks.invalidate()
        if needUpdateRandomName and currentRandomName is not None:
            model.setCurrentRandomName(currentRandomName)
        return

    def __onDataUpdated(self, keys):
        with self.viewModel.transaction() as tx:
            if FestSyncDataKeys.RANDOM_PRICES in keys or FestSyncDataKeys.ITEMS in keys or FestSyncDataKeys.TICKETS in keys:
                self.__updateRandomPacks(tx)


class FestivalRandomGeneratorWindow(AnimatedDialogWindow):
    __festController = dependency.descriptor(IFestivalController)
    __slots__ = ('__needToShowTutorial', '__secondDialogVisible')

    def __init__(self, parent=None):
        super(FestivalRandomGeneratorWindow, self).__init__(content=FestivalRandomGeneratorView(), bottomContent=DialogContent(R.views.lobby.festival.festival_components.FestivalBuyItemBottomContent(), CurrencyItemModel), balanceContent=FestivalRandomGeneratorBalanceContent(), parent=parent, enableBlur=False)
        self.__needToShowTutorial = False
        self.__secondDialogVisible = False

    def _initialize(self):
        super(FestivalRandomGeneratorWindow, self)._initialize()
        self.viewModel.setPreset(DialogPresets.FESTIVAL_RANDOM_GENERATOR)
        self._addButton(DialogButtons.PURCHASE, R.strings.festival.dogtagView.create(), isFocused=True, soundDown=R.sounds.ev_fest_hangar_token_buy_random_item())
        self._addButton(DialogButtons.CANCEL, R.strings.festival.dialogs.buyItems.btnReturnToDogtag(), invalidateAll=True)
        self._getButton(DialogButtons.PURCHASE).setTooltipOnDisabled(R.strings.festival.tooltip.notEnoughMoney())
        self.viewModel.setTitle(R.strings.festival.dogtagView.randomElement())
        self.contentViewModel.onRandomNameChanged += self.__onRandomNameChanged
        self.__festController.onDataUpdated += self.__updateBalance
        self.__updateBalance()

    def _finalize(self):
        self.contentViewModel.onRandomNameChanged -= self.__onRandomNameChanged
        self.__festController.onDataUpdated -= self.__updateBalance
        super(FestivalRandomGeneratorWindow, self)._finalize()

    def _getResultData(self):
        return self.__needToShowTutorial

    def _onButtonClick(self, item):
        if self.__secondDialogVisible:
            return
        if item.getIsEnabled() and item.getName() == DialogButtons.PURCHASE:
            self.__disableControls()
            self.__secondDialogVisible = True
            self.__onBuyRandomPack()
            return
        if item.getName() == DialogButtons.CANCEL:
            self.processAnimatedAction(AnimatedDialogWindowModel.ACTION_CLOSE, item)
            return
        super(FestivalRandomGeneratorWindow, self)._onButtonClick(item)

    @decorators.process('festival/buyRandomFestivalItem')
    def __onBuyRandomPack(self):
        result = yield FestivalBuyRandomItemProcessor(self.contentViewModel.getCurrentRandomName()).request()
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.__showCongratsWindow(result.auxData)
        else:
            self.__secondDialogVisible = False
            self.__enableControls()

    @async
    def __showCongratsWindow(self, festItemID):
        randomName = self.contentViewModel.getCurrentRandomName()
        needToShowEarnTickets = self.__festController.needToShowWhereEarnTickets() and self.__festController.getTickets() < self.__festController.getRandomCost(randomName)
        dialog = FestivalRandomCongratulationWindow(festItemID, needToShowEarnTickets, self.parent, self)
        dialog.load()
        result = yield await(dialog.wait())
        dialog.destroy()
        self.__secondDialogVisible = False
        if result.result != DialogButtons.SUBMIT:
            self.__needToShowTutorial = needToShowEarnTickets
            self._onClosed()
            return
        self.__enableControls()
        self.__updateBalance()

    def __onRandomNameChanged(self, _=None):
        self.__updateBalance()

    def __updateBalance(self, _=None):
        randomName = self.contentViewModel.getCurrentRandomName()
        randomCost = self.__festController.getRandomCost(randomName)
        isEnough = randomCost <= self.__festController.getTickets()
        self.bottomContentViewModel.setValue(backport.getIntegralFormat(randomCost))
        self.bottomContentViewModel.setIsEnough(isEnough)
        self._getButton(DialogButtons.PURCHASE).setIsEnabled(isEnough and not self.__festController.isCommonItemCollected())
        self.viewModel.getBalanceContent().getViewModel().setValue(backport.getIntegralFormat(self.__festController.getTickets()))

    def __enableControls(self):
        randomName = self.contentViewModel.getCurrentRandomName()
        randomCost = self.__festController.getRandomCost(randomName)
        isEnough = randomCost <= self.__festController.getTickets()
        purchaseBtn = self._getButton(DialogButtons.PURCHASE)
        purchaseBtn.setIsEnabled(isEnough and not self.__festController.isCommonItemCollected())
        purchaseBtn.setDoSetFocus(False)
        purchaseBtn.setDoSetFocus(True)
        self._getButton(DialogButtons.CANCEL).setIsEnabled(True)

    def __disableControls(self):
        self._getButton(DialogButtons.PURCHASE).setIsEnabled(False)
        self._getButton(DialogButtons.CANCEL).setIsEnabled(False)
