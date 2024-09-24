# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/submodels/single_box_rewards.py
import logging
import Windowing
from typing import TYPE_CHECKING
from gui.impl.gen.view_models.views.lobby.lootbox_system.main_view_model import SubViewID
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.single_box_rewards_view_model import SingleBoxRewardsViewModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.lootbox_system.common import SubViewImpl
from gui.impl.lobby.lootbox_system.submodels.common import updateAnimationState
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.lootbox_system.bonuses_packers import packBonusModelAndTooltipData
from gui.lootbox_system.common import ViewID, Views
from gui.lootbox_system.decorators import createTooltipContentDecorator
from gui.lootbox_system.sound import playVideoPauseSound, playVideoResumeSound
from gui.lootbox_system.utils import areUsedExternalTransitions, openBoxes
from gui.lootbox_system.views_loaders import hideItemPreview, showItemPreview
from gui.server_events.bonuses import SimpleBonus
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import ILootBoxSystemController
if TYPE_CHECKING:
    from typing import Dict, List
_logger = logging.getLogger(__name__)
_EXTRA_BONUSES_NAMES = ('slots',)

class SingleBoxRewards(SubViewImpl):
    __slots__ = ('__isReopen', '__category', '__openCount', '__bonuses', '__extraBonuses', '__tooltipItems', '__isVideoPlaying')
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, viewModel, parentView):
        super(SingleBoxRewards, self).__init__(viewModel, parentView)
        self.__isReopen = False
        self.__category = ''
        self.__openCount = 0
        self.__bonuses = []
        self.__extraBonuses = []
        self.__tooltipItems = {}
        self.__isVideoPlaying = False

    @property
    def viewModel(self):
        return self.getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(SingleBoxRewards, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(SingleBoxRewards, self).createToolTip(event)

    def getTooltipData(self, event):
        return self.__tooltipItems.get(event.getArgument('tooltipId', 0))

    def initialize(self, *args, **kwargs):
        super(SingleBoxRewards, self).initialize(*args, **kwargs)
        self.__isReopen = kwargs.get('isReopen', False)
        self.__category = kwargs.get('category', '')
        self.__openCount = kwargs.get('count', 0)
        self.__updateBonusesData(first(kwargs.get('bonuses', []), []))
        with self.viewModel.transaction() as vmTx:
            self.__setWindowAccessible(model=vmTx)
            self.__updateData(model=vmTx)
            self.__updateCounters(model=vmTx)
            self.__updateBonuses(model=vmTx)
            self.__updateAnimationState(model=vmTx)
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)

    def finalize(self):
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        super(SingleBoxRewards, self).finalize()

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

    def __setVideoPlaying(self, ctx=None):
        isPlaying = ctx.get('isPlaying')
        self.__isVideoPlaying = isPlaying

    def _getListeners(self):
        return ((events.LootBoxSystemEvent.OPENING_ERROR, self.__onErrorBack, EVENT_BUS_SCOPE.LOBBY),)

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

    @replaceNoneKwargsModel
    def __updateBonuses(self, model=None):
        model.bonuses.clearItems()
        model.extraBonuses.clearItems()
        packBonusModelAndTooltipData(self.__bonuses, model.bonuses, self.__tooltipItems, merge=False)
        packBonusModelAndTooltipData(self.__extraBonuses, model.extraBonuses, self.__tooltipItems, merge=False)
        model.bonuses.invalidate()
        model.extraBonuses.invalidate()

    @replaceNoneKwargsModel
    def __updateAnimationState(self, ctx=None, model=None):
        updateAnimationState(model, ctx)

    def __openNext(self, ctx=None):
        category = ctx.get('category') if ctx is not None else ''

        def processResult(bonuses):
            self.viewModel.setIsAwaitingResponse(False)
            self.viewModel.setBoxCategory(self.__category)
            self.__updateCounters()
            self.__updateBonusesData(first(bonuses))
            self.__updateBonuses()

        self.__isReopen = False
        self.viewModel.setIsAwaitingResponse(True)
        if category:
            self.__category = category
        openBoxes(self.__category, self.__openCount, processResult)
        return

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
        Views.load(ViewID.MAIN, SubViewID.SINGLE_BOX_REWARDS, isReopen=True, count=self.__openCount, category=self.__category, bonuses=[self.__bonuses + self.__extraBonuses])

    def __updateBonusesData(self, bonuses):
        self.__extraBonuses = []
        if len(bonuses) == 1:
            self.__bonuses = bonuses
            return
        self.__bonuses = []
        for bonus in bonuses:
            if bonus.getName() in _EXTRA_BONUSES_NAMES:
                self.__extraBonuses.append(bonus)
            self.__bonuses.append(bonus)
