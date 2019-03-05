# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/progressive_reward/progressive_reward_view.py
import logging
from frameworks.wulf import ViewFlags
from frameworks.wulf import WindowFlags
from gui.impl.auxiliary.rewards_helper import fillStepsModel
from gui.impl.gen.view_models.views.lobby.progressive_reward.progressive_reward_view_model import ProgressiveRewardViewModel
from gui.impl.lobby.progressive_reward.progressive_award_sounds import setSoundState, ProgressiveRewardSoundEvents
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)

class ProgressiveRewardView(ViewImpl):
    _eventsCache = dependency.descriptor(IEventsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ()

    def __init__(self, contentResId, *args, **kwargs):
        super(ProgressiveRewardView, self).__init__(contentResId, ViewFlags.VIEW, ProgressiveRewardViewModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(ProgressiveRewardView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ProgressiveRewardView, self)._initialize(*args, **kwargs)
        self.viewModel.onDestroyEvent += self.__onDestroy
        self.viewModel.onCloseAction += self.__onWindowClose
        self._eventsCache.onSyncCompleted += self.__onSyncCompleted
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__update()
        setSoundState(groupName=ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_GROUP, stateName=ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_ENTER)

    def _finalize(self):
        self.viewModel.onCloseAction -= self.__onWindowClose
        self.viewModel.onDestroyEvent -= self.__onDestroy
        self._eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        super(ProgressiveRewardView, self)._finalize()

    def __onWindowClose(self, _=None):
        if self.viewModel.getHardReset():
            self.__onDestroy()
        else:
            self.viewModel.setFadeOut(True)

    def __onDestroy(self, _=None):
        setSoundState(groupName=ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_GROUP, stateName=ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_EXIT)
        self.destroyWindow()

    def __onSyncCompleted(self, *_):
        self.__update()

    def __update(self):
        if not self._lobbyContext.getServerSettings().getProgressiveRewardConfig().isEnabled:
            self.viewModel.setHardReset(True)
            return
        progressive = self._eventsCache.getProgressiveReward()
        with self.viewModel.transaction() as tx:
            steps = tx.getSteps()
            steps.clear()
            fillStepsModel(progressive.currentStep, progressive.probability, progressive.maxSteps, False, steps)
            steps.invalidate()
            tx.setStepIdx(progressive.currentStep)

    def __onServerSettingsChange(self, diff):
        if 'progressive_reward_config' in diff:
            if self._lobbyContext.getServerSettings().getProgressiveRewardConfig().isEnabled:
                self.__update()
            else:
                self.__onWindowClose()


class ProgressiveRewardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, contentResId, *args, **kwargs):
        super(ProgressiveRewardWindow, self).__init__(wndFlags=WindowFlags.OVERLAY, decorator=None, content=ProgressiveRewardView(contentResId, *args, **kwargs), parent=None)
        return
