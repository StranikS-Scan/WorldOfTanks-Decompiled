# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/base/submodels/has_boxes.py
from typing import TYPE_CHECKING
from account_helpers.AccountSettings import LOOT_BOXES_SELECTED_BOX
from gui.impl.gen.view_models.views.lobby.lootbox_system.main_view_model import SubViewID
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.has_boxes_view_model import HasBoxesViewModel
from gui.impl.lobby.lootbox_system.base.common import SubViewImpl
from gui.impl.lobby.lootbox_system.base.submodels.common import updateAnimationState, updateBoxesInfoModel
from gui.impl.lobby.lootbox_system.base.submodels.statistics import Statistics
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.lootbox_system.base.common import ViewID, Views
from gui.lootbox_system.base.decorators import createTooltipContentDecorator
from gui.lootbox_system.base.utils import getOpeningOptions, getPreferredBox, openBoxes, isShopVisible
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import ILootBoxSystemController
if TYPE_CHECKING:
    from typing import Dict, List
    from gui.server_events.bonuses import SimpleBonus

class HasBoxes(SubViewImpl):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)
    __options = {}

    def __init__(self, viewModel, parentView):
        super(HasBoxes, self).__init__(viewModel, parentView)
        self.__stats = Statistics()
        self.__isResetCompleted = False
        self.__boxOption = None
        self.__eventName = ''
        return

    @property
    def boxCategory(self):
        return self.__boxOption

    @property
    def viewModel(self):
        return self.getViewModel()

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(HasBoxes, self).createToolTip(event)

    def initialize(self, *args, **kwargs):
        super(HasBoxes, self).initialize(*args, **kwargs)
        self.__eventName = kwargs.get('eventName', '')
        self.__boxOption = self.__lootBoxes.getSetting(self.__eventName, LOOT_BOXES_SELECTED_BOX)
        for event in self.__lootBoxes.getActiveEvents():
            self.__options.setdefault(event, {})

        with self.viewModel.transaction() as vmTx:
            self.__updateData(model=vmTx)
            self.__updateCounters(model=vmTx)
            self.__updateAnimationState(model=vmTx)
            self.__updateOpeningOptions(model=vmTx)
            self.__updateSelectedOpeningOption(model=vmTx)

    def finalize(self):
        self.__lootBoxes.setSetting(self.__eventName, LOOT_BOXES_SELECTED_BOX, self.__boxOption)
        super(HasBoxes, self).finalize()

    def _getEvents(self):
        return ((self.viewModel.onInfoOpen, self.__showInfo),
         (self.viewModel.onBoxesOpen, self.__openBoxes),
         (self.viewModel.onBuyBoxes, self.__buyBoxes),
         (self.viewModel.onAnimationStateChanged, self.__updateAnimationState),
         (self.viewModel.onOpeningOptionChanged, self.__updateSelectedOpeningOption),
         (self.viewModel.onBoxOptionChanged, self.__updateSelectedBoxOption),
         (self.viewModel.onResetError, self.__resetError),
         (self.viewModel.onClose, self.destroy),
         (self.viewModel.statistics.onReset, self.__onStatisticsReset),
         (self.viewModel.statistics.onUpdateResetState, self.__onUpdateResetState),
         (self.__lootBoxes.onBoxesCountChanged, self.__updateCounters),
         (self.__lootBoxes.onStatusChanged, self.__onStatusChanged),
         (self.__lootBoxes.onBoxesUpdated, self.__updateStatistics),
         (self.__lootBoxes.onBoxesAvailabilityChanged, self.__onStatusChanged))

    def _getListeners(self):
        return ((events.LootBoxSystemEvent.ON_STATISTICS_RESET, self.__onUpdateReset, EVENT_BUS_SCOPE.LOBBY), (events.LootBoxSystemEvent.OPENING_ERROR, self.__onErrorBack, EVENT_BUS_SCOPE.LOBBY))

    @replaceNoneKwargsModel
    def __updateData(self, model=None):
        model.setEventName(self.__eventName)
        model.setIsShopVisible(isShopVisible(self.__eventName))
        updateBoxesInfoModel(self.__eventName, model.getBoxesInfo())
        self.__updateSelectedBoxOption(model=model)
        self.__updateStatistics(model=model)

    @replaceNoneKwargsModel
    def __updateCounters(self, model=None):
        updateBoxesInfoModel(self.__eventName, model.getBoxesInfo())

    @replaceNoneKwargsModel
    def __updateAnimationState(self, ctx=None, model=None):
        updateAnimationState(model, ctx, self.__eventName)

    @replaceNoneKwargsModel
    def __updateSelectedBoxOption(self, ctx=None, model=None):
        boxOption = (ctx or {}).get('boxOption')
        if boxOption is None:
            if self.__boxOption is None or self.__boxOption not in self.__getBoxOptions() or not self.__getBoxOptions()[self.__boxOption].getInventoryCount():
                self.__boxOption = self.__getDefaultBoxOption()
        else:
            self.__boxOption = boxOption
        model.setSelectedBoxOption(self.__boxOption)
        inventoryCount = self.__getBoxOptions()[self.__boxOption].getInventoryCount()
        selectedCount = getOpeningOptions(self.__eventName)[self.__options[self.__eventName].get('openingOption', 0)]
        if inventoryCount < selectedCount:
            self.__resetSelectedOpeningOption(model=model)
        return

    @replaceNoneKwargsModel
    def __updateOpeningOptions(self, model=None):
        openingOptions = model.getOpeningOptions()
        openingOptions.clear()
        for o in getOpeningOptions(self.__eventName):
            openingOptions.addNumber(o)

        openingOptions.invalidate()

    @replaceNoneKwargsModel
    def __updateSelectedOpeningOption(self, ctx=None, model=None):
        openingOption = (ctx or {}).get('openingOption')
        if openingOption is None:
            openingOption = self.__options.get('openingOption', 0)
        else:
            self.__options['openingOption'] = int(openingOption)
        model.setSelectedOpeningOption(openingOption)
        return

    @replaceNoneKwargsModel
    def __resetSelectedOpeningOption(self, model=None):
        self.__options[self.__eventName]['openingOption'] = 0
        model.setSelectedOpeningOption(self.__options[self.__eventName]['openingOption'])

    @replaceNoneKwargsModel
    def __resetError(self, model=None):
        model.setIsError(False)

    @replaceNoneKwargsModel
    def __updateStatistics(self, model=None):
        useStats = self.__lootBoxes.useStats(self.__eventName)
        model.setUseStats(useStats)
        if useStats:
            self.__stats.update(model.statistics, findFirst(lambda b: b.getCategory() == self.boxCategory, self.__lootBoxes.getActiveBoxes(self.__eventName)).getID(), self.__isResetCompleted, self.__eventName)

    def __getDefaultBoxOption(self):
        return getPreferredBox(self.__eventName).getCategory()

    def __getBoxOptions(self):
        return {box.getCategory():box for box in self.__lootBoxes.getActiveBoxes(self.__eventName)}

    def __showInfo(self):
        Views.load(ViewID.INFO, eventName=self.__eventName)

    @replaceNoneKwargsModel
    def __openBoxes(self, ctx, model=None):
        count = int(ctx.get('count'))

        def processResult(bonuses):
            self.parentView.switchToSubView(isBackground=True, eventName=self.__eventName)
            Views.load(ViewID.MAIN, subViewID=SubViewID.MULTIPLE_BOXES_REWARDS if count > 1 else SubViewID.SINGLE_BOX_REWARDS, eventName=self.__eventName, category=self.boxCategory, count=count, bonuses=bonuses)

        model.setIsError(False)
        openBoxes(self.__eventName, self.boxCategory, count, processResult)

    @replaceNoneKwargsModel
    def __onErrorBack(self, _, model=None):
        model.setIsError(True)

    def __buyBoxes(self):
        Views.load(ViewID.SHOP, eventName=self.__eventName)

    def __onUpdateResetState(self):
        self.__isResetCompleted = False
        self.viewModel.statistics.setIsResetCompleted(self.__isResetCompleted)

    def __onUpdateReset(self, event):
        self.__isResetCompleted = event.ctx['isCompleted']

    def __onStatisticsReset(self):
        self.__stats.reset()

    def __onStatusChanged(self):
        if self.__lootBoxes.isAvailable(self.__eventName) and self.__lootBoxes.getActiveBoxes(self.__eventName):
            if not self.__lootBoxes.getBoxesCount(self.__eventName):
                Views.load(ViewID.MAIN, subViewID=SubViewID.NO_BOXES, eventName=self.__eventName)
            else:
                self.__updateData()
                self.__updateStatistics()
