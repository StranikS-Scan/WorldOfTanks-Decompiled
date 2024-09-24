# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/submodels/multiple_boxes_rewards.py
from typing import TYPE_CHECKING
import Windowing
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.lootbox_system.main_view_model import SubViewID
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.multiple_boxes_rewards_view_model import MultipleBoxesRewardsViewModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.lootbox_system.common import SubViewImpl
from gui.impl.lobby.lootbox_system.submodels.common import updateAnimationState
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.lootbox_system.bonuses_packers import packBonusModelAndTooltipData
from gui.lootbox_system.common import ViewID, Views
from gui.lootbox_system.decorators import createTooltipContentDecorator
from gui.lootbox_system.sound import enterLootBoxesMultipleRewardState, exitLootBoxesMultipleRewardState, playVideoPauseSound, playVideoResumeSound
from gui.lootbox_system.utils import areUsedExternalTransitions, openBoxes
from gui.lootbox_system.views_loaders import hideItemPreview, showItemPreview
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency
from skeletons.gui.game_control import ILootBoxSystemController
if TYPE_CHECKING:
    from typing import Dict, List, Optional
    from gui.server_events.bonuses import SimpleBonus

class MultipleBoxesRewards(SubViewImpl):
    __slots__ = ('__isReopen', '__category', '__openCount', '__bonuses', '__tooltipItems', '__isVideoPlaying')
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, viewModel, parentView):
        super(MultipleBoxesRewards, self).__init__(viewModel, parentView)
        self.__isReopen = False
        self.__category = ''
        self.__openCount = 0
        self.__bonuses = None
        self.__tooltipItems = {}
        self.__isVideoPlaying = False
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(MultipleBoxesRewards, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(MultipleBoxesRewards, self).createToolTip(event)

    def getTooltipData(self, event):
        return self.__tooltipItems.get(event.getArgument('tooltipId', 0))

    def initialize(self, *args, **kwargs):
        super(MultipleBoxesRewards, self).initialize(*args, **kwargs)
        enterLootBoxesMultipleRewardState()
        self.__isReopen = kwargs.get('isReopen', False)
        self.__category = kwargs.get('category', '')
        self.__openCount = kwargs.get('count', 0)
        self.__bonuses = kwargs.get('bonuses', [])
        with self.viewModel.transaction() as vmTx:
            self.__setWindowAccessible(model=vmTx)
            self.__updateData(model=vmTx)
            self.__updateCounters(model=vmTx)
            self.__updateBonuses(model=vmTx)
            self.__updateAnimationState(model=vmTx)
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)

    def finalize(self):
        exitLootBoxesMultipleRewardState()
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        super(MultipleBoxesRewards, self).finalize()

    def _getEvents(self):
        return ((self.viewModel.onOpen, self.__openNext),
         (self.viewModel.onGoBack, self.__goBack),
         (self.viewModel.onPreview, self.__showPreview),
         (self.viewModel.onBuyBoxes, self.__openShop),
         (self.viewModel.onAnimationStateChanged, self.__updateAnimationState),
         (self.viewModel.onVideoPlaying, self.__setVideoPlaying),
         (self.viewModel.onClose, self.__goBack),
         (self.__lootBoxes.onBoxesCountChanged, self.__updateCounters),
         (self.__lootBoxes.onBoxesUpdated, self.__updateCounters))

    def _getListeners(self):
        return ((events.LootBoxSystemEvent.OPENING_ERROR, self.__onErrorBack, EVENT_BUS_SCOPE.LOBBY),)

    def __setVideoPlaying(self, ctx=None):
        isPlaying = ctx.get('isPlaying')
        self.__isVideoPlaying = isPlaying

    @replaceNoneKwargsModel
    def __setWindowAccessible(self, model=None):
        isWindowAccessible = Windowing.isWindowAccessible()
        model.setIsWindowAccessible(isWindowAccessible)

    def __onWindowAccessibilityChanged(self, _):
        isWindowAccessible = Windowing.isWindowAccessible()
        if self.__isVideoPlaying:
            self.__setWindowAccessible()
            if isWindowAccessible:
                playVideoResumeSound()
            else:
                playVideoPauseSound()

    @replaceNoneKwargsModel
    def __updateData(self, model=None):
        model.setEventName(self.__lootBoxes.eventName)
        model.setBoxCategory(self.__category)
        model.setIsReopen(self.__isReopen)
        model.setUseExternal(areUsedExternalTransitions())

    @replaceNoneKwargsModel
    def __updateCounters(self, model=None):
        model.setBoxesCount(self.__lootBoxes.getBoxesCount(self.__category))
        model.setBoxesCountToGuaranteed(self.__lootBoxes.getBoxesCountToGuaranteed(self.__category))
        model.setOpeningCount(self.__openCount)

    @replaceNoneKwargsModel
    def __updateBonuses(self, model=None):
        bonuses = model.getBonuses()
        bonuses.clear()
        for boxRewards in self.__bonuses:
            boxModel = Array()
            packBonusModelAndTooltipData(boxRewards, boxModel, self.__tooltipItems, merge=False)
            bonuses.addArray(boxModel)

        bonuses.invalidate()

    @replaceNoneKwargsModel
    def __updateAnimationState(self, ctx=None, model=None):
        updateAnimationState(model, ctx)

    def __openNext(self, ctx=None):
        count = int(ctx.get('openCount'))
        category = ctx.get('category')

        def processResult(bonuses):
            self.viewModel.setIsAwaitingResponse(False)
            if count > 1:
                self.__bonuses = bonuses
                self.__updateBonuses()
                self.__updateCounters()
            else:
                self.parentView.switchToSubView(isBackground=True)
                self.parentView.switchToSubView(SubViewID.SINGLE_BOX_REWARDS, category=self.__category, count=count, bonuses=bonuses)

        self.__isReopen = False
        self.viewModel.setIsAwaitingResponse(True)
        if category:
            self.__category = category
        openBoxes(self.__category, count or self.__openCount, processResult)

    def __goBack(self):
        self.parentView.switchToSubView()

    def __onErrorBack(self, *_):
        self.viewModel.setIsAwaitingResponse(False)
        self.parentView.switchToSubView()

    def __showPreview(self, ctx):
        showItemPreview(str(ctx.get('bonusType')), int(ctx.get('bonusId')), int(ctx.get('styleID')), self.__reopen)

    def __openShop(self):
        Views.load(ViewID.SHOP)

    def __reopen(self):
        hideItemPreview()
        Views.load(ViewID.MAIN, SubViewID.MULTIPLE_BOXES_REWARDS, isReopen=True, count=self.__openCount, category=self.__category, bonuses=self.__bonuses)
