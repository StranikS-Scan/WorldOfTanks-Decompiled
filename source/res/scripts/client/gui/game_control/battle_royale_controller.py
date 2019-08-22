# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/battle_royale_controller.py
import logging
from collections import defaultdict
import typing
import BigWorld
import Event
import season_common
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR, ROYALE_VEHICLE, CURRENT_VEHICLE
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior, GRAPHICS
from adisp import process
from battle_royale_common import BR_TOKEN_FOR_TITLE
from constants import QUEUE_TYPE, Configs, PREBATTLE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.battle_royale.constants import ZERO_TITLE_ID, AmmoTypes, BattleRoyalePerfProblems
from gui.battle_royale.royale_helpers.stats_composer import BattleRoyaleStatsComposer
from gui.battle_royale.royale_models import DEFAULT_TITLE, TitleData, BattleRoyaleSeason, Title, ProgressEntityState, TitleStep, TitleProgress
from gui.game_control.br_vo_controller import BRVoiceOverController
from gui.periodic_battles.models import PrimeTime
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction, LeavePrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LoadViewEvent
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier, PeriodicNotifier
from helpers import dependency, time_utils
from helpers.statistics import HARDWARE_SCORE_PARAMS
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY
from season_provider import SeasonProvider
from shared_utils import collapseIntervals, first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.hangars_switcher import HangarNames
from skeletons.hangars_switcher import IHangarsSwitchManager
if typing.TYPE_CHECKING:
    from season_common import GameSeason
_logger = logging.getLogger(__name__)

class BATTLE_ROYALE_GAME_LIMIT_TYPE(object):
    SYSTEM_DATA = 0
    HARDWARE_PARAMS = 1


PERFORMANCE_GROUP_LIMITS = {BattleRoyalePerfProblems.HIGH_RISK: [{BATTLE_ROYALE_GAME_LIMIT_TYPE.SYSTEM_DATA: {'osBit': 1,
                                                                                   'graphicsEngine': 0}}, {BATTLE_ROYALE_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_MEMORY: 490}}, {BATTLE_ROYALE_GAME_LIMIT_TYPE.SYSTEM_DATA: {'graphicsEngine': 0},
                                       BATTLE_ROYALE_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_RAM: 2900}}],
 BattleRoyalePerfProblems.MEDIUM_RISK: [{BATTLE_ROYALE_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_SCORE: 150}}, {BATTLE_ROYALE_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_CPU_SCORE: 50000}}]}

class BattleRoyaleController(IBattleRoyaleController, Notifiable, SeasonProvider, IGlobalListener):
    __battleResultsService = dependency.descriptor(IBattleResultsService)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __hangarsSwitchMgr = dependency.descriptor(IHangarsSwitchManager)
    __hangarsSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(BattleRoyaleController, self).__init__()
        self.onUpdated = Event.Event()
        self.onGameModeStatusTick = Event.Event()
        self.onGameModeStatusUpdated = Event.Event()
        self._setSeasonSettingsProvider(self.__getCachedSettings)
        self.__clientValuesInited = False
        self.__clientTitle = DEFAULT_TITLE
        self.__clientShields = {}
        self.__clientMaxTitle = DEFAULT_TITLE
        self.__performanceGroup = None
        self.__titlesCache = []
        self.__serverSettings = None
        self.__battleRoyaleSettings = None
        self.__statsComposer = None
        self.__wasInLobby = False
        self.__wasInRoyaleMode = False
        self.__needToChangeSpace = False
        self.__equipmentCount = {}
        self.__voControl = BRVoiceOverController()
        return

    def init(self):
        super(BattleRoyaleController, self).init()
        self.addNotificator(SimpleNotifier(self.getTimer, self.__timerUpdate))
        self.addNotificator(PeriodicNotifier(self.getTimer, self.__timerTick))

    def fini(self):
        self.__voControl.destroy()
        self.__voControl = None
        self.__equipmentCount = None
        self.onUpdated.clear()
        self.onGameModeStatusTick.clear()
        self.onGameModeStatusUpdated.clear()
        self.clearNotification()
        super(BattleRoyaleController, self).fini()
        return

    def wasInLobby(self):
        return self.__wasInLobby

    def onLobbyInited(self, event):
        super(BattleRoyaleController, self).onLobbyInited(event)
        self.__statsComposer = BattleRoyaleStatsComposer(self.__battleRoyaleSettings)
        if not self.__clientValuesInited:
            self.__resizeTitlesCache(self.__battleRoyaleSettings)
            self.updateClientValues()
            self.__clientValuesInited = True
        g_clientUpdateManager.addCallbacks({'battleRoyale': self.__updateRoyale})
        self.startNotification()
        self.startGlobalListening()
        self.__hangarsSpace.onSpaceChangedByAction += self.__onSpaceChangedByAction
        if not self.__wasInLobby and self.isBattleRoyaleMode():
            if self.__hangarsSpace.spaceInited:
                self.__needToChangeSpace = True
            else:
                self.__hangarsSpace.onSpaceCreate += self.__onSpaceCreate
        self.__updateMode()
        self.__wasInLobby = True
        self.__wasInRoyaleMode = self.isBattleRoyaleMode()

    def onDisconnected(self):
        self.__wasInLobby = False
        self.__clearCaches()
        self.__clearClientValues()
        self.__clear()
        self.__voControl.onDisconnected()
        super(BattleRoyaleController, self).onDisconnected()

    def onConnected(self):
        super(BattleRoyaleController, self).onConnected()
        self.__voControl.onConnected()

    def onAccountBecomePlayer(self):
        self.__clearCaches()
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        self.__battleResultsService.onResultPosted += self.__showBattleResults
        super(BattleRoyaleController, self).onAccountBecomePlayer()

    def onAvatarBecomePlayer(self):
        self.__needToChangeSpace = False
        self.__clearCaches()
        self.__clear()
        self.__battleResultsService.onResultPosted -= self.__showBattleResults
        self.__voControl.onAvatarBecomePlayer()
        super(BattleRoyaleController, self).onAvatarBecomePlayer()

    def isAvailable(self):
        return self.isEnabled() and not self.isFrozen() and self.getCurrentSeason() is not None

    def isEnabled(self):
        return self.__battleRoyaleSettings.isEnabled

    def isAccountMastered(self):
        currentTitle, _ = self.__itemsCache.items.battleRoyale.accTitle
        return currentTitle == self.getMaxPossibleTitle()

    def isFrozen(self):
        peripheryPrimeTime = self.getPrimeTimes().get(self.__connectionMgr.peripheryID)
        return True if peripheryPrimeTime is not None and not peripheryPrimeTime.hasAnyPeriods() else False

    def getEndTime(self):
        return self.getCurrentSeason().getCycleEndDate() if self.isAvailable() else None

    def hasAnySeason(self):
        return bool(self.__battleRoyaleSettings.seasons)

    def hasAvailablePrimeTimeServers(self):
        if self.__connectionMgr.isStandalone():
            allPeripheryIDs = {self.__connectionMgr.peripheryID}
        else:
            allPeripheryIDs = set([ host.peripheryID for host in g_preDefinedHosts.hostsWithRoaming() ])
        for peripheryID in allPeripheryIDs:
            primeTimeStatus, _, _ = self.getPrimeTimeStatus(peripheryID)
            if primeTimeStatus == PrimeTimeStatus.AVAILABLE:
                return True

        return False

    def hasConfiguredPrimeTimeServers(self):
        peripheryIDs = self.__battleRoyaleSettings.peripheryIDs
        hostsList = self.__getHostList()
        avalaiblePeripheryIDS = []
        for _, _, _, _, peripheryID in hostsList:
            if peripheryID in peripheryIDs:
                avalaiblePeripheryIDS.append(peripheryID)

        if not avalaiblePeripheryIDS:
            return False
        primeTimes = self.__battleRoyaleSettings.primeTimes
        canShowPrimeTime = False
        for primeTime in primeTimes.itervalues():
            for pID in primeTime['peripheryIDs']:
                if pID not in avalaiblePeripheryIDS:
                    continue
                canShowPrimeTime = True

        return canShowPrimeTime

    def getClientTitle(self):
        return self.__clientTitle

    def getClientMaxTitle(self):
        return self.__clientMaxTitle

    def getCurrentSeason(self):
        now = time_utils.getCurrentLocalServerTimestamp()
        isCycleActive, seasonInfo = season_common.getSeason(self.__battleRoyaleSettings.asDict(), now)
        if isCycleActive:
            _, _, seasonID, _ = seasonInfo
            return self._createSeason(seasonInfo, self.__battleRoyaleSettings.seasons.get(seasonID, {}))
        else:
            return None

    def getCurrentTitle(self):
        return TitleData(*self.__itemsCache.items.battleRoyale.accTitle)

    def getMaxTitle(self):
        return TitleData(*self.__itemsCache.items.battleRoyale.maxTitle)

    def getMinPossibleTitle(self):
        return ZERO_TITLE_ID

    def getMaxPossibleTitle(self):
        return len(self.__battleRoyaleSettings.eventProgression.get('brPointsByTitle', ()))

    def getStatsComposer(self):
        return self.__statsComposer

    def getPerformanceGroup(self):
        if not self.__performanceGroup:
            self.__analyzeClientSystem()
            _logger.debug('Current performance group %s', self.__performanceGroup)
        return self.__performanceGroup

    def getPrimeTimeStatus(self, peripheryID=None):
        if peripheryID is None:
            peripheryID = self.__connectionMgr.peripheryID
        primeTime = self.getPrimeTimes().get(peripheryID)
        if primeTime is None:
            return (PrimeTimeStatus.NOT_SET, 0, False)
        elif not primeTime.hasAnyPeriods():
            return (PrimeTimeStatus.FROZEN, 0, False)
        else:
            season = self.getCurrentSeason()
            currTime = time_utils.getCurrentLocalServerTimestamp()
            if season and season.hasActiveCycle(currTime):
                isNow, timeTillUpdate = primeTime.getAvailability(currTime, season.getCycleEndDate())
            else:
                timeTillUpdate = 0
                if season:
                    nextCycle = season.getNextByTimeCycle(currTime)
                    if nextCycle:
                        primeTimeStart = primeTime.getNextPeriodStart(nextCycle.startDate, season.getEndDate(), includeBeginning=True)
                        if primeTimeStart:
                            timeTillUpdate = max(primeTimeStart, nextCycle.startDate) - currTime
                isNow = False
            return (PrimeTimeStatus.AVAILABLE, timeTillUpdate, isNow) if isNow else (PrimeTimeStatus.NOT_AVAILABLE, timeTillUpdate, False)

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        primeTimes = self.getPrimeTimes()
        dayStart, dayEnd = time_utils.getDayTimeBoundsForLocal(selectedTime)
        dayEnd += 1
        serversPeriodsMapping = {}
        hostsList = self.__getHostList()
        for _, _, serverShortName, _, peripheryID in hostsList:
            if peripheryID not in primeTimes:
                continue
            dayPeriods = primeTimes[peripheryID].getPeriodsBetween(dayStart, dayEnd)
            if groupIdentical and dayPeriods in serversPeriodsMapping.values():
                for name, period in serversPeriodsMapping.iteritems():
                    serverInMapping = name if period == dayPeriods else None
                    if serverInMapping:
                        newName = '{0}, {1}'.format(serverInMapping, serverShortName)
                        serversPeriodsMapping[newName] = serversPeriodsMapping.pop(serverInMapping)
                        break

            serversPeriodsMapping[serverShortName] = dayPeriods

        return serversPeriodsMapping

    def getPrimeTimes(self):
        primeTimes = self.__battleRoyaleSettings.primeTimes
        peripheryIDs = self.__battleRoyaleSettings.peripheryIDs
        primeTimesPeriods = defaultdict(lambda : defaultdict(list))
        for primeTime in primeTimes.itervalues():
            period = (primeTime['start'], primeTime['end'])
            weekdays = primeTime['weekdays']
            for pID in primeTime['peripheryIDs']:
                if pID not in peripheryIDs:
                    continue
                periphery = primeTimesPeriods[pID]
                for wDay in weekdays:
                    periphery[wDay].append(period)

        return {pID:PrimeTime(pID, {wDay:collapseIntervals(periods) for wDay, periods in pPeriods.iteritems()}) for pID, pPeriods in primeTimesPeriods.iteritems()}

    def getTitle(self, titleID):
        return self.getCachedTitlesChain(titleID, titleID)[titleID]

    def getCachedTitlesChain(self, leftRequiredBorder=None, rightRequiredBorder=None):
        leftRequiredBorder = leftRequiredBorder or self.getMinPossibleTitle()
        rightRequiredBorder = rightRequiredBorder or self.getMaxPossibleTitle()
        leftRequiredBorder = max(self.getMinPossibleTitle(), leftRequiredBorder)
        rightRequiredBorder = min(self.getMaxPossibleTitle(), rightRequiredBorder)
        invalidTitlesIDs = set()
        for titleID in range(leftRequiredBorder, rightRequiredBorder + 1):
            if self.__titlesCache[titleID] is None:
                invalidTitlesIDs.add(titleID)

        if invalidTitlesIDs:
            currentProgress = self.getCurrentTitle()
            lastProgress = self.getClientTitle()
            maxProgress = self.getMaxTitle()
            for titleID in invalidTitlesIDs:
                self.__titlesCache[titleID] = self.__createTitle(currentProgress, lastProgress, maxProgress, titleID)

        return self.__titlesCache[:]

    def getTitlesChainExt(self, currentProgress, lastProgress, maxProgress):
        cacheCopy = self.__titlesCache[:]
        leftRequiredBorder = max(self.getMinPossibleTitle(), min(lastProgress.title, currentProgress.title))
        rightRequiredBorder = min(self.getMaxPossibleTitle(), max(lastProgress.title, currentProgress.title) + 1)
        for titleID in range(leftRequiredBorder, rightRequiredBorder + 1):
            cacheCopy[titleID] = self.__createTitle(currentProgress, lastProgress, maxProgress, titleID)

        return cacheCopy

    def getUnburnableTitles(self):
        return self.__battleRoyaleSettings.eventProgression.get('unburnableTitles', ())

    def getSoloStepsTop(self):
        return self.__battleRoyaleSettings.eventProgression.get('brPointsChangesByPlace', ())

    def getSquadStepsTop(self):
        return self.__battleRoyaleSettings.eventProgression.get('brPointsChangesBySquadPlace', ())

    def getTimer(self):
        primeTimeStatus, timeLeft, _ = self.getPrimeTimeStatus()
        if primeTimeStatus != PrimeTimeStatus.AVAILABLE and not self.__connectionMgr.isStandalone():
            allPeripheryIDs = set([ host.peripheryID for host in g_preDefinedHosts.hostsWithRoaming() ])
            for peripheryID in allPeripheryIDs:
                peripheryStatus, peripheryTime, _ = self.getPrimeTimeStatus(peripheryID)
                if peripheryStatus == PrimeTimeStatus.NOT_AVAILABLE and peripheryTime < timeLeft:
                    timeLeft = peripheryTime

        seasonsChangeTime = self.getClosestStateChangeTime()
        currTime = time_utils.getCurrentLocalServerTimestamp()
        if seasonsChangeTime and (currTime + timeLeft > seasonsChangeTime or timeLeft == 0):
            timeLeft = seasonsChangeTime - currTime
        return timeLeft + 1 if timeLeft > 0 else time_utils.ONE_MINUTE

    def showBattleRoyalePage(self, ctx):
        if self.isEnabled():
            if not self.isBattleRoyaleMode() and self.isAvailable():
                self.selectRoyaleBattle()
            if not self.__isWelcomeViewProcessed():
                g_eventBus.handleEvent(LoadViewEvent(BATTLEROYALE_ALIASES.BATTLE_ROYALE_INTRO_ALIAS, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
            else:
                g_eventBus.handleEvent(LoadViewEvent(BATTLEROYALE_ALIASES.BATTLE_ROYALE_MAIN_PAGE_ALIAS, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)

    def updateClientValues(self):
        titleChanges = self.__clientTitle != self.getCurrentTitle()
        maxTitleChanges = self.__clientMaxTitle != self.getMaxTitle()
        shouldFlushCache = titleChanges or maxTitleChanges
        if shouldFlushCache:
            self.__partialFlushTitlesCache()
        self.__clientTitle = self.getCurrentTitle()
        self.__clientMaxTitle = self.getMaxTitle()

    def getDefaultAmmoCount(self, itemKey, intCD=None):
        if itemKey in (AmmoTypes.BASIC_SHELL, AmmoTypes.PREMIUM_SHELL):
            return self.__equipmentCount[itemKey]
        return self.__equipmentCount[itemKey].get(intCD, 0) if itemKey == AmmoTypes.ITEM else 0

    @property
    def voiceoverController(self):
        return self.__voControl

    def isBattleRoyaleMode(self):
        dispatcher = self.prbDispatcher
        if dispatcher is not None:
            state = dispatcher.getFunctionalState()
            return state.isInPreQueue(queueType=QUEUE_TYPE.BATTLE_ROYALE) or state.isInUnit(PREBATTLE_TYPE.BATTLE_ROYALE)
        else:
            return False

    def isInBattleRoyaleSquad(self):
        dispatcher = self.prbDispatcher
        if dispatcher is not None:
            state = dispatcher.getFunctionalState()
            return state.isInUnit(PREBATTLE_TYPE.BATTLE_ROYALE)
        else:
            return False

    def onPrbEntitySwitched(self):
        isInRoyaleMode = self.isBattleRoyaleMode()
        self.__needToChangeSpace = isInRoyaleMode != self.__wasInRoyaleMode
        self.__wasInRoyaleMode = isInRoyaleMode
        self.__updateMode()

    def selectRoyaleBattle(self):
        if self.isEnabled():
            dispatcher = g_prbLoader.getDispatcher()
            if dispatcher is None:
                _logger.error('Prebattle dispatcher is not defined')
                return
            self.__doSelectBattleRoyalePrb(dispatcher)
        return

    def selectRandomBattle(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            _logger.error('Prebattle dispatcher is not defined')
            return
        else:
            self.__doSelectRandomPrb(dispatcher)
            return

    def _createSeason(self, cycleInfo, seasonData):
        return BattleRoyaleSeason(cycleInfo, seasonData)

    def __onSpaceChangedByAction(self):
        if self.isBattleRoyaleMode():
            self.__needToChangeSpace = False
            self.__wasInRoyaleMode = False
            self.selectRandomBattle()

    def __onSpaceCreate(self):
        if self.isBattleRoyaleMode():
            self.__hangarsSpace.onSpaceCreate -= self.__onSpaceCreate
            BigWorld.callback(0.0, self.__switchToRoyalHangar)

    def __switchToRoyalHangar(self):
        self.__hangarsSwitchMgr.changeHangar(HangarNames.BATTLE_ROYALE)

    def __updateMode(self):
        if self.isBattleRoyaleMode():
            self.__enableRoyaleMode(self.__needToChangeSpace)
        else:
            self.__disableRoyaleMode(self.__needToChangeSpace)

    def __enableRoyaleMode(self, needToSwitchHangar):
        royaleVehicleID = AccountSettings.getFavorites(ROYALE_VEHICLE)
        if not royaleVehicleID:
            criteria = REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.BATTLE_ROYALE]) | REQ_CRITERIA.INVENTORY
            royaleVehicle = first(self.__itemsCache.items.getVehicles(criteria=criteria).values())
            if royaleVehicle:
                royaleVehicleID = royaleVehicle.invID
        if royaleVehicleID:
            g_currentVehicle.selectVehicle(royaleVehicleID)
        else:
            g_currentVehicle.selectNoVehicle()
        if needToSwitchHangar:
            self.__hangarsSwitchMgr.changeHangar(HangarNames.BATTLE_ROYALE)
        self.__voControl.activate()

    def __disableRoyaleMode(self, needToSwitchHangar):
        storedVehInvID = AccountSettings.getFavorites(CURRENT_VEHICLE)
        if not storedVehInvID:
            criteria = REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.BATTLE_ROYALE])
            vehicle = first(self.__itemsCache.items.getVehicles(criteria=criteria).values())
            if vehicle:
                storedVehInvID = vehicle.invID
        if storedVehInvID:
            g_currentVehicle.selectVehicle(storedVehInvID)
        else:
            g_currentVehicle.selectNoVehicle()
        if needToSwitchHangar:
            self.__hangarsSwitchMgr.changeHangar(HangarNames.FESTIVAL)
        self.__voControl.deactivate()

    @process
    def __doSelectBattleRoyalePrb(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.BATTLE_ROYALE))

    @process
    def __doSelectRandomPrb(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))

    @process
    def fightClick(self):
        dispatcher = g_prbLoader.getDispatcher()
        if not dispatcher:
            return
        lobbyContext = dependency.instance(ILobbyContext)
        navigationPossible = yield lobbyContext.isHeaderNavigationPossible()
        fightButtonPressPossible = yield lobbyContext.isFightButtonPressPossible()
        if navigationPossible and fightButtonPressPossible:
            if dispatcher:
                dispatcher.doAction(PrbAction(PREBATTLE_ACTION_NAME.BATTLE_ROYALE))
            else:
                _logger.error('Prebattle dispatcher is not defined')

    @process
    def _doLeaveBattleRoyalePrb(self, dispatcher):
        if dispatcher is None:
            return
        else:
            yield dispatcher.doLeaveAction(LeavePrbAction())
            return

    def __getBattleRoyaleSettings(self):
        generalSettings = self.__serverSettings.battleRoyale
        cycleID = None
        now = time_utils.getCurrentLocalServerTimestamp()
        _, cycleInfo = season_common.getSeason(generalSettings.asDict(), now)
        if cycleInfo:
            _, _, _, cycleID = cycleInfo
        for season in generalSettings.seasons.values():
            if cycleID in season.get('cycles', {}):
                return generalSettings.replace(season).replace(season['cycles'][cycleID])

        return generalSettings

    @staticmethod
    def __buildProgress(titleID, stepsCount, currentProgress, maxProgress, lastProgress):
        result = []
        for stepID in range(1, stepsCount + 1):
            stepState = ProgressEntityState.UNDEFINED
            stepUniqueID = (titleID - 1, stepID)
            if stepUniqueID < currentProgress:
                stepState |= ProgressEntityState.ACQUIRED
                if stepUniqueID > lastProgress:
                    stepState |= ProgressEntityState.NEW_FOR_PLAYER
            elif stepUniqueID == currentProgress:
                stepState |= ProgressEntityState.ACQUIRED | ProgressEntityState.CURRENT
                if stepUniqueID > lastProgress:
                    stepState |= ProgressEntityState.NEW_FOR_PLAYER
            else:
                stepState |= ProgressEntityState.NOT_ACQUIRED
                if stepUniqueID <= lastProgress:
                    stepState |= ProgressEntityState.NEW_FOR_PLAYER
            if currentProgress < stepUniqueID <= maxProgress:
                stepState |= ProgressEntityState.LOST
            result.append(TitleStep(titleID, stepState))

        return TitleProgress(result) if result else None

    @staticmethod
    def __buildTitleStatus(titleID, currentProgress, maxProgress, lastProgress):
        currentTitle, _ = currentProgress
        maxTitle, _ = maxProgress
        lastTitle, _ = lastProgress
        titleState = ProgressEntityState.UNDEFINED
        if titleID < currentTitle:
            titleState |= ProgressEntityState.ACQUIRED
            if titleID > lastTitle:
                titleState |= ProgressEntityState.NEW_FOR_PLAYER
        elif titleID == currentTitle:
            titleState |= ProgressEntityState.ACQUIRED | ProgressEntityState.CURRENT
            if titleID != lastTitle:
                titleState |= ProgressEntityState.NEW_FOR_PLAYER
        else:
            titleState |= ProgressEntityState.NOT_ACQUIRED
            if titleID <= lastTitle:
                titleState |= ProgressEntityState.NEW_FOR_PLAYER
        if currentTitle < titleID <= maxTitle:
            titleState |= ProgressEntityState.LOST
        return titleState

    def __getCachedSettings(self):
        return self.__battleRoyaleSettings

    def __getHostList(self):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        if self.__connectionMgr.isStandalone():
            hostsList.insert(0, (self.__connectionMgr.url,
             self.__connectionMgr.serverUserName,
             self.__connectionMgr.serverUserNameShort,
             HOST_AVAILABILITY.IGNORED,
             0))
        return hostsList

    def __getQuestForTitle(self, titleId):
        return first(self.__eventsCache.getHiddenQuests(lambda q: q.getID() == BR_TOKEN_FOR_TITLE.format(title=titleId)).values())

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onGameModeStatusUpdated(status)

    def __timerTick(self):
        self.onGameModeStatusTick()

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()
        self.__timerTick()

    def __resizeTitlesCache(self, settings):
        self.__titlesCache = [ None for _ in settings.eventProgression.get('brPointsByTitle', ()) ]
        self.__titlesCache.append(None)
        return

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateRoyaleSettings
        self.__serverSettings = serverSettings
        self.__battleRoyaleSettings = self.__getBattleRoyaleSettings()
        self.__updateEquipmentCount()
        self.__serverSettings.onServerSettingsChange += self.__updateRoyaleSettings
        return

    def __partialFlushTitlesCache(self):
        leftFlushBorder = min(self.__clientTitle.title, self.getCurrentTitle().title)
        leftFlushBorder = max(ZERO_TITLE_ID, leftFlushBorder)
        rightFlushBorder = max(self.__clientTitle.title, self.getCurrentTitle().title) + 1
        rightFlushBorder = min(self.getMaxPossibleTitle(), rightFlushBorder)
        for titleID in range(leftFlushBorder, rightFlushBorder + 1):
            self.__titlesCache[titleID] = None

        return

    def __showBattleResults(self, *_):
        self.updateClientValues()

    def __updateRoyaleSettings(self, diff):
        if Configs.BATTLE_ROYALE_CONFIG not in diff:
            return
        else:
            self.__battleRoyaleSettings = self.__getBattleRoyaleSettings()
            self.__updateEquipmentCount()
            self.__statsComposer = BattleRoyaleStatsComposer(self.__battleRoyaleSettings)
            self.__resizeTitlesCache(self.__battleRoyaleSettings)
            self.__divisions = None
            self.onUpdated()
            self.__resetTimer()
            return

    def __clear(self):
        self.stopNotification()
        self.stopGlobalListening()
        self.__hangarsSpace.onSpaceChangedByAction -= self.__onSpaceChangedByAction
        self.__hangarsSpace.onSpaceCreate -= self.__onSpaceCreate
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __clearCaches(self):
        self.__titlesCache = [ None for _ in self.__titlesCache ]
        return

    def __clearClientValues(self):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateRoyaleSettings
        self.__serverSettings = None
        self.__clientTitle = DEFAULT_TITLE
        self.__clientMaxTitle = DEFAULT_TITLE
        self.__clientValuesInited = False
        if self.__statsComposer:
            self.__statsComposer.clear()
            self.__statsComposer = None
        return

    def __createTitle(self, currentProgress, lastProgress, maxProgress, titleID):
        stepsToProgress = self.__battleRoyaleSettings.eventProgression.get('brPointsByTitle', ())
        titleIdx = titleID - 1
        stepsCount = stepsToProgress[titleIdx] if titleIdx >= self.getMinPossibleTitle() else 0
        title = Title(titleID, self.__buildTitleStatus(titleID, currentProgress, maxProgress, lastProgress), self.__buildProgress(titleID, stepsCount, currentProgress, maxProgress, lastProgress), quest=self.__getQuestForTitle(titleID))
        return title

    def __updateRoyale(self, _):
        self.__partialFlushTitlesCache()
        self.onUpdated()
        self.__resetTimer()

    def __isWelcomeViewProcessed(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        filters = self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        return filters[GuiSettingsBehavior.BATTLE_ROYALE_WELCOME_VIEW_SHOWED]

    def __analyzeClientSystem(self):
        stats = BigWorld.wg_getClientStatistics()
        stats['graphicsEngine'] = self.__settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE)
        self.__performanceGroup = BattleRoyalePerfProblems.LOW_RISK
        for groupName, conditions in PERFORMANCE_GROUP_LIMITS.iteritems():
            for currentLimit in conditions:
                condValid = True
                systemStats = currentLimit.get(BATTLE_ROYALE_GAME_LIMIT_TYPE.SYSTEM_DATA, {})
                for key, limit in systemStats.iteritems():
                    currValue = stats.get(key, None)
                    if currValue is None or currValue != limit:
                        condValid = False

                hardwareParams = currentLimit.get(BATTLE_ROYALE_GAME_LIMIT_TYPE.HARDWARE_PARAMS, {})
                for key, limit in hardwareParams.iteritems():
                    currValue = BigWorld.getAutoDetectGraphicsSettingsScore(key)
                    if currValue >= limit:
                        condValid = False

                if condValid:
                    self.__performanceGroup = groupName
                    return

        return

    def __updateEquipmentCount(self):
        if self.__equipmentCount:
            self.__equipmentCount = None
        items = self.__battleRoyaleSettings.defaultAmmo
        self.__equipmentCount = {AmmoTypes.BASIC_SHELL: 0,
         AmmoTypes.PREMIUM_SHELL: 0,
         AmmoTypes.ITEM: defaultdict(lambda : 0)}
        for itemGroup in items:
            groupKey, groupItems = itemGroup
            if groupKey in (AmmoTypes.BASIC_SHELL, AmmoTypes.PREMIUM_SHELL):
                self.__equipmentCount[groupKey] = groupItems[0]
            itemCD = groupItems[0]
            self.__equipmentCount[groupKey][itemCD] += 1

        return
