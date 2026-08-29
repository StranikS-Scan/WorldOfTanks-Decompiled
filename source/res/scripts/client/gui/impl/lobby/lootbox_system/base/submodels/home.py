# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/base/submodels/home.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
from account_helpers.AccountSettings import LOOT_BOXES_SELECTED_BOX
from frameworks.wulf.view.array import fillIntsArray
from gui.impl.gen.view_models.views.lobby.lootbox_system.main_view_model import SubViewID
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.home_view_model import HomeViewModel
from gui.impl.lobby.lootbox_system.base.common import SubViewImpl
from gui.impl.lobby.lootbox_system.base.submodels.common import updateAnimationState, updateBoxesInfoModel
from gui.impl.lobby.lootbox_system.base.submodels.statistics import Statistics
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.lootbox_system.base.common import ViewID, Views
from gui.lootbox_system.base.decorators import createTooltipContentDecorator
from gui.lootbox_system.base.utils import getOpeningOptions, getPreferredBox, openBoxes, isShopVisible
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from shared_utils import findFirst
from skeletons.gui.game_control import ILootBoxSystemController
if TYPE_CHECKING:
    from typing import Dict, List
    from gui.server_events.bonuses import SimpleBonus
_OPENING_OPTION_KEY = 'openingOption'

class Home(SubViewImpl):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)
    __options = {}

    def __init__(self, viewModel, parentView):
        super(Home, self).__init__(viewModel, parentView)
        self._stats = Statistics()
        self.__isResetCompleted = False
        self.__isOpeningInProgress = False
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
        return super(Home, self).createToolTip(event)

    def initialize(self, *args, **kwargs):
        super(Home, self).initialize(*args, **kwargs)
        self.__eventName = kwargs.get('eventName', '')
        self.__boxOption = self.__lootBoxes.getSetting(self.__eventName, LOOT_BOXES_SELECTED_BOX)
        for event in self.__lootBoxes.getActiveEvents():
            self.__options.setdefault(event, {})

        with self.viewModel.transaction() as vmTx:
            self.__updateData(model=vmTx)
            self.__updateCounters(model=vmTx)
            self.__updateAnimationState(model=vmTx)
            self.__updateSelectedOpeningOption(model=vmTx)

    def finalize(self):
        self.__isOpeningInProgress = False
        self.__lootBoxes.setSetting(self.__eventName, LOOT_BOXES_SELECTED_BOX, self.__boxOption)
        super(Home, self).finalize()

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
        self.__updateTime(model=model)

    @replaceNoneKwargsModel
    def __updateCounters(self, model=None):
        if self.__isOpeningInProgress:
            return
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
        self.__lootBoxes.setSetting(self.__eventName, LOOT_BOXES_SELECTED_BOX, self.__boxOption)
        self.__updateOpeningOptions(model=model)
        return

    @replaceNoneKwargsModel
    def __updateOpeningOptions(self, model=None):
        openingOptions = getOpeningOptions(self.__eventName, self.__boxOption)
        fillIntsArray(openingOptions, model.getOpeningOptions())
        openingIndex = self.__options[self.__eventName].get(_OPENING_OPTION_KEY, 0)
        if openingIndex == 0:
            return
        else:
            box = self.__lootBoxes.getBox(self.__eventName, self.__boxOption)
            inventoryCount = box.getInventoryCount() if box is not None else 0
            if openingIndex >= len(openingOptions) or inventoryCount < openingOptions[openingIndex]:
                self.__resetSelectedOpeningOption(model=model)
            return

    @replaceNoneKwargsModel
    def __updateSelectedOpeningOption(self, ctx=None, model=None):
        openingOption = (ctx or {}).get(_OPENING_OPTION_KEY)
        if openingOption is None:
            openingOption = self.__options.get(_OPENING_OPTION_KEY, 0)
        else:
            self.__options[_OPENING_OPTION_KEY] = int(openingOption)
        model.setSelectedOpeningOption(openingOption)
        return

    @replaceNoneKwargsModel
    def __resetSelectedOpeningOption(self, model=None):
        self.__options[self.__eventName][_OPENING_OPTION_KEY] = 0
        model.setSelectedOpeningOption(self.__options[self.__eventName][_OPENING_OPTION_KEY])

    @replaceNoneKwargsModel
    def __resetError(self, model=None):
        model.setIsError(False)

    @replaceNoneKwargsModel
    def __updateStatistics(self, model=None):
        useStats = self.__lootBoxes.useStats(self.__eventName)
        model.setUseStats(useStats)
        if useStats:
            self._stats.update(model.statistics, findFirst(lambda b: b.getCategory() == self.boxCategory, self.__lootBoxes.getActiveBoxes(self.__eventName)).getID(), self.__isResetCompleted, self.__eventName)

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
            self.__isOpeningInProgress = False

        model.setIsError(False)
        self.__isOpeningInProgress = True
        openBoxes(self.__eventName, self.boxCategory, count, processResult)

    @replaceNoneKwargsModel
    def __onErrorBack(self, _, model=None):
        self.__isOpeningInProgress = False
        self.__updateCounters()
        model.setIsError(True)

    def __buyBoxes(self):
        Views.load(ViewID.SHOP, eventName=self.__eventName)

    def __onUpdateResetState(self):
        self.__isResetCompleted = False
        self.viewModel.statistics.setIsResetCompleted(self.__isResetCompleted)

    def __onUpdateReset(self, event):
        self.__isResetCompleted = event.ctx['isCompleted']

    def __onStatisticsReset(self):
        self._stats.reset()

    def __onStatusChanged(self):
        if self.__lootBoxes.isAvailable(self.__eventName) and self.__lootBoxes.getActiveBoxes(self.__eventName):
            self.__updateData()
            self.__updateStatistics()

    def __updateTime(self, model=None):
        model.setEventExpireTime(self.__getEventExpireTime())

    def __getEventExpireTime(self):
        _, finish = self.__lootBoxes.getActiveTime(self.__eventName)
        return finish - getServerUTCTime()
