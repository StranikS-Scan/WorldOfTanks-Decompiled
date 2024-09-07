# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/daily_quests_intro_presenter.py
from frameworks.wulf import ViewStatus
from gui.battle_pass.battle_pass_helpers import isBattlePassDailyQuestsIntroShown, showBattlePassDailyQuestsIntro
from gui.impl.gen import R
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController, IDailyQuestIntroPresenter, IWotPlusController
from skeletons.gui.impl import IGuiLoader
from gui.impl.lobby.subscription.subscription_helpers import showSubscriptionDailyQuestsIntro, isSubscriptionDailyQuestsIntroShown
from skeletons.gui.lobby_context import ILobbyContext

class DailyQuestsIntroPresenter(IDailyQuestIntroPresenter):
    __slots__ = ()
    __settingsCore = dependency.descriptor(ISettingsCore)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __subscription = dependency.descriptor(IWotPlusController)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    @property
    def parentViewLayoutID(self):
        return R.views.lobby.missions.Daily()

    def onLobbyStarted(self, *_):
        self.__addListeners()
        self.__update()

    def onAccountBecomeNonPlayer(self):
        self.__clearListeners()

    def fini(self):
        self.__clearListeners()

    def __addListeners(self):
        if self.__guiLoader.windowsManager is not None:
            self.__guiLoader.windowsManager.onViewStatusChanged += self.__onViewStatusChanged
        return

    def __clearListeners(self):
        if self.__guiLoader.windowsManager is not None:
            self.__guiLoader.windowsManager.onViewStatusChanged -= self.__onViewStatusChanged
        return

    def __onViewStatusChanged(self, uniqueID, newStatus):
        if newStatus == ViewStatus.LOADED:
            if self.__guiLoader.windowsManager.getView(uniqueID).layoutID == self.parentViewLayoutID:
                self.__update()

    def __update(self, *_):
        if self.__isDailyQuestView():
            if not isSubscriptionDailyQuestsIntroShown() and self._lobbyContext.getServerSettings().isDailyQuestsExtraRewardsEnabled():
                showSubscriptionDailyQuestsIntro()
            elif self.__battlePassController.isActive() and not isBattlePassDailyQuestsIntroShown():
                showBattlePassDailyQuestsIntro()

    def __isDailyQuestView(self):
        return self.__guiLoader.windowsManager.getViewByLayoutID(self.parentViewLayoutID) is not None
