# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/tab_screen.py
import logging
import BattleReplay
import BigWorld
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from ReplayEvents import g_replayEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SELECTED_QUEST_IN_REPLAY
from account_helpers.settings_core.options import QuestsProgressViewType
from account_helpers.settings_core.settings_constants import QUESTS_PROGRESS
from gui.impl import backport
from gui.Scaleform.daapi.view.meta.TabScreenMeta import TabScreenMeta
from gui.Scaleform.genConsts.QUESTSPROGRESS import QUESTSPROGRESS
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles, icons
from gui.battle_control.battle_constants import TabsAliases
from helpers import dependency
from helpers.i18n import makeString
from gui.impl.gen import R
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from uilogging.player_satisfaction_rating.loggers import BattleTeamStatsViewLogger
_logger = logging.getLogger(__name__)

class TabScreenComponent(TabScreenMeta):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(TabScreenComponent, self).__init__()
        self._uiPlayerSatisfactionRatingLogger = BattleTeamStatsViewLogger()
        self.__tabsMap = {}

    @property
    def hasTabs(self):
        return True

    def hasTab(self, alias):
        return alias in self.__tabsMap

    def setActiveTab(self, tabAlias):
        if tabAlias is None:
            self.as_resetActiveTabS()
        else:
            index = self.__tabsMap.get(tabAlias)
            if index is None:
                _logger.error("FullStatsComponent doesn't have %s tab", tabAlias)
            else:
                self.as_setActiveTabS(index)
        return

    def onStatsTableVisibiltyToggled(self, isVisible):
        if isVisible:
            self._uiPlayerSatisfactionRatingLogger.onViewInitialize()
        else:
            self._uiPlayerSatisfactionRatingLogger.onViewFinalize()

    def onSelectQuest(self, questID):
        qProgressCtrl = self.sessionProvider.shared.questProgress
        qProgressCtrl.selectQuest(questID)
        self.__setQuestTrackingData()

    def _populate(self):
        super(TabScreenComponent, self)._populate()
        tabs = self._buildTabs(_TabsBuilder())
        for idx, tabData in enumerate(tabs):
            self.__tabsMap[tabData['alias']] = idx
            tabData['alias'] = tabData['alias'].value

        self.as_updateTabsS(tabs)
        qProgressCtrl = self.sessionProvider.shared.questProgress
        self.__settingsCore.onSettingsChanged += self.__onSettingsChange
        if qProgressCtrl is not None:
            qProgressCtrl.onQuestProgressInited += self.__onQuestProgressInited
            if qProgressCtrl.isInited():
                self.__setNoQuestsDescription()
                self.__setQuestTrackingData()
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart += self.__onReplayTimeWarpStart
            g_replayEvents.onTimeWarpFinish += self.__onReplayTimeWarpFinished
        return

    @staticmethod
    def _buildTabs(builder):
        builder.addStatisticsTab()
        builder.addPersonalQuestsTab()
        builder.addBoostersTab()
        return builder.getTabs()

    def _dispose(self):
        super(TabScreenComponent, self)._dispose()
        self.__tabsMap = {}
        qProgressCtrl = self.sessionProvider.shared.questProgress
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChange
        if qProgressCtrl is not None:
            qProgressCtrl.onQuestProgressInited -= self.__onQuestProgressInited
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart -= self.__onReplayTimeWarpStart
            g_replayEvents.onTimeWarpFinish -= self.__onReplayTimeWarpFinished
        return

    def onToggleVisibility(self, isVisible):
        self._onToggleVisibility(isVisible)

    def _onToggleVisibility(self, isVisible):
        if not isVisible:
            qProgressCtrl = self.sessionProvider.shared.questProgress
            if qProgressCtrl:
                qProgressCtrl.showQuestProgressAnimation()

    def __onQuestProgressInited(self):
        self.__setNoQuestsDescription()
        self.__setQuestTrackingData()

    def __onReplayTimeWarpFinished(self):
        questID = AccountSettings.getSettings(SELECTED_QUEST_IN_REPLAY)
        if questID:
            self.onSelectQuest(questID)
        AccountSettings.setSettings(SELECTED_QUEST_IN_REPLAY, questID)

    def __onReplayTimeWarpStart(self):
        quest = self.sessionProvider.shared.questProgress.getSelectedQuest()
        questID = None
        if quest:
            questID = quest.getID()
        AccountSettings.setSettings(SELECTED_QUEST_IN_REPLAY, questID)
        return

    def __onSettingsChange(self, diff):
        if QUESTS_PROGRESS.VIEW_TYPE in diff:
            self.__setQuestTrackingData()

    def __setQuestTrackingData(self):
        questProgress = self.sessionProvider.shared.questProgress
        selectedQuest = questProgress.getSelectedQuest()
        progressViewType = self.__settingsCore.getSetting(QUESTS_PROGRESS.VIEW_TYPE)
        isProgressTrackingEnabled = progressViewType == QuestsProgressViewType.TYPE_STANDARD
        trackingData = []
        personalMissions = self.__eventsCache.getPersonalMissions()
        for quest in sorted(questProgress.getInProgressQuests().itervalues(), key=lambda q: q.getQuestBranch()):
            isSelected = quest == selectedQuest
            operation = personalMissions.getOperationsForBranch(quest.getQuestBranch())[quest.getOperationID()]
            trackingData.append({'eyeBtnVisible': isProgressTrackingEnabled and isSelected,
             'selected': isSelected,
             'missionName': makeString(quest.getShortUserName()),
             'fullMissionName': makeString(quest.getUserName()),
             'operationName': makeString(operation.getShortUserName()),
             'vehicle': QUESTSPROGRESS.getOperationTrackingIcon(operation.getID()),
             'questID': quest.getID(),
             'onPause': quest.isOnPause})

        trackingStatus = ''
        if len(trackingData) > 1:
            trackingStatus = ''.join((icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_NOTIFICATIONS_OFF, 16, 16, -2, 0), ' ', text_styles.standard(PERSONAL_MISSIONS.QUESTPROGRESSTRACKING_TRACKINGSTATUS)))
        self.as_updateProgressTrackingS({'trackingStatus': trackingStatus,
         'trackingData': trackingData})

    def __setNoQuestsDescription(self):
        settings = self.__lobbyContext.getServerSettings()
        questProgress = self.sessionProvider.shared.questProgress
        if questProgress.areQuestsEnabledForArena():
            if not settings.isPMBattleProgressEnabled():
                self.as_questProgressPerformS({'hasQuestToPerform': False,
                 'noQuestTitle': text_styles.promoSubTitle(INGAME_GUI.STATISTICS_TAB_QUESTS_SWITCHOFF_TITLE),
                 'noQuestDescr': ''})
            else:
                self.as_questProgressPerformS({'hasQuestToPerform': questProgress.hasQuestsToPerform(),
                 'noQuestTitle': text_styles.promoSubTitle(INGAME_GUI.STATISTICS_TAB_QUESTS_NOTHINGTOPERFORM_TITLE),
                 'noQuestDescr': text_styles.highlightText(INGAME_GUI.STATISTICS_TAB_QUESTS_NOTHINGTOPERFORM_DESCR)})
        else:
            self.as_questProgressPerformS({'hasQuestToPerform': False,
             'noQuestTitle': text_styles.promoSubTitle(INGAME_GUI.STATISTICS_TAB_QUESTS_NOTAVAILABLE_TITLE),
             'noQuestDescr': ''})


class _TabsBuilder(object):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__tabs = []

    def addStatisticsTab(self):
        self.__tabs.append({'label': backport.text(R.strings.ingame_gui.statistics.tab.line_up.header()),
         'alias': TabsAliases.STATS})

    def addPersonalQuestsTab(self):
        if self.__lobbyContext.getServerSettings().isPersonalMissionsEnabled():
            self.__tabs.append({'label': backport.text(R.strings.ingame_gui.statistics.tab.quests.header()),
             'alias': TabsAliases.QUESTS_PROGRESS})

    def addBoostersTab(self):
        if self.__isBoosterProcessingAvailable():
            self.__tabs.append({'label': backport.text(R.strings.ingame_gui.statistics.tab.personalReserves.header()),
             'alias': TabsAliases.BOOSTERS})

    def getTabs(self):
        return self.__tabs

    def __isBoosterProcessingAvailable(self):
        return self.__lobbyContext.getServerSettings().personalReservesConfig.isReservesInBattleActivationEnabled and BigWorld.player().hasBonusCap(ARENA_BONUS_TYPE_CAPS.BOOSTERS)
