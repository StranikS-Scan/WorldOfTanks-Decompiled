# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback/winback_daily_quests_intro_view.py
from constants import DAILY_QUESTS_CONFIG
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen.view_models.views.lobby.winback.winback_daily_quests_intro_view_model import WinbackDailyQuestsIntroViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R
from helpers import dependency
from gui.server_events.events_helpers import dailyQuestsSortFunc
from skeletons.new_year import INewYearController
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.lobby_context import ILobbyContext

class WinbackDailyQuestsIntroView(ViewImpl):
    __slots__ = ('__hasNYResourcesReward',)
    __eventsCache = dependency.descriptor(IEventsCache)
    __battlePass = dependency.descriptor(IBattlePassController)
    __nyController = dependency.descriptor(INewYearController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        viewSettings = ViewSettings(R.views.lobby.winback.WinbackDailyQuestsIntroView())
        viewSettings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        viewSettings.model = WinbackDailyQuestsIntroViewModel()
        super(WinbackDailyQuestsIntroView, self).__init__(viewSettings)
        self.__hasNYResourcesReward = False

    @property
    def viewModel(self):
        return super(WinbackDailyQuestsIntroView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WinbackDailyQuestsIntroView, self)._onLoading(*args, **kwargs)
        self.__onDailyQuestsChanged()
        self.__update()
        self.__onNYEventStateChanged()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.__battlePass.onBattlePassSettingsChange, self.__update),
         (self.__nyController.onStateChanged, self.__onNYEventStateChanged),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged))

    def __onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        if DAILY_QUESTS_CONFIG in diff:
            self.__onDailyQuestsChanged()

    def __onDailyQuestsChanged(self):
        quests = sorted(self.__eventsCache.getDailyQuests().values(), key=dailyQuestsSortFunc)
        self.__hasNYResourcesReward = any([ bonus.getName() == 'nyRandomResource' for quest in quests for bonus in quest.getBonuses() ])

    def __update(self, *_):
        self.viewModel.setHasBattlePass(self.__battlePass.isActive())

    def __onNYEventStateChanged(self):
        with self.viewModel.transaction() as model:
            model.setIsNewYearActive(self.__nyController.isEnabled() and self.__hasNYResourcesReward)

    def __onClose(self):
        self.destroyWindow()


class WinbackDailyQuestsIntroWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WinbackDailyQuestsIntroWindow, self).__init__(WindowFlags.WINDOW, content=WinbackDailyQuestsIntroView(), parent=parent, layer=WindowLayer.TOP_SUB_VIEW)
