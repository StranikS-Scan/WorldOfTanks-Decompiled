# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_reward_view.py
import logging
from frameworks.wulf import ViewSettings, WindowFlags
from constants import SENIORITY_AWARDS_CONFIG
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_reward_view_model import SeniorityRewardViewModel
from gui.impl.lobby.progressive_reward.progressive_award_sounds import setSoundState, ProgressiveRewardSoundEvents
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from gui.Scaleform.daapi.view.lobby.hangar.seniority_awards import getSeniorityAwardsBoxesCount, getSeniorityAwardsAutoOpenDate
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.seniority_awards.seniority_awards_helper import showSeniorityAwardsMultyOpen
_logger = logging.getLogger(__name__)

class SeniorityRewardView(ViewImpl):
    __COUNT_OPEN_AWARDS = 5
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, contentResId, *args, **kwargs):
        settings = ViewSettings(contentResId)
        settings.model = SeniorityRewardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(SeniorityRewardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SeniorityRewardView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(SeniorityRewardView, self)._initialize(*args, **kwargs)
        self.viewModel.onDestroyEvent += self.__onDestroy
        self.viewModel.onCloseAction += self.__onWindowClose
        self.viewModel.onOpenBtnClick += self.__onOpenBtnClick
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self._eventsCache.onSyncCompleted += self.__onSyncCompleted
        self._itemsCache.onSyncCompleted += self.__onCacheResync
        self.__update()
        setSoundState(groupName=ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_GROUP, stateName=ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_ENTER)

    def _finalize(self):
        self.viewModel.onOpenBtnClick -= self.__onOpenBtnClick
        self.viewModel.onCloseAction -= self.__onWindowClose
        self.viewModel.onDestroyEvent -= self.__onDestroy
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self._eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        super(SeniorityRewardView, self)._finalize()

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
        countAvailableAward = getSeniorityAwardsBoxesCount()
        if countAvailableAward > 0:
            autoOpenDate = getSeniorityAwardsAutoOpenDate()
            with self.viewModel.transaction() as tx:
                tx.setBuyBtnOpenCount(self.__COUNT_OPEN_AWARDS)
                tx.setCountAwards(countAvailableAward)
                tx.setAutoOpenDate(autoOpenDate)
        else:
            self.viewModel.setHardReset(True)

    def __onServerSettingsChange(self, diff):
        configs = {SENIORITY_AWARDS_CONFIG}
        if configs.intersection(diff):
            boxesCount = getSeniorityAwardsBoxesCount()
            if boxesCount == 0:
                self.__onWindowClose()
            else:
                self.__update()

    def __onOpenBtnClick(self):
        self.destroyWindow()
        showSeniorityAwardsMultyOpen()

    def __onCacheResync(self, reason, diff):
        self.__update()


class SeniorityRewardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, contentResId, *args, **kwargs):
        super(SeniorityRewardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, decorator=None, content=SeniorityRewardView(contentResId, *args, **kwargs), parent=None)
        return
