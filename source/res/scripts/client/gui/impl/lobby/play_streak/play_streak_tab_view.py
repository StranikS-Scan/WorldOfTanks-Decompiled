# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/play_streak/play_streak_tab_view.py
from account_helpers.AccountSettings import PlayStreak, AccountSettings
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.play_streak.play_streak_tab_view_model import PlayStreakTabViewModel
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from skeletons.gui.game_control import IPlayStreakController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class PlayStreakTabView(ViewImpl):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __playStreakController = dependency.descriptor(IPlayStreakController)

    def __init__(self, layoutID=R.views.lobby.daily.PlayStreakTabView()):
        super(PlayStreakTabView, self).__init__(ViewSettings(layoutID, ViewFlags.VIEW, self._createViewModel()))

    @property
    def viewModel(self):
        return super(PlayStreakTabView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PlayStreakTabView, self)._onLoading()
        self._updateModel()

    def _updateModel(self):
        with self.viewModel.transaction() as tx:
            tx.setStreakLength(self.__playStreakController.getStreakProgress())
            self.__setIsFirstAppearance(model=tx)
            tx.setSkipDayCount(self.__playStreakController.getSkipDayCount())
            tx.setDailyWin(self.itemsCache.items.playStreak.getDailyConditionCompleted())
            tx.setIsPaused(self.lobbyContext.getServerSettings().playStreakConfig.isPaused)
            tx.setRedemptionDayCount(self.itemsCache.items.playStreak.getRedemptionDay())
            tx.setIsBlocked(self.__playStreakController.getIsBlocked())
            tx.setRedemptionMaxDayCount(self.lobbyContext.getServerSettings().playStreakConfig.daySkipSettings.get('freezeModeLength'))
            tx.setIsEnabled(self.lobbyContext.getServerSettings().playStreakConfig.isEnabled)

    def _onSyncCompleted(self, *_):
        self._updateModel()

    @replaceNoneKwargsModel
    def __setIsFirstAppearance(self, model=None):
        streakProgress = self.__playStreakController.getStreakProgress()
        freezeProgress = self.itemsCache.items.playStreak.getRedemptionDay()
        lastSeenCount = AccountSettings.getPlayStreak(PlayStreak.PLAY_STREAK_LAST_LEVEL_SEEN_TAB)
        lastFreezeSeenCount = AccountSettings.getPlayStreak(PlayStreak.PLAY_STREAK_LAST_LEVEL_FREEZE_SEEN_TAB)
        if streakProgress != lastSeenCount and streakProgress:
            AccountSettings.setPlayStreak(PlayStreak.PLAY_STREAK_LAST_LEVEL_SEEN_TAB, streakProgress)
            model.setIsFirstAppearance(True)
        elif lastFreezeSeenCount != freezeProgress and self.itemsCache.items.playStreak.getDailyConditionCompleted():
            AccountSettings.setPlayStreak(PlayStreak.PLAY_STREAK_LAST_LEVEL_FREEZE_SEEN_TAB, freezeProgress)
            if freezeProgress > 0:
                model.setIsFirstAppearanceRedemptionDay(True)
            else:
                model.setIsLastDayRedemption(True)
        else:
            model.setIsFirstAppearance(False)
            model.setIsLastDayRedemption(False)
            model.setIsFirstAppearanceRedemptionDay(False)

    def __onFinishAnimation(self):
        self.__setIsFirstAppearance()

    def _getEvents(self):
        return ((self.eventsCache.onSyncCompleted, self._onSyncCompleted),
         (self.lobbyContext.getServerSettings().onServerSettingsChange, self._onSyncCompleted),
         (self.viewModel.onFinishAnimation, self.__onFinishAnimation),
         (self.__playStreakController.onDataUpdated, self._updateModel))

    def _getCallbacks(self):
        return (('tokens', self._onSyncCompleted),)

    def __onShowInfo(self):
        url = GUI_SETTINGS.lookup('infoPagePlayStreak')
        showBrowserOverlayView(url, VIEW_ALIAS.PLAY_STREAK_INFO_OVERLAY)

    def _createViewModel(self):
        return PlayStreakTabViewModel()
