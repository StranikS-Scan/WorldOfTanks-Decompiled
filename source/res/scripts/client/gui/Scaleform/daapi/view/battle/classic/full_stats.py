# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/full_stats.py
import BattleReplay
from ReplayEvents import g_replayEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SELECTED_QUEST_IN_REPLAY
from account_helpers.settings_core.options import QuestsProgressViewType
from account_helpers.settings_core.settings_constants import QUESTS_PROGRESS
from constants import ARENA_GUI_TYPE
from gui.Scaleform.daapi.view.meta.ClassicFullStatsMeta import ClassicFullStatsMeta
from gui.Scaleform.genConsts.QUESTSPROGRESS import QUESTSPROGRESS
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles, icons
from helpers import dependency
from helpers.i18n import makeString
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache

class FullStatsComponent(ClassicFullStatsMeta):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def onSelectQuest(self, questID):
        qProgressCtrl = self.sessionProvider.shared.questProgress
        qProgressCtrl.selectQuest(questID)
        self.__setQuestTrackingData()

    def _populate(self):
        super(FullStatsComponent, self)._populate()
        qProgressCtrl = self.sessionProvider.shared.questProgress
        self.__settingsCore.onSettingsChanged += self.__onSettingsChange
        guiType = self.sessionProvider.arenaVisitor.getArenaGuiType()
        self.as_isFDEventS(guiType == ARENA_GUI_TYPE.EVENT_BATTLES)
        if qProgressCtrl is not None:
            qProgressCtrl.onQuestProgressInited += self.__onQuestProgressInited
            if qProgressCtrl.isInited():
                self.__setNoQuestsDescription()
                self.__setQuestTrackingData()
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart += self.__onReplayTimeWarpStart
            g_replayEvents.onTimeWarpFinish += self.__onReplayTimeWarpFinished
        return

    def _dispose(self):
        super(FullStatsComponent, self)._dispose()
        qProgressCtrl = self.sessionProvider.shared.questProgress
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChange
        if qProgressCtrl is not None:
            qProgressCtrl.onQuestProgressInited -= self.__onQuestProgressInited
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart -= self.__onReplayTimeWarpStart
            g_replayEvents.onTimeWarpFinish -= self.__onReplayTimeWarpFinished
        return

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
