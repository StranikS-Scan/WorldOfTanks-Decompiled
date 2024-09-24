# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/submodels/has_boxes.py
from typing import TYPE_CHECKING
from gui.impl.gen.view_models.views.lobby.lootbox_system.main_view_model import SubViewID
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.has_boxes_view_model import HasBoxesViewModel
from gui.impl.lobby.lootbox_system.common import SubViewImpl
from gui.impl.lobby.lootbox_system.submodels.common import updateAnimationState, updateBoxesInfoModel
from gui.impl.lobby.lootbox_system.submodels.statistics import Statistics
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.lootbox_system.common import ViewID, Views
from gui.lootbox_system.decorators import createTooltipContentDecorator
from gui.lootbox_system.utils import areUsedExternalTransitions, getPreferredBox, openBoxes
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency
from shared_utils import findFirst, first
from skeletons.gui.game_control import ILootBoxSystemController
if TYPE_CHECKING:
    from typing import Dict, List
    from gui.server_events.bonuses import SimpleBonus
_OPENING_OPTIONS = (1, 5)

class HasBoxes(SubViewImpl):
    __slots__ = ('__stats', '__isResetCompleted')
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)
    __options = {}

    def __init__(self, viewModel, parentView):
        super(HasBoxes, self).__init__(viewModel, parentView)
        self.__stats = Statistics()
        self.__isResetCompleted = False

    @property
    def boxCategory(self):
        return self.__getBoxOptions().get(self.__options['boxOption']).getCategory()

    @property
    def viewModel(self):
        return self.getViewModel()

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(HasBoxes, self).createToolTip(event)

    def initialize(self, *args, **kwargs):
        super(HasBoxes, self).initialize(*args, **kwargs)
        with self.viewModel.transaction() as vmTx:
            self.__updateData(model=vmTx)
            self.__updateCounters(model=vmTx)
            self.__updateAnimationState(model=vmTx)
            self.__updateOpeningOptions(model=vmTx)
            self.__updateSelectedOpeningOption(model=vmTx)
            self.__updateSelectedBoxOption(model=vmTx)
            self.__updateStatistics(model=vmTx)

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
         (self.__lootBoxes.onBoxesInfoUpdated, self.__updateStatistics),
         (self.__lootBoxes.onBoxesUpdated, self.__updateStatistics),
         (self.__lootBoxes.onBoxesAvailabilityChanged, self.__onStatusChanged))

    def _getListeners(self):
        return ((events.LootBoxSystemEvent.ON_STATISTICS_RESET, self.__onUpdateReset, EVENT_BUS_SCOPE.LOBBY), (events.LootBoxSystemEvent.OPENING_ERROR, self.__onErrorBack, EVENT_BUS_SCOPE.LOBBY))

    @replaceNoneKwargsModel
    def __updateData(self, model=None):
        model.setEventName(self.__lootBoxes.eventName)
        model.setUseExternal(areUsedExternalTransitions())
        updateBoxesInfoModel(model.getBoxesInfo())

    @replaceNoneKwargsModel
    def __updateCounters(self, model=None):
        updateBoxesInfoModel(model.getBoxesInfo())

    @replaceNoneKwargsModel
    def __updateAnimationState(self, ctx=None, model=None):
        updateAnimationState(model, ctx)

    @replaceNoneKwargsModel
    def __updateSelectedBoxOption(self, ctx=None, model=None):
        boxOption = (ctx or {}).get('boxOption')
        if boxOption is None:
            if 'boxOption' not in self.__options:
                self.__options['boxOption'] = self.__getDefaultBoxOption()
            boxOption = self.__options['boxOption']
            if not self.__getBoxOptions()[boxOption].getInventoryCount():
                self.__options['boxOption'] = self.__getDefaultBoxOption()
            boxOption = self.__options['boxOption']
        else:
            self.__options['boxOption'] = int(boxOption)
        model.setSelectedBoxOption(boxOption)
        inventoryCount = self.__getBoxOptions()[self.__options['boxOption']].getInventoryCount()
        selectedCount = _OPENING_OPTIONS[self.__options.get('openingOption', 0)]
        if inventoryCount < selectedCount:
            self.__resetSelectedOpeningOption(model=model)
        return

    @replaceNoneKwargsModel
    def __updateOpeningOptions(self, model=None):
        openingOptions = model.getOpeningOptions()
        openingOptions.clear()
        for o in _OPENING_OPTIONS:
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
        self.__options['openingOption'] = 0
        model.setSelectedOpeningOption(self.__options['openingOption'])

    @replaceNoneKwargsModel
    def __resetError(self, model=None):
        model.setIsError(False)

    @replaceNoneKwargsModel
    def __updateStatistics(self, model=None):
        model.setUseStats(self.__lootBoxes.useStats)
        if self.__lootBoxes.useStats:
            self.__stats.update(model.statistics, findFirst(lambda b: b.getCategory() == self.boxCategory, self.__lootBoxes.getActiveBoxes()).getID(), self.__isResetCompleted)

    def __getDefaultBoxOption(self):
        preferredCategory = getPreferredBox().getCategory()
        return first((o for o, box in self.__getBoxOptions().iteritems() if box.getCategory() == preferredCategory), 0)

    def __getBoxOptions(self):
        return {o:box for o, box in enumerate(self.__lootBoxes.getActiveBoxes())}

    def __showInfo(self):
        Views.load(ViewID.INFO, ViewID.MAIN)

    @replaceNoneKwargsModel
    def __openBoxes(self, ctx, model=None):
        count = int(ctx.get('count'))

        def processResult(bonuses):
            model.setIsAwaitingResponse(False)
            self.parentView.switchToSubView(isBackground=True)
            self.parentView.switchToSubView(SubViewID.MULTIPLE_BOXES_REWARDS if count > 1 else SubViewID.SINGLE_BOX_REWARDS, category=self.boxCategory, count=count, bonuses=bonuses)

        model.setIsError(False)
        model.setIsAwaitingResponse(True)
        openBoxes(self.boxCategory, count, processResult)

    @replaceNoneKwargsModel
    def __onErrorBack(self, _, model=None):
        model.setIsAwaitingResponse(False)
        model.setIsError(True)

    def __buyBoxes(self):
        Views.load(ViewID.SHOP)

    def __onUpdateResetState(self):
        self.__isResetCompleted = False
        self.viewModel.statistics.setIsResetCompleted(self.__isResetCompleted)

    def __onUpdateReset(self, event):
        self.__isResetCompleted = event.ctx['isCompleted']

    def __onStatisticsReset(self):
        self.__stats.reset()

    def __onStatusChanged(self):
        if self.__lootBoxes.isActive and self.__lootBoxes.isLootBoxesAvailable:
            self.__updateStatistics()
