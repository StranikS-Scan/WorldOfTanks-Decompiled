# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/quest_progress/quest_progress_ctrl.py
import logging
import BigWorld
from Event import EventManager, Event
from constants import ARENA_PERIOD
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_control.arena_info.interfaces import IArenaPeriodController, IArenaVehiclesController
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.server_events.cond_formatters.mixed_formatters import PM1BattleConditionsFormatterAdapter
from gui.server_events.personal_progress.formatters import DetailedProgressFormatter
from gui.server_events.personal_progress.storage import BattleProgressStorage
from helpers import dependency
from personal_missions import PM_STATE
from shared_utils import first
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)

class QuestProgressController(IArenaPeriodController, IArenaVehiclesController):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(QuestProgressController, self).__init__()
        self._period = ARENA_PERIOD.IDLE
        self._endTime = 0
        self._length = 0
        self._callbackID = None
        self.__storage = {}
        self.__selectedQuest = None
        self.__eManager = EventManager()
        self.__battleCtx = None
        self.__isInited = False
        self.__inProgressQuests = {}
        self.onConditionProgressUpdate = Event(self.__eManager)
        self.onHeaderProgressesUpdate = Event(self.__eManager)
        self.onFullConditionsUpdate = Event(self.__eManager)
        self.onQuestProgressInited = Event(self.__eManager)
        return

    def getInProgressQuests(self):
        return self.__inProgressQuests

    def hasQuestsToPerform(self):
        return bool(self.__inProgressQuests)

    def getSelectedQuest(self):
        return self.__selectedQuest

    def isInited(self):
        return self.__isInited

    def selectQuest(self, missionID):
        self.__selectedQuest = self.__inProgressQuests.get(missionID)
        self.onFullConditionsUpdate()

    def invalidateArenaInfo(self):
        isPersonalMissionsEnabled = self.lobbyContext.getServerSettings().isPersonalMissionsEnabled
        if not self.__isInited:
            personalMissions = self.eventsCache.getPersonalMissions()
            selectedMissionsIDs = self.__battleCtx.getSelectedQuestIDs()
            selectedMissionsInfo = self.__battleCtx.getSelectedQuestInfo() or {}
            if selectedMissionsIDs:
                missions = personalMissions.getAllQuests()
                for missionID in selectedMissionsIDs:
                    mission = missions.get(missionID)
                    if mission and not mission.isDisabled() and isPersonalMissionsEnabled(mission.getQuestBranch()):
                        pqState = selectedMissionsInfo.get(missionID, (0, PM_STATE.NONE))[1]
                        mission.updatePqStateInBattle(pqState)
                        self.__inProgressQuests[missionID] = mission
                        if mission.hasBattleProgress():
                            generalQuestID = mission.getGeneralQuestID()
                            self.__selectedQuest = mission
                            self.__storage[generalQuestID] = BattleProgressStorage(generalQuestID, mission.getConditionsConfig(), mission.getConditionsProgress())

                if self.__selectedQuest is None:
                    self.__selectedQuest = first(self.__inProgressQuests.itervalues())
                self.__updateTimerConditions(sendDiff=False)
            self.__isInited = True
            self.onQuestProgressInited()
        return

    def startControl(self, battleCtx, arenaVisitor):
        self.__battleCtx = battleCtx

    def areQuestsEnabledForArena(self):
        return self.__battleCtx.areQuestsEnabledForArena()

    def stopControl(self):
        self._period = ARENA_PERIOD.IDLE
        self._endTime = 0
        self._length = 0
        self.__selectedQuest = None
        self.__battleCtx = None
        self.__storage.clear()
        self.__eManager.clear()
        self.__clearCallback()
        self.__inProgressQuests.clear()
        self.__isInited = False
        return

    def setPeriodInfo(self, period, endTime, length, additionalInfo, soundID):
        self.__updatePeriodInfo(period, endTime, length)

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        self.__updatePeriodInfo(period, endTime, length)

    def getQuestFullData(self):
        selectedQuest = self.__selectedQuest
        if selectedQuest:
            formatter = self.__getFormatter(selectedQuest)
            return {'questName': selectedQuest.getUserName(),
             'questID': selectedQuest.getID(),
             'questIndexStr': str(selectedQuest.getInternalID()),
             'questIcon': RES_ICONS.getAllianceGoldIcon(selectedQuest.getMajorTag()),
             'headerProgress': formatter.headerFormat(),
             'bodyProgress': formatter.bodyFormat()}
        return {}

    def getQuestHeaderProgresses(self):
        formatter = self.__getFormatter(self.__selectedQuest)
        return formatter.headerFormat()

    def updateQuestProgress(self, questID, info):
        if questID in self.__storage:
            self.__storage[questID].update(info)
        else:
            _logger.error('Storage for quest:%s is not found.', questID)
        selectedQuest = self.__selectedQuest
        if selectedQuest is not None and selectedQuest.hasBattleProgress():
            storage = self.__storage[selectedQuest.getGeneralQuestID()]
            needHeaderResync = False
            for headerProgress in storage.getHeaderProgresses().itervalues():
                if headerProgress.isChanged():
                    needHeaderResync = True
                    headerProgress.markAsVisited()

            if needHeaderResync:
                self.onHeaderProgressesUpdate()
            for progressID, condProgress in storage.getChangedConditions().iteritems():
                condProgress.markAsVisited()
                self.onConditionProgressUpdate(progressID, condProgress.getProgress())

        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.QUEST_PROGRESS

    def getCtrlScope(self):
        return _SCOPE.PERIOD | _SCOPE.VEHICLES

    def __updatePeriodInfo(self, period, endTime, length):
        self._period = period
        self._endTime = endTime
        self._length = length
        self.__clearCallback()
        if self._period == ARENA_PERIOD.BATTLE:
            self.__setCallback()

    def __setCallback(self):
        self._callbackID = None
        battleEndLeftTime = self._endTime - BigWorld.serverTime()
        tickInterval = 1 if battleEndLeftTime > 1 else 0
        self.__updateTimerConditions()
        self._callbackID = BigWorld.callback(tickInterval, self.__setCallback)
        return

    def __clearCallback(self):
        if self._callbackID is not None:
            BigWorld.cancelCallback(self._callbackID)
            self._callbackID = None
        return

    def __updateTimerConditions(self, sendDiff=True):
        selectedQuest = self.__selectedQuest
        hasProgress = selectedQuest and selectedQuest.hasBattleProgress()
        if self._period == ARENA_PERIOD.BATTLE and hasProgress:
            startTime = self._endTime - self._length
            timesGoneFromStart = BigWorld.serverTime() - startTime
            timerConditions = self.__storage[selectedQuest.getGeneralQuestID()].getTimerConditions()
            for progressID, condProgress in timerConditions.iteritems():
                secondsLeft = max(condProgress.getCountDown() - timesGoneFromStart, 0)
                isChanged = condProgress.setTimeLeft(secondsLeft)
                if isChanged and sendDiff:
                    self.onConditionProgressUpdate(progressID, condProgress.getProgress())

    def __getFormatter(self, selectedQuest):
        return DetailedProgressFormatter(self.__storage.get(selectedQuest.getGeneralQuestID()), selectedQuest) if selectedQuest.hasBattleProgress() else PM1BattleConditionsFormatterAdapter(selectedQuest)


def createQuestProgressController():
    return QuestProgressController()
