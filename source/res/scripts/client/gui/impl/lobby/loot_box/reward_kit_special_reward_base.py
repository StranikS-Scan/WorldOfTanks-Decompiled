# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/reward_kit_special_reward_base.py
import logging
from functools import partial
from gui.impl.lobby.loot_box.loot_box_helper import LootBoxHideableView, showLootBoxReward, fireCloseToHangar, fireSpecialRewardsClosed
from helpers import dependency
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxVideoStartStopHandler
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from skeletons.gui.game_control import IFestivityController
from uilogging.ny.loggers import NyLootBoxesRewardsFlowLogger
_logger = logging.getLogger(__name__)

class RewardKitSpecialRewardBase(LootBoxHideableView):
    __slots__ = ('_videoStartStopHandler', '_congratsSourceId', '_backToSingleOpening', '__showRewardsAndDestroyFunc')
    _festivityController = dependency.descriptor(IFestivityController)
    _flowLogger = NyLootBoxesRewardsFlowLogger()

    def __init__(self, settings):
        self._congratsSourceId = 0
        self._backToSingleOpening = False
        self._videoStartStopHandler = LootBoxVideoStartStopHandler()
        super(RewardKitSpecialRewardBase, self).__init__(settings)
        self.__showRewardsAndDestroyFunc = None
        return

    def _initialize(self, *args, **kwargs):
        super(RewardKitSpecialRewardBase, self)._initialize()
        if self._isMemoryRiskySystem and self._backToSingleOpening:
            g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.REMOVE_HIDE_VIEW), EVENT_BUS_SCOPE.LOBBY)
            self._isCanClose = True
        self.setHoldSwfs(True)

    def _finalize(self):
        self.setHoldSwfs(False)
        self._videoStartStopHandler.onVideoDone()
        self._videoStartStopHandler = None
        super(RewardKitSpecialRewardBase, self)._finalize()
        return

    def _onContinue(self, _=None):
        if self._isMemoryRiskySystem and self._backToSingleOpening:
            if not self._isCanClose or not self._festivityController.isEnabled():
                return
            self.__showRewardsAndDestroyFunc = partial(showLootBoxReward, None, None, None, self._backToSingleOpening)
            self._startFade(self.__showRewardsAndDestroy, withPause=True)
        else:
            fireSpecialRewardsClosed()
            self.destroyWindow()
        return

    def _onGoToReward(self, _=None):
        raise NotImplementedError

    def _closeToHangar(self):
        fireCloseToHangar()

    def _onVideoStopped(self, _=None):
        self._videoStartStopHandler.onVideoDone()

    def _onWindowAccessibilityChanged(self, isWindowAccessible):
        self._videoStartStopHandler.setIsNeedPause(not isWindowAccessible)

    def __showRewardsAndDestroy(self):
        if self.__showRewardsAndDestroyFunc is not None:
            self.__showRewardsAndDestroyFunc()
            self.__showRewardsAndDestroyFunc = None
        self.destroyWindow()
        return
