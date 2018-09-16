# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/ranked_battles_controller.py
import operator
from collections import defaultdict
from operator import itemgetter
import BigWorld
import Event
import constants
import ranked_common
from adisp import async, process
from constants import ARENA_BONUS_TYPE, EVENT_TYPE
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.awards_formatters import getRankedQuestsOrderedAwards
from gui.ranked_battles.constants import PRIME_TIME_STATUS
from gui.ranked_battles.ranked_models import RankedSeason, Rank, VehicleRank, RANK_STATE, RankStep, RankProgress, RankedDossier
from gui.ranked_battles.ranked_models import PrimeTime, RANK_CHANGE_STATES
from debug_utils import LOG_WARNING
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.shared import event_dispatcher, events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, time_utils
from items import vehicles
from optional_bonuses import TrackVisitor, BONUS_MERGERS, walkBonuses
from shared_utils import first, findFirst, collapseIntervals
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.web import IWebController
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY

class RankedBattlesController(IRankedBattlesController, Notifiable):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    battleResultsService = dependency.descriptor(IBattleResultsService)
    connectionMgr = dependency.descriptor(IConnectionManager)
    clansController = dependency.descriptor(IWebController)

    def __init__(self):
        super(RankedBattlesController, self).__init__()
        self.onUpdated = Event.Event()
        self.onPrimeTimeStatusUpdated = Event.Event()
        self.__arenaBattleResultsWasShown = set()
        self.__awardWindowWasShown = False
        self.__fakeWebLeague = None
        return

    def init(self):
        super(RankedBattlesController, self).init()
        self.addNotificator(SimpleNotifier(self.__getTimer, self.__timerUpdate))

    def fini(self):
        self.onUpdated.clear()
        self.onPrimeTimeStatusUpdated.clear()
        self.clearNotification()
        super(RankedBattlesController, self).fini()

    def onDisconnected(self):
        self.__clear()

    def onAccountBecomePlayer(self):
        self.battleResultsService.onResultPosted += self.__showBattleResults

    def onAvatarBecomePlayer(self):
        self.__clear()
        self.battleResultsService.onResultPosted -= self.__showBattleResults

    def onLobbyStarted(self, ctx):
        lobbyContext = dependency.instance(ILobbyContext)
        lobbyContext.getServerSettings().onServerSettingsChange += self.__updateRankedSettings
        g_clientUpdateManager.addCallbacks({'ranked': self.__updateRanked})
        self.startNotification()

    def isEnabled(self):
        return self.__getSettings().isEnabled

    def isFrozen(self):
        peripheryPrimeTime = self.getPrimeTimes().get(self.connectionMgr.peripheryID)
        return True if peripheryPrimeTime is not None and not peripheryPrimeTime.hasAnyPeriods() else False

    def isAvailable(self):
        return self.isEnabled() and not self.isFrozen() and self.getCurrentSeason() is not None

    def hasAnySeason(self):
        return bool(self.__getSettings().seasons)

    def getCurrentCycleID(self):
        isCurrent, seasonInfo = ranked_common.getRankedSeason(self.__getSettings().asDict())
        if isCurrent:
            _, _, _, cycleID = seasonInfo
            return cycleID
        else:
            return None

    def getSeasonPassed(self):
        now = time_utils.getServerRegionalTime()
        settings = self.__getSettings()
        seasonsPassed = []
        for seasonID, season in settings.seasons.iteritems():
            endSeason = season['endSeason']
            if now > endSeason:
                seasonsPassed.append((seasonID, endSeason))

        return seasonsPassed

    def getPreviousSeason(self):
        seasonsPassed = self.getSeasonPassed()
        if seasonsPassed:
            seasonID, _ = max(seasonsPassed, key=operator.itemgetter(1))
            return self.getSeason(seasonID)
        else:
            return None

    def getCurrentSeason(self):
        settings = self.__getSettings()
        isCurrent, seasonInfo = ranked_common.getRankedSeason(settings.asDict())
        if isCurrent:
            _, _, seasonID, _ = seasonInfo
            currPoints = self.getLadderPoints()
            return RankedSeason(seasonInfo, settings.seasons.get(seasonID, {}), self.__getRankedDossier(), currPoints)
        else:
            return None

    def getLadderPoints(self):
        return self.itemsCache.items.ranked.ladderPoints

    def getNextSeason(self):
        now = time_utils.getServerRegionalTime()
        settings = self.__getSettings()
        seasonsComing = []
        for seasonID, season in settings.seasons.iteritems():
            startSeason = season['startSeason']
            if now < startSeason:
                seasonsComing.append((seasonID, startSeason))

        if seasonsComing:
            seasonID, _ = min(seasonsComing, key=operator.itemgetter(1))
            return self.getSeason(seasonID)
        else:
            return None

    def getSeason(self, seasonID):
        seasonData = self.__getSettings().seasons.get(seasonID, {})
        if seasonData:
            cycleInfo = (None,
             None,
             seasonID,
             None)
            return RankedSeason(cycleInfo, seasonData, self.__getRankedDossier())
        else:
            return

    def getRank(self, rankID, vehicle=None):
        return self.getAllRanksChain(vehicle)[rankID]

    def getCurrentRank(self, vehicle=None):
        if vehicle is not None:
            result = findFirst(operator.methodcaller('isCurrent'), self.getVehicleRanksChain(vehicle))
            if result is not None:
                return result
        return findFirst(operator.methodcaller('isCurrent'), self.getRanksChain())

    def getMaxRank(self, vehicle=None):
        if vehicle is not None:
            result = findFirst(operator.methodcaller('isMax'), self.getVehicleRanksChain(vehicle))
            if result is not None:
                return result
        return findFirst(operator.methodcaller('isMax'), self.getRanksChain())

    def getMaxRankForCycle(self, cycleID):
        season = self.getCurrentSeason()
        if season is None:
            return
        elif cycleID == season.getCycleID():
            resultCD = None
            maxVehRank = (0, 0)
            for vehCD, rank in self.itemsCache.items.ranked.vehRanks.iteritems():
                if resultCD is None or rank > maxVehRank:
                    resultCD = vehCD

            if resultCD is not None:
                vehicle = Vehicle(strCompactDescr=vehicles.getVehicleTypeCompactDescr(resultCD))
            else:
                vehicle = None
            return self.getMaxRank(vehicle)
        else:
            cycleDossier = self.__getDossierForCycle(cycleID, seasonID=season.getSeasonID())
            rankID, vehicleRank = cycleDossier.rank, cycleDossier.vehRankCount
            if vehicleRank > 0:
                return VehicleRank(None, rankID, vehicleRank, RANK_STATE.UNDEFINED, 0)
            return Rank(rankID, RANK_STATE.UNDEFINED, 0)
            return

    def getLastRank(self, vehicle=None):
        if vehicle is not None:
            result = findFirst(operator.methodcaller('isLastSeenByPlayer'), self.getVehicleRanksChain(vehicle))
            if result is not None:
                return result
        return findFirst(operator.methodcaller('isLastSeenByPlayer'), self.getRanksChain())

    def setLastRank(self, vehicle=None):
        currentProgress = self.itemsCache.items.ranked.accRank
        lastProgress = self.itemsCache.items.ranked.clientRank
        if currentProgress != lastProgress:
            BigWorld.player().ranked.setClientRank(*currentProgress)
        if vehicle is not None:
            vehCD = vehicle.intCD
            currentProgress = self.itemsCache.items.ranked.vehRanks.get(vehCD, (0, 0))
            lastProgress = self.itemsCache.items.ranked.clientVehRanks.get(vehCD, (0, 0))
            if currentProgress != lastProgress:
                BigWorld.player().ranked.setClientVehRank(vehCD, *currentProgress)
        return

    def setLastShields(self):
        rank = self.getCurrentRank()
        shieldStatus = self.getShieldStatus(rank=rank)
        if shieldStatus:
            _, shieldHp, _, _, _ = shieldStatus
            BigWorld.player().ranked.setClientShields([rank.getID(), shieldHp])

    @async
    @process
    def getLeagueData(self, callback):
        if not self.__fakeWebLeague or not constants.IS_DEVELOPMENT:
            if self.clansController.getAccountProfile():
                result = yield self.clansController.getClanDossier().requestRankedPosition()
                if result is not None:
                    result = result.get('results')
            else:
                result = None
        else:
            result = self.__fakeWebLeague
        callback(result)
        return

    def getLeagueAwards(self):
        isCurrent, seasonInfo = ranked_common.getRankedSeason(self.__getSettings().asDict())
        result = []
        percentTotal = 0
        if isCurrent:
            _, _, seasonID, _ = seasonInfo
            seasonQuests = self.eventsCache.getHiddenQuests(lambda q: q.getType() == EVENT_TYPE.TOKEN_QUEST and ranked_helpers.isRankedQuestID(q.getID()))
            for qID in sorted(seasonQuests):
                season, cohort, percent = ranked_helpers.getRankedDataFromTokenQuestID(qID)
                percentTotal += percent
                if season == seasonID:
                    quest = seasonQuests[qID]
                    awards = []
                    for bonus in quest.getBonuses():
                        awards.extend(bonus.getRankedAwardVOs(iconSize='big'))

                    result.append({'cohortNumber': cohort,
                     'playersPercent': percent,
                     'awards': awards})

        result.append({'cohortNumber': 0,
         'playersPercent': 100 - percentTotal,
         'awards': []})
        return result

    def openWebLeaguePage(self, ctx=None):
        g_eventBus.handleEvent(events.LoadViewEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_BROWSER_VIEW, ctx=ctx), EVENT_BUS_SCOPE.LOBBY)

    def hasProgress(self):
        currentRank = self.getCurrentRank()
        return currentRank.getID() > 0 or currentRank.hasProgress()

    def getAccRanksTotal(self):
        return len(self.__getSettings().accSteps)

    def isAccountMastered(self):
        currentRank, _ = self.itemsCache.items.ranked.accRank
        return currentRank == self.getAccRanksTotal()

    def getConsolationQuest(self):
        return first(self.eventsCache.getRankedQuests(lambda q: not q.isHidden()).values())

    def getRanksChain(self):
        currentProgress = self.itemsCache.items.ranked.accRank
        maxProgress = self.itemsCache.items.ranked.maxRank
        lastProgress = self.itemsCache.items.ranked.clientRank
        return self.buildRanksChain(currentProgress, maxProgress, lastProgress)

    def getVehicleRanksChain(self, vehicle):
        rankedStats = self.itemsCache.items.ranked
        vehCD = vehicle.intCD if vehicle is not None else None
        currentProgress = rankedStats.vehRanks.get(vehCD, (0, 0))
        maxProgress = rankedStats.maxVehRanks.get(vehCD, (0, 0))
        lastProgress = rankedStats.clientVehRanks.get(vehCD, (0, 0))
        return self.buildVehicleRanksChain(currentProgress, maxProgress, lastProgress, vehicle)

    def getAllRanksChain(self, vehicle=None):
        result = self.getRanksChain()
        if vehicle is not None:
            result.extend(self.getVehicleRanksChain(vehicle))
        return result

    def buildRanksChain(self, currentProgress, maxProgress, lastProgress):
        _, _ = currentProgress
        settings = self.__getSettings()
        stepsToProgress = settings.accSteps
        unburnableRanks = settings.unburnableRanks
        unburnableStepRanks = settings.unburnableStepRanks
        points = settings.accLadderPts
        result = [Rank(*self.__buildRank(0, 0, currentProgress, maxProgress, lastProgress, unburnableRanks, unburnableStepRanks, points))]
        maxAccRank = self.getAccRanksTotal()
        for rankID, stepsCount in enumerate(stepsToProgress, 1):
            quest = self.__getQuestForRank(rankID)
            finalQuest = self.__getQuestForMaxRank(rankID)
            result.append(Rank(quest=quest, finalQuest=finalQuest, isMaxAccRank=(rankID == maxAccRank), *self.__buildRank(rankID, stepsCount, currentProgress, maxProgress, lastProgress, unburnableRanks, unburnableStepRanks, points)))

        return result

    def buildVehicleRanksChain(self, currentProgress, maxProgress, lastProgress, vehicle):
        currentRank, _ = currentProgress
        settings = self.__getSettings()
        vehStepsToProgress = settings.vehSteps
        vehTotalStepsCount = len(vehStepsToProgress)
        unburnableRanks = settings.unburnableVehRanks
        unburnableVehStepRanks = settings.unburnableVehStepRanks
        points = settings.vehLadderPts
        accTopRankID = self.getAccRanksTotal()
        result = []
        quest = self.getVehicleQuestForCycle(self.getCurrentCycleID())
        for rankIdx, rankID in enumerate(xrange(1, currentRank + 2)):
            if rankIdx < vehTotalStepsCount:
                stepsCount = vehStepsToProgress[rankIdx]
            else:
                stepsCount = vehStepsToProgress[-1]
            if rankID > settings.vehRanks and settings.vehRanks in settings.unburnableVehRanks:
                unburnableRanks = set(settings.unburnableVehRanks)
                unburnableRanks.add(rankID)
            result.append(VehicleRank(vehicle, accTopRankID, quest=quest, *self.__buildRank(rankID, stepsCount, currentProgress, maxProgress, lastProgress, unburnableRanks, unburnableVehStepRanks, points)))

        return result

    def runQuests(self, quests):
        notCompletedQuests = []
        for quest in quests:
            if not quest.isCompleted():
                notCompletedQuests.append(quest.getID())
            LOG_WARNING('Quest is already completed: ', quest.getID())

        if notCompletedQuests:
            BigWorld.player().runQuest(EVENT_TYPE.RANKED_QUEST, notCompletedQuests, lambda *args: None)

    def getQuestsForCycle(self, cycleID, completedOnly=False):
        if completedOnly:
            if cycleID < self.getCurrentCycleID():
                maxRank = self.__getDossierForCycle(cycleID).rank
            else:
                maxRank = self.getMaxRank().getID()
        else:
            maxRank = len(self.__getSettings(cycleID).accSteps)
        return self.eventsCache.getRankedQuests(lambda q: q.isHidden() and q.getCycleID() == cycleID and q.isForRank() and q.getRank() <= maxRank)

    def getVehicleQuestForCycle(self, cycleID):
        return first(self.eventsCache.getRankedQuests(lambda q: q.isHidden() and q.getCycleID() == cycleID and q.isForVehicleMastering()).values())

    def getVehicleMastersCount(self, cycleID):
        if cycleID < self.getCurrentCycleID():
            result = self.__getDossierForCycle(cycleID).vehRankCount
        else:
            result = sum(map(itemgetter(0), self.itemsCache.items.ranked.maxVehRanks.values()))
        return result

    def awardWindowShouldBeShown(self, rankChangeInfo):
        if rankChangeInfo.stepChanges > 0:
            if rankChangeInfo.vehRank - rankChangeInfo.prevVehRank > 0:
                return True
            rankedData = self.itemsCache.items.ranked
            if rankedData.maxRankWithAwardReceived[0] < rankChangeInfo.accRank and rankedData.maxRank[0] == rankChangeInfo.accRank:
                return True
        return False

    @staticmethod
    def setAwardWindowShown(rankID):
        BigWorld.player().ranked.setClientMaxRank(rankID, 0)

    def wasAwardWindowShown(self):
        return self.__awardWindowWasShown

    def getRankChangeStatus(self, changeInfo):
        stepChanges = changeInfo.stepChanges
        stepToJudge = changeInfo.vehStep or changeInfo.accStep
        if stepChanges > 0:
            if changeInfo.accRank > changeInfo.prevAccRank:
                state = RANK_CHANGE_STATES.RANK_EARNED
            elif changeInfo.vehRank > changeInfo.prevVehRank:
                state = RANK_CHANGE_STATES.RANK_POINT
            elif stepChanges > 1:
                state = RANK_CHANGE_STATES.STEPS_EARNED
            else:
                state = RANK_CHANGE_STATES.STEP_EARNED
        elif stepChanges < 0:
            settings = self.__getSettings()
            if changeInfo.vehRank:
                if len(settings.vehSteps) > changeInfo.vehRank:
                    maxStepInRank = settings.vehSteps[changeInfo.vehRank]
                else:
                    maxStepInRank = settings.vehSteps[-1]
            else:
                currRank = changeInfo.accRank
                if currRank == self.getAccRanksTotal():
                    maxStepInRank = settings.vehSteps[0]
                else:
                    maxStepInRank = settings.accSteps[changeInfo.accRank]
            if stepToJudge == maxStepInRank - 1:
                state = RANK_CHANGE_STATES.RANK_LOST
            else:
                state = RANK_CHANGE_STATES.STEP_LOST
        else:
            state = RANK_CHANGE_STATES.NOTHING_CHANGED
        return state

    def getPrimeTimes(self):
        lobbyContext = dependency.instance(ILobbyContext)
        rankedBattlesConfig = lobbyContext.getServerSettings().rankedBattles
        primeTimes = rankedBattlesConfig.primeTimes
        peripheryIDs = rankedBattlesConfig.peripheryIDs
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

    def getPrimeTimeStatus(self, peripheryID=None):
        if not self.isEnabled():
            return (PRIME_TIME_STATUS.DISABLED, 0, False)
        else:
            if peripheryID is None:
                peripheryID = self.connectionMgr.peripheryID
            primeTimes = self.getPrimeTimes()
            hasAnyPeriods = False
            for pId in primeTimes:
                hasAnyPeriods = primeTimes[pId].hasAnyPeriods()
                if hasAnyPeriods:
                    break

            if not hasAnyPeriods:
                LOG_WARNING('RankedBattles enabled but primetimes did not have any period to play or they are frozen!')
            primeTime = primeTimes.get(peripheryID)
            if primeTime is None:
                if hasAnyPeriods:
                    return (PRIME_TIME_STATUS.NOT_SET, 0, False)
                LOG_WARNING('RankedBattles primetimes did not have playable period on pID:', peripheryID)
                return (PRIME_TIME_STATUS.DISABLED, 0, False)
            if not primeTime.hasAnyPeriods():
                return (PRIME_TIME_STATUS.FROZEN, 0, False)
            currentSeason = self.getCurrentSeason()
            if currentSeason is None:
                return (PRIME_TIME_STATUS.NO_SEASON, 0, False)
            isNow, timeLeft = primeTime.getAvailability(time_utils.getCurrentLocalServerTimestamp(), self.getCurrentSeason().getCycleEndDate())
            return (PRIME_TIME_STATUS.AVAILABLE, timeLeft, isNow) if isNow else (PRIME_TIME_STATUS.NOT_AVAILABLE, timeLeft, False)

    def hasAvailablePrimeTimeServers(self):
        if self.isAvailable():
            lobbyContext = dependency.instance(ILobbyContext)
            rankedBattlesConfig = lobbyContext.getServerSettings().rankedBattles
            peripheryIDs = rankedBattlesConfig.peripheryIDs
            hostsList = self.__getHostList()
            avalaiblePeripheryIDS = []
            for _, _, _, _, peripheryID in hostsList:
                if peripheryID in peripheryIDs:
                    avalaiblePeripheryIDS.append(peripheryID)

            if not avalaiblePeripheryIDS:
                if peripheryIDs:
                    LOG_WARNING('RankedBattles no any playable periphery! Peripheries setup:', peripheryIDs)
                return False
            primeTimes = rankedBattlesConfig.primeTimes
            canShowPrimeTime = False
            for primeTime in primeTimes.itervalues():
                for pID in primeTime['peripheryIDs']:
                    if pID not in avalaiblePeripheryIDS:
                        continue
                    canShowPrimeTime = True

            return canShowPrimeTime
        return False

    def hasAnyPeripheryWithPrimeTime(self):
        if not self.isAvailable():
            return False
        currentSeason = self.getCurrentSeason()
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        endTime = currentSeason.getCycleEndDate()
        for primeTime in self.getPrimeTimes().itervalues():
            if primeTime.hasAnyPeriods():
                isAvailable, _ = primeTime.getAvailability(currentTime, endTime)
                if isAvailable:
                    return True

        return False

    def getCycleRewards(self, cycleID):
        result = []
        maxRank = self.__getDossierForCycle(cycleID).rank
        quest = first(self.eventsCache.getRankedQuests(lambda q: q.getRank() == maxRank and q.getCycleID() == cycleID and q.isProcessedAtCycleEnd()).values())
        if quest is not None:
            for bonus in quest.getBonuses():
                if bonus.getName() == 'oneof':
                    awards = bonus.getRankedAwardVOs()
                    for awardVO in awards:
                        awardVO['tooltip'] = RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_AWARDBLOCK_BOXTOOLTIP
                        awardVO['align'] = BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT
                        result.insert(0, awardVO)

                result.extend(bonus.getRankedAwardVOs())

        return result

    def getAllAwardsForCycle(self, cycleID):
        resultDict = {}
        maxRank = self.__getDossierForCycle(cycleID).rank
        questsIterator = self.eventsCache.getRankedQuests(lambda q: q.getRank() == maxRank and q.getCycleID() == cycleID and q.isProcessedAtCycleEnd()).itervalues()
        for quest in questsIterator:
            qProgress = self.eventsCache.questsProgress.getQuestProgress(quest.getID()) or {}
            if qProgress:
                bonusTrack = qProgress.get(None, {}).get('bonusTracks', [''])[0]
                trackReplay = TrackVisitor(BONUS_MERGERS, bonusTrack, 1, None)
                trackResult = walkBonuses(quest.getData().get('bonus', {}), trackReplay)
                for bonus in quest.getBonuses(bonusData=trackResult):
                    for awardVO in bonus.getRankedAwardVOs(iconSize='big', withCounts=True, withKey=True):
                        itemKey = awardVO.pop('itemKey')
                        if itemKey in resultDict:
                            resultDict[itemKey]['count'] += awardVO['count']
                        resultDict[itemKey] = awardVO

        return resultDict

    def getRanksChanges(self, isLoser=False):
        settings = self.__getSettings()
        return settings.loserRankChanges if isLoser else settings.winnerRankChanges

    def getMinXp(self):
        settings = self.__getSettings()
        return settings.minXP

    def hasSuitableVehicles(self):
        minLevel, maxLevel = self.getSuitableVehicleLevels()
        vehLevels = range(minLevel, maxLevel + 1)
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(vehLevels))
        return len(vehs) > 0

    def getSuitableVehicleLevels(self):
        rankedConfigData = self.__getSettings()
        return (rankedConfigData.minLevel, rankedConfigData.maxLevel)

    def getShieldStatus(self, rank, isStatic=False):
        shieldsConfig = self.__getSettings().shields
        shields = self.itemsCache.items.ranked.shields
        prevShields = self.itemsCache.items.ranked.clientShields
        rankID = rank.getID()
        shieldConfig = shieldsConfig.get(rankID, None)
        if shieldConfig is not None:
            if isStatic:
                hp = shieldConfig[1]
                return (hp,
                 hp,
                 hp,
                 RANKEDBATTLES_ALIASES.SHIELD_ENABLED,
                 None)
            accShield = shields.get(rankID, None)
            _, maxHP = shieldConfig
            shieldState = RANKEDBATTLES_ALIASES.SHIELD_DISABLED
            newShieldState = None
            if not rank.isCurrent() and accShield is not None:
                hp, _ = accShield
                if hp > 0:
                    shieldState = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
                    newShieldState = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
                return (hp,
                 hp,
                 maxHP,
                 shieldState,
                 newShieldState)
            if accShield is not None:
                accPrevShieldHP = prevShields.get(rankID, None)
                hp, _ = accShield
                if accPrevShieldHP is None:
                    LOG_WARNING('Info about rank shield not available for', rankID, ' in clientShields')
                    accPrevShieldHP = hp
                if accPrevShieldHP == hp:
                    if hp > 0:
                        shieldState = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
                        newShieldState = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
                elif accPrevShieldHP < hp:
                    if accPrevShieldHP == 0:
                        shieldState = RANKEDBATTLES_ALIASES.SHIELD_FULL_RENEW
                        newShieldState = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
                    else:
                        shieldState = RANKEDBATTLES_ALIASES.SHIELD_RENEW
                        newShieldState = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
                elif accPrevShieldHP > hp:
                    if hp == 0:
                        shieldState = RANKEDBATTLES_ALIASES.SHIELD_LOSE
                        newShieldState = RANKEDBATTLES_ALIASES.SHIELD_DISABLED
                    else:
                        shieldState = RANKEDBATTLES_ALIASES.SHIELD_LOSE_STEP
                        newShieldState = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
                return (accPrevShieldHP,
                 hp,
                 maxHP,
                 shieldState,
                 newShieldState)
        return

    def getCurrentCycleStats(self):
        return self.itemsCache.items.getAccountDossier().getDossierDescr()['rankedCurrentCycle']

    def getRanksTops(self, isLoser=False, stepDiff=None):
        settings = self.__getSettings()
        rankChanges = settings.loserRankChanges if isLoser else settings.winnerRankChanges
        if stepDiff is None:
            return len(rankChanges)
        else:
            if stepDiff == RANKEDBATTLES_ALIASES.STEP_VALUE_EARN:
                total = sum((1 for i in rankChanges if i > 0))
            elif stepDiff == RANKEDBATTLES_ALIASES.STEP_VALUE_NO_CHANGE:
                total = sum((1 for i in rankChanges if i == 0))
            else:
                total = sum((1 for i in rankChanges if i < 0))
            return total

    def showRankedAwardWindow(self, rankInfo, vehicle, questsProgress):
        completedQuests = []
        rankID = rankInfo.vehRank + rankInfo.accRank

        def _filter(q):
            return ranked_helpers.isRankedQuestID(q.getID())

        quests = self.eventsCache.getHiddenQuests(filterFunc=_filter)
        for qID, qProgress in questsProgress.iteritems():
            _, pPrev, pCur = qProgress
            isCompleted = pCur.get('bonusCount', 0) - pPrev.get('bonusCount', 0) > 0
            if qID in quests and isCompleted:
                completedQuests.append(quests[qID])

        self.__awardWindowWasShown = True
        if completedQuests:
            event_dispatcher.showRankedAwardWindow(rankID, vehicle=vehicle, awards=getRankedQuestsOrderedAwards(completedQuests, size=AWARDS_SIZES.BIG))

    def setWebLeague(self, league=0, position=0):
        if constants.IS_DEVELOPMENT:
            self.__fakeWebLeague = {'league': league,
             'position': position}

    def __clear(self):
        lobbyContext = dependency.instance(ILobbyContext)
        lobbyContext.getServerSettings().onServerSettingsChange -= self.__updateRankedSettings
        self.stopNotification()
        g_clientUpdateManager.removeObjectCallbacks(self)

    @staticmethod
    def __getSettings(cycleID=None):
        lobbyContext = dependency.instance(ILobbyContext)
        generalSettings = lobbyContext.getServerSettings().rankedBattles
        if cycleID is None:
            _, cycleInfo = ranked_common.getRankedSeason(generalSettings.asDict())
            if cycleInfo:
                _, _, _, cycleID = cycleInfo
        for season in generalSettings.seasons.values():
            if cycleID in season.get('cycles', {}):
                return generalSettings.replace(season).replace(season['cycles'][cycleID])

        return generalSettings

    def __buildRank(self, rankID, stepsCount, currentProgress, maxProgress, lastProgress, unburnableRanks, unburnableStepRanks, points):
        currentRank, _ = currentProgress
        maxRank, _ = maxProgress
        lastRank, _ = lastProgress
        rankState = RANK_STATE.UNDEFINED
        if rankID < currentRank:
            rankState |= RANK_STATE.ACQUIRED
            if rankID > lastRank:
                rankState |= RANK_STATE.NEW_FOR_PLAYER
        elif rankID == currentRank:
            rankState |= RANK_STATE.ACQUIRED | RANK_STATE.CURRENT
            if rankID != lastRank:
                rankState |= RANK_STATE.NEW_FOR_PLAYER
        else:
            rankState |= RANK_STATE.NOT_ACQUIRED
            if rankID <= lastRank:
                rankState |= RANK_STATE.NEW_FOR_PLAYER
        if currentRank < rankID <= maxRank:
            rankState |= RANK_STATE.LOST
        if rankID == maxRank:
            rankState |= RANK_STATE.MAXIMUM
        if rankID in unburnableRanks:
            rankState |= RANK_STATE.UNBURNABLE
        if rankID == lastRank:
            rankState |= RANK_STATE.LAST_SEEN_BY_PLAYER
        progress = None
        if stepsCount:
            progress = self.__buildProgress(rankID, stepsCount, currentProgress, maxProgress, lastProgress, unburnableStepRanks)
        if rankID == 0:
            points = 0
        elif rankID <= len(points):
            points = points[rankID - 1]
        else:
            points = points[-1]
        return (rankID,
         rankState,
         points,
         progress)

    def __buildProgress(self, rankID, stepsCount, currentProgress, maxProgress, lastProgress, unburnableStepRanks):
        result = []
        for stepID in xrange(1, stepsCount + 1):
            stepState = RANK_STATE.UNDEFINED
            stepUniqueID = (rankID - 1, stepID)
            if stepUniqueID < currentProgress:
                stepState |= RANK_STATE.ACQUIRED
                if stepUniqueID > lastProgress:
                    stepState |= RANK_STATE.NEW_FOR_PLAYER
            elif stepUniqueID == currentProgress:
                stepState |= RANK_STATE.ACQUIRED | RANK_STATE.CURRENT
                if stepUniqueID > lastProgress:
                    stepState |= RANK_STATE.NEW_FOR_PLAYER
            else:
                stepState |= RANK_STATE.NOT_ACQUIRED
                if stepUniqueID <= lastProgress:
                    stepState |= RANK_STATE.NEW_FOR_PLAYER
            if currentProgress < stepUniqueID <= maxProgress:
                stepState |= RANK_STATE.LOST
            if stepUniqueID == maxProgress:
                stepState |= RANK_STATE.MAXIMUM
            if rankID in unburnableStepRanks:
                stepState |= RANK_STATE.UNBURNABLE
            if stepUniqueID == lastProgress:
                stepState |= RANK_STATE.LAST_SEEN_BY_PLAYER
            result.append(RankStep(stepID, stepState))

        return RankProgress(result)

    def __getQuestForRank(self, rankId):
        season = self.getCurrentSeason()
        return None if season is None else first(self.eventsCache.getRankedQuests(lambda q: q.getRank() == rankId and q.isHidden() and q.isForRank() and q.getSeasonID() == season.getSeasonID() and q.getCycleID() == season.getCycleID()).values())

    def __getQuestForMaxRank(self, rankId):
        season = self.getCurrentSeason()
        return None if season is None else first(self.eventsCache.getRankedQuests(lambda q: q.getRank() == rankId and q.isHidden() and q.isProcessedAtCycleEnd() and q.getSeasonID() == season.getSeasonID() and q.getCycleID() == season.getCycleID()).values())

    def __getRankedDossier(self):
        return self.itemsCache.items.getAccountDossier().getDossierDescr()['rankedSeasons']

    def __getDossierForCycle(self, cycleID, seasonID=None):
        cycleDossier = None
        if seasonID is None:
            season = self.getCurrentSeason()
            if season is not None:
                seasonID = season.getSeasonID()
        dossier = self.__getRankedDossier()
        if seasonID is not None:
            cycleDossier = dossier.get((seasonID, cycleID))
        return RankedDossier(*(cycleDossier or RankedDossier.defaults()))

    def __showBattleResults(self, reusableInfo, composer):
        arenaBonusType = reusableInfo.common.arenaBonusType
        arenaUniqueID = reusableInfo.arenaUniqueID
        if arenaBonusType == ARENA_BONUS_TYPE.RANKED and arenaUniqueID not in self.__arenaBattleResultsWasShown:
            rankInfo = reusableInfo.personal.getRankInfo()
            vehicle = first(reusableInfo.personal.getVehicleItemsIterator())[1]
            questsProgress = reusableInfo.personal.getQuestsProgress()
            rankedResultsVO = composer.getResultsTeamsVO()
            event_dispatcher.showRankedBattleResultsWindow(rankedResultsVO, vehicle, rankInfo, questsProgress)
            self.__arenaBattleResultsWasShown.add(reusableInfo.arenaUniqueID)
        else:
            LOG_WARNING('Ranked Overlay windows will not be shown, received arenaBonusType: ', arenaBonusType)

    def __updateRanked(self, diff):
        changes = set(diff.keys())
        changes -= {'clientRank', 'clientVehRanks', 'clientShields'}
        if changes:
            self.onUpdated()
            self.__resetTimer()

    def __updateRankedSettings(self, diff):
        if 'ranked_config' in diff:
            self.onUpdated()
            self.__resetTimer()

    def __getTimer(self):
        _, timeLeft, _ = self.getPrimeTimeStatus()
        return timeLeft + 1 if timeLeft > 0 else time_utils.ONE_MINUTE

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onPrimeTimeStatusUpdated(status)

    def __getHostList(self):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        if self.connectionMgr.isStandalone():
            hostsList.insert(0, (self.connectionMgr.url,
             self.connectionMgr.serverUserName,
             self.connectionMgr.serverUserNameShort,
             HOST_AVAILABILITY.IGNORED,
             0))
        return hostsList
