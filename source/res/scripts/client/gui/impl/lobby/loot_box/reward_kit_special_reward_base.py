# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/reward_kit_special_reward_base.py
import logging
from gui.impl.lobby.loot_box.loot_box_helper import LootBoxHideableView, fireCloseToHangar, fireSpecialRewardsClosed
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxVideoStartStopHandler
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared import events
from helpers import dependency
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

    def _finalize(self):
        self._videoStartStopHandler.onVideoDone()
        self._videoStartStopHandler = None
        super(RewardKitSpecialRewardBase, self)._finalize()
        return

    def _onContinue(self, _=None):
        fireSpecialRewardsClosed()
        self.destroyWindow()

    def _onGoToReward(self, _=None):
        raise NotImplementedError

    @staticmethod
    def _closeToHangar():
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
