# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/entry_point.py
from collections import defaultdict
from functools import partial
import typing
from account_helpers.AccountSettings import WOT_ANNIVERSARY_SEEN_DAILY_QUEST, WOT_ANNIVERSARY_SEEN_WEEKLY_QUEST
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import WotAnniversaryStorageKeys
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.wot_anniversary_entry_point_model import WotAnniversaryEntryPointModel, State
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_helpers import EventInfoModel
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.wot_anniversary.wot_anniversary_helpers import showWotAnniversaryIntroWindow, getWotAnniversarySectionSetting, setWotAnniversarySectionSetting, findWeeklyQuest, showMainView
from helpers import dependency
from helpers import time_utils
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IWotAnniversaryController, IWalletController
from skeletons.gui.shared import IItemsCache

class WotAnniversaryEntryPointInjectWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return WotAnniversaryEntryPointWidget()


class WotAnniversaryEntryPointWidget(ViewImpl):
    __wotAnniversaryCtrl = dependency.descriptor(IWotAnniversaryController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.wot_anniversary.EntryPoint())
        settings.flags = ViewFlags.COMPONENT
        settings.model = WotAnniversaryEntryPointModel()
        self.__onClickCallbacks = defaultdict(list)
        super(WotAnniversaryEntryPointWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WotAnniversaryEntryPointWidget, self).getViewModel()

    def _initialize(self):
        super(WotAnniversaryEntryPointWidget, self)._initialize()
        self.viewModel.onWidgetClick += self.__onWidgetClick
        self.__wotAnniversaryCtrl.onSettingsChanged += self.__onSettingChanged
        self.__wallet.onWalletStatusChanged += self.__onWalletStatusChanged
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate,
         'stats.eventCoin': self.__onTokensUpdate})
        g_eventBus.addListener(events.WotAnniversaryEvent.ON_WIDGET_STATE_UPDATED, self.__updateWidgetState, scope=EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        g_eventBus.removeListener(events.WotAnniversaryEvent.ON_WIDGET_STATE_UPDATED, self.__updateWidgetState, scope=EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.onWidgetClick -= self.__onWidgetClick
        self.__wotAnniversaryCtrl.onSettingsChanged -= self.__onSettingChanged
        self.__wallet.onWalletStatusChanged -= self.__onWalletStatusChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__onClickCallbacks.clear()
        self.__onClickCallbacks = None
        super(WotAnniversaryEntryPointWidget, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(WotAnniversaryEntryPointWidget, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def __updateModel(self):
        self.__onClickCallbacks.clear()
        if not self.__wotAnniversaryCtrl.isAvailable():
            return
        allQuests = self.__wotAnniversaryCtrl.getQuests()
        isDailyQuestUpdated, isDailyQuestDone, hasDailyQuest = self.__findAndProcessDailyQuest(allQuests)
        isWeeklyQuestUpdated, isWeeklyQuestDone, hasWeeklyQuest = self.__findAndProcessWeeklyQuest(allQuests)
        with self.viewModel.transaction() as tx:
            if all((isDailyQuestDone, isWeeklyQuestDone)):
                state = State.DONE if self.__wotAnniversaryCtrl.isLastDayNow() else State.NOQUESTS
            elif any((isDailyQuestUpdated, isWeeklyQuestUpdated)):
                state = State.NEWQUESTS
            elif not any((hasDailyQuest, hasWeeklyQuest)):
                state = State.NOQUESTS
            else:
                state = State.INPROGRESS
            tx.setState(state)
            self.__updateBalance(model=tx)

    @replaceNoneKwargsModel
    def __updateBalance(self, model=None):
        eventCoins = self.__itemsCache.items.stats.eventCoin if self.__wallet.isAvailable else -1
        model.setBalance(eventCoins)

    def __findAndProcessDailyQuest(self, quests):
        quest = quests.get(self.__wotAnniversaryCtrl.getDailyQuestName())
        isQuestUpdated = False
        if quest is None:
            return (isQuestUpdated, False, False)
        else:
            questID = quest.getID()
            prevQuestID, questUpdateTime = getWotAnniversarySectionSetting(WOT_ANNIVERSARY_SEEN_DAILY_QUEST)
            nextGameDay = time_utils.getCurrentLocalServerTimestamp() + EventInfoModel.getDailyProgressResetTimeDelta()
            if prevQuestID != questID or questUpdateTime < time_utils.getCurrentLocalServerTimestamp():
                isQuestUpdated = True
                self.__onClickCallbacks[State.NEWQUESTS].append(partial(setWotAnniversarySectionSetting, WOT_ANNIVERSARY_SEEN_DAILY_QUEST, (questID, nextGameDay)))
            return (isQuestUpdated, quest.isCompleted(), True)

    def __findAndProcessWeeklyQuest(self, quests):
        isQuestDone = False
        isQuestUpdated = False
        hasQuest = False
        _, weeklyQuest = findWeeklyQuest(quests)
        if weeklyQuest is not None:
            hasQuest = True
            questID = weeklyQuest.getID()
            isQuestDone = weeklyQuest.isCompleted()
            prevQuestID = getWotAnniversarySectionSetting(WOT_ANNIVERSARY_SEEN_WEEKLY_QUEST)
            if prevQuestID != questID:
                isQuestUpdated = True
                self.__onClickCallbacks[State.NEWQUESTS].append(partial(setWotAnniversarySectionSetting, WOT_ANNIVERSARY_SEEN_WEEKLY_QUEST, questID))
        return (isQuestUpdated, isQuestDone, hasQuest)

    def __onWidgetClick(self):
        self.__updateWidgetState()
        if not self.__settingsCore.serverSettings.getSection(SETTINGS_SECTIONS.WOT_ANNIVERSARY_STORAGE).get(WotAnniversaryStorageKeys.WOT_ANNIVERSARY_INTRO_SHOWED):
            showWotAnniversaryIntroWindow(closeCallback=showMainView)
            return
        showMainView()

    def __onSettingChanged(self):
        self.__updateModel()

    def __onTokensUpdate(self, _):
        self.__updateModel()

    def __onWalletStatusChanged(self, _):
        self.__updateBalance()

    def __onBalanceChanged(self, _):
        self.__updateBalance()

    def __updateWidgetState(self, *_):
        state = self.viewModel.getState()
        isStateUpdated = False
        while self.__onClickCallbacks[state]:
            isStateUpdated = True
            callback = self.__onClickCallbacks[state].pop()
            callback()

        if isStateUpdated:
            self.__updateModel()
