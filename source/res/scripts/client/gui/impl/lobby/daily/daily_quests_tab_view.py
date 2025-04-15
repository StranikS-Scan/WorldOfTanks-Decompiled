# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/daily_quests_tab_view.py
import typing
from constants import PremiumConfigs, DAILY_QUESTS_CONFIG
from frameworks.wulf import Array, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.daily_quest_premium_tab_view_model import DailyQuestPremiumTabViewModel
from gui.impl.gen.view_models.views.lobby.daily.daily_quest_regular_tab_view_model import DailyQuestRegularTabViewModel
from gui.impl.lobby.daily import DailyTabs
from gui.impl.lobby.daily.daily_quest_view_constants import QUESTS_TABS_IN_LEVEL
from gui.impl.pub import ViewImpl
from gui.server_events.events_helpers import dailyQuestsSortFunc, isPremiumQuestsEnable, isPremiumPlusAccount, isDailyRegularQuestsEnabled
from gui.shared.missions.packers.events import getEventUIDataPacker
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController, IUnseenEventsCounter
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import List

class DailyQuestTabView(ViewImpl):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __unseenEventsManager = dependency.descriptor(IUnseenEventsCounter)
    TAB_CONST = DailyTabs.QUESTS
    LAYOUT_ID = R.views.lobby.daily.DailyQuestRegularTabView()

    def __init__(self, layoutID=None):
        settings = ViewSettings(layoutID or self.LAYOUT_ID)
        settings.model = self._createViewModel()
        super(DailyQuestTabView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DailyQuestTabView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DailyQuestTabView, self)._onLoading()
        self._updateModel()

    def _updateModel(self):
        isEnabled = isDailyRegularQuestsEnabled()
        quests = sorted(self.eventsCache.getDailyQuests().values(), key=dailyQuestsSortFunc)
        with self.viewModel.transaction() as tx:
            tx.setIsEnabled(isEnabled)
            self._updateUnseenCount(tx)
            if isEnabled:
                self._updateQuests(tx.getQuests(), quests)

    def _updateQuests(self, questModels, quests):
        questModels.clear()
        questModels.reserve(len(quests))
        for quest in quests:
            packer = getEventUIDataPacker(quest)
            questModels.addViewModel(packer.pack())

        questModels.invalidate()

    def _onSyncCompleted(self, *_):
        self._updateModel()

    def _onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        cfName = self._getConfigName()
        if cfName in diff:
            dqDiff = diff[cfName]
            stateChanged = 'enabled' in dqDiff and dqDiff['enabled'] is not self.viewModel.getIsEnabled()
            if stateChanged:
                self._updateModel()

    def _getCallbacks(self):
        return (('tokens', self._onSyncCompleted),)

    def _getEvents(self):
        return ((self.eventsCache.onSyncCompleted, self._onSyncCompleted), (self.lobbyContext.getServerSettings().onServerSettingsChange, self._onServerSettingsChanged), (self.__unseenEventsManager.onSeenEvents, self.__onSeenEvents))

    def _updateUnseenCount(self, model):
        model.setUnseenCount(self.__unseenEventsManager.getUnseenEventsCount(self.eventsCache.getDailyQuests(filterLevels=QUESTS_TABS_IN_LEVEL[self.TAB_CONST]).keys()))

    def __onSeenEvents(self, *_):
        self._updateUnseenCount(self.viewModel)

    @classmethod
    def _createViewModel(cls):
        return DailyQuestRegularTabViewModel()

    @classmethod
    def _getConfigName(cls):
        return DAILY_QUESTS_CONFIG


class DailyQuestPremTabView(DailyQuestTabView):
    gameSession = dependency.descriptor(IGameSessionController)
    __unseenEventsManager = dependency.descriptor(IUnseenEventsCounter)
    TAB_CONST = DailyTabs.PREMIUM
    LAYOUT_ID = R.views.lobby.daily.DailyQuestPremiumTabView()

    @property
    def viewModel(self):
        return super(DailyQuestPremTabView, self).getViewModel()

    def _getEvents(self):
        eventsTuple = super(DailyQuestPremTabView, self)._getEvents()
        return eventsTuple + ((self.gameSession.onPremiumTypeChanged, self.__onPremiumChanged),)

    def _updateModel(self):
        hasPremAcc = isPremiumPlusAccount()
        isEnabled = isPremiumQuestsEnable()
        quests = sorted(self.eventsCache.getDailyPremiumQuests().values(), key=dailyQuestsSortFunc)
        with self.viewModel.transaction() as tx:
            tx.setIsEnabled(isEnabled)
            tx.setHasPremiumAccount(hasPremAcc)
            self._updateUnseenCount(tx)
            if isEnabled:
                self._updateQuests(tx.getQuests(), quests)

    @classmethod
    def _createViewModel(cls):
        return DailyQuestPremiumTabViewModel()

    @classmethod
    def _getConfigName(cls):
        return PremiumConfigs.PREM_QUESTS

    def __onPremiumChanged(self, _):
        self._updateModel()
