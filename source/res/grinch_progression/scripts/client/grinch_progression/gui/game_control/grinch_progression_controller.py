# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/game_control/grinch_progression_controller.py
import logging
from account_helpers import AccountSyncData
from grinch_progression.account_helpers.account_settings import getCompletedQuests, setCompletedQuests
from grinch_progression.account_helpers.grinch_cache_manager import PDATA_KEY, GrinchCacheManager
from grinch_progression.gui.shared.gui_items.processors.processors import OpenStepForChapter
from grinch_progression.skeletons.game_controller import IGrinchProgressionController
from grinch_progression_common.grinch_progression_constants import Configs, ProgressionStates
from helpers.time_utils import getServerUTCTime
import Event
from GrinchProgressionAccountSettings import getSettings, setSettings, PREVIOUS_POINTS_COUNT, IS_FIRST_ENTRY
from PlayerEvents import g_playerEvents
from adisp import adisp_process, adisp_async
from grinch.skeletons.battle_controller import IGrinchController
from gui.periodic_battles.models import PeriodType
from helpers.CallbackDelayer import CallbackDelayer
from helpers import dependency, time_utils
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
_logger = logging.getLogger(__name__)

class CurrentStepHelper(object):

    def __init__(self, chapters):
        super(CurrentStepHelper, self).__init__()
        self.__chapters = chapters

    def getNextStep(self, currStepID, currChapterID):
        chapter = self.__chapters.get(currChapterID, {})
        if currStepID < len(chapter.get('steps', [])):
            return (currStepID + 1, currChapterID)
        return (1, currChapterID + 1) if currChapterID < len(self.__chapters.keys()) else None


class GrinchProgressionController(IGrinchProgressionController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __grinchCtrl = dependency.descriptor(IGrinchController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self):
        super(GrinchProgressionController, self).__init__()
        self.__callbackDelayer = CallbackDelayer()
        self.__grinchConfig = None
        self.__grinchCacheManager = GrinchCacheManager()
        self._prevState = False
        self.onDataUpdated = Event.Event()
        return

    def onLobbyInited(self, event):
        self._prevState = self.isEnabled
        self.__resetCompletedQuests()
        self.__setUpdateTimer()

    def fini(self):
        self.__callbackDelayer.clearCallbacks()
        self.__grinchConfig = None
        return

    def onAccountBecomePlayer(self):
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__grinchCtrl.onConfigChanged += self.__updateGrinchConfig
        self.__grinchCtrl.onPrimeTimeStatusUpdated += self.__onUpdatePrimeTime

    def onAccountBecomeNonPlayer(self):
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__grinchCtrl.onConfigChanged -= self.__updateGrinchConfig
        self.__grinchCtrl.onPrimeTimeStatusUpdated -= self.__onUpdatePrimeTime

    def onDisconnected(self):
        self.__grinchCacheManager.onDisconnected()

    @property
    def isEnabled(self):
        return self.__grinchConfig['isEnabled']

    @property
    def token(self):
        return self.getConfig().get('progressionTokenID')

    def getNextChapterID(self):
        chaptersData = self.getCurrentSeasonChapters()
        currentTime = getServerUTCTime()
        lastChapter = 0
        for chapterId, chapterData in chaptersData.iteritems():
            lastChapter = chapterId
            if chapterData['chapterStart'] > currentTime:
                return chapterId

        return lastChapter

    @property
    def enoughForClaimReward(self):
        if not self.__anyRewardsLeft():
            return False
        currentStepHelper = CurrentStepHelper(self.getActiveChapters())
        curChapterID, stepID = self.getCurrentChapterStep()
        res = currentStepHelper.getNextStep(stepID, curChapterID)
        if not res:
            return False
        nextStepID, nextChapterID = res
        chapter = self.getActiveChapters()[nextChapterID]
        nextStep = chapter.get('steps').get(nextStepID)
        if not nextStep:
            return False
        nextStepPrice = nextStep.get('price', 0)
        return False if not nextStepPrice else self.getPoints() >= nextStepPrice

    def getProgressionState(self):
        timeTill = self.getTimeTillSeasonStart()
        if timeTill or not self.isEnabled:
            return ProgressionStates.NOT_STARTED
        periodInfo = self.__grinchCtrl.getPeriodInfo()
        if periodInfo.periodType != PeriodType.BETWEEN_SEASONS:
            if self.getIsCurrentLastChapter() and not self.__anyRewardsLeft():
                return ProgressionStates.FINISHED
            return ProgressionStates.IN_PROGRESS
        return ProgressionStates.OFF_CHAPTER

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().getSettings().get(Configs.GRINCH_PROGRESSION_CONFIG.value)

    def getPoints(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.token)

    def getTimeTillSeasonStart(self):
        timeTill = self.getStartEventDate() - getServerUTCTime()
        return 0 if timeTill < 0 else timeTill

    def getCurrentChapter(self):
        chaptersData = self.getCurrentSeasonChapters()
        currentTime = getServerUTCTime()
        maxChapter = 0
        for chapterId, chapterData in chaptersData.iteritems():
            if chapterData['chapterStart'] < currentTime < chapterData['chapterFinish']:
                if chapterId > maxChapter:
                    maxChapter = chapterId

        return maxChapter

    def getTimeTillNextChapterStart(self):
        chaptersData = self.getCurrentSeasonChapters()
        currentTime = getServerUTCTime()
        for _, chapterData in chaptersData.iteritems():
            if currentTime < chapterData['chapterStart']:
                return chapterData['chapterStart'] - currentTime

    def getTimeTillNextBattlesStart(self):
        nearestSeason = self.__grinchCtrl.getNextSeason()
        if not nearestSeason:
            return 0
        nearestTimeCycle = nearestSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
        if not nearestTimeCycle:
            return 0
        timeTill = nearestTimeCycle.startDate - getServerUTCTime()
        return 0 if timeTill < 0 else timeTill

    def getStartEventDate(self):
        seasonData = self.__getCurrentSeasonData()
        return seasonData['seasonStart'] if seasonData else 0

    def getEndEventDate(self):
        seasonData = self.__getCurrentSeasonData()
        return seasonData['seasonFinish'] if seasonData else 0

    def getCurrentSeasonChapters(self):
        return self.__getCurrentSeasonData().get('chapters', {})

    def getActiveChapters(self):
        chaptersData = self.getCurrentSeasonChapters()
        currentTime = getServerUTCTime()
        result = dict()
        for chapterID, chapterData in chaptersData.iteritems():
            if chapterData['chapterStart'] < currentTime < chapterData['chapterFinish']:
                result[chapterID] = chapterData

        return result

    def getGrinchVehicles(self):
        return self.__grinchConfig.get('vehicles', [])

    def getChapterDates(self, chapterId):
        chaptersData = self.getCurrentSeasonChapters()
        chapterData = chaptersData.get(chapterId)
        return (chapterData['chapterStart'], chapterData['chapterFinish'])

    def getMaxChapterStep(self):
        chaptersSteps = [ len(chapterData['steps']) for chapterData in self.getCurrentSeasonChapters().itervalues() ]
        return max(chaptersSteps)

    def getPreviousPointsCount(self):
        return getSettings(PREVIOUS_POINTS_COUNT)

    def setPreviousPointsCount(self, value):
        return setSettings(PREVIOUS_POINTS_COUNT, value)

    def getIsFirstEntry(self):
        return getSettings(IS_FIRST_ENTRY)

    def setIsFirstEntry(self, value):
        return setSettings(IS_FIRST_ENTRY, value)

    def getCurrentChapterStep(self):
        lastCupterID = self.__grinchCacheManager.getLastChapterID() or 1
        lastStepID = self.__grinchCacheManager.getLastStepID()
        chapters = self.getActiveChapters()
        if self.__grinchCacheManager.getLastChapterID() < 1:
            return (1, lastStepID)
        chapterSteps = self.getActiveChapters()[lastCupterID].get('steps')
        return (lastCupterID, lastStepID) if lastStepID < len(chapterSteps) or lastCupterID == len(chapters) else (lastCupterID + 1, 0)

    def getIsCurrentLastChapter(self):
        return self.__grinchCacheManager.getLastChapterID() == len(self.getCurrentSeasonChapters())

    @adisp_async
    @adisp_process
    def moveToNextStep(self, callback):
        if not self.isEnabled or not self.__anyRewardsLeft():
            return
        helper = CurrentStepHelper(self.getActiveChapters())
        curChapterID, stepID = self.getCurrentChapterStep()
        getNextStepRes = helper.getNextStep(stepID, curChapterID)
        if not getNextStepRes:
            _logger.error("Couldn't find the next step")
            return
        nextStepID, nextChapterID = getNextStepRes
        chapter = self.getActiveChapters()[nextChapterID]
        nextStep = chapter.get('steps')[nextStepID]
        nextStepPrice = nextStep.get('price', 0)
        if not nextStepPrice:
            _logger.error('Step ID: %s has no price', nextStepID)
            return
        if not self.enoughForClaimReward:
            _logger.error('Not enough tokens for step')
            return
        result = yield OpenStepForChapter(nextChapterID, nextStepID).request()
        callback(result)

    def __getCurrentSeasonData(self):
        config = self.getConfig()
        currentTime = getServerUTCTime()
        firstNotStartedSeason = {}
        for _, seasonData in config.get('seasons').iteritems():
            if not firstNotStartedSeason and currentTime < seasonData['seasonStart']:
                firstNotStartedSeason = seasonData
            if seasonData['seasonStart'] < currentTime < seasonData['seasonFinish']:
                return seasonData

        return firstNotStartedSeason

    def __anyChapterAvailable(self):
        chaptersData = self.getCurrentSeasonChapters()
        currentTime = getServerUTCTime()
        for _, chapterData in chaptersData.iteritems():
            if chapterData['chapterStart'] < currentTime < chapterData['chapterFinish']:
                return True

        return False

    def __anyRewardsLeft(self):
        curChapterID, stepID = self.getCurrentChapterStep()
        chapters = self.getActiveChapters()
        chapterSteps = self.getActiveChapters().get(curChapterID, {}).get('steps', [])
        return not (stepID == len(chapterSteps) and curChapterID == len(chapters))

    def __updateGrinchConfig(self, _):
        self.__grinchConfig = self.__grinchCtrl.getConfig()
        self.onDataUpdated()

    def __onClientUpdated(self, diff, _):
        isFullSync = AccountSyncData.isFullSyncDiff(diff)
        self.__grinchCacheManager.synchronize(isFullSync, diff)
        if PDATA_KEY in diff:
            self.onDataUpdated()

    def __onServerSettingsChange(self, diff):
        if Configs.GRINCH_PROGRESSION_CONFIG.value in diff:
            self.onDataUpdated()

    def __onUpdatePrimeTime(self, *_):
        self.onDataUpdated()
        self.__setUpdateTimer()

    def __resetCompletedQuests(self):
        completedQuests = getCompletedQuests()
        resetedSet = set()
        for qID in completedQuests:
            quest = self.__eventsCache.getQuestByID(qID)
            if quest.isCompleted():
                resetedSet.add(qID)

        setCompletedQuests(resetedSet)

    def __setUpdateTimer(self):
        timeLeft = self.__grinchCtrl.getClosestStateChangeTime() - time_utils.getCurrentLocalServerTimestamp()
        if timeLeft > 0:
            self.__callbackDelayer.delayCallback(timeLeft, self.__onUpdatePrimeTime)
