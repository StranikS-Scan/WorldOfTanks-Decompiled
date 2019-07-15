# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/epic_meta_game_ctrl.py
import logging
from itertools import chain
from collections import defaultdict
import BigWorld
import WWISE
import Event
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.game_control.links import URLMacros
from shared_utils import collapseIntervals, CONST_CONTAINER
from gui.periodic_battles.models import PrimeTime
from constants import ARENA_BONUS_TYPE, PREBATTLE_TYPE, QUEUE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import event_dispatcher, g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency, i18n, time_utils
from items import vehicles
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.connection_mgr import IConnectionManager
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE
from CurrentVehicle import g_currentVehicle
from items.vehicles import getVehicleClassFromVehicleType
from gui.shared.gui_items.vehicle_equipment import BattleAbilityConsumables
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import FUNCTIONAL_FLAG
from helpers.statistics import HARDWARE_SCORE_PARAMS
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY
from account_helpers.AccountSettings import AccountSettings, GUI_START_BEHAVIOR
from gui import DialogsInterface, GUI_SETTINGS
from adisp import async, process
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import GRAPHICS
from season_provider import SeasonProvider
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_cycle_helpers import getCurrentWelcomeScreenVersion
from player_ranks import getSettings as getRankSettings
_logger = logging.getLogger(__name__)
_VALID_PREBATTLE_TYPES = [PREBATTLE_TYPE.EPIC, PREBATTLE_TYPE.EPIC_TRAINING]

class FRONTLINE_SCREENS(CONST_CONTAINER):
    RESERVES_SCREEN = 'reserves/'
    REWARDS_SCREEN = 'rewards/'


def _showBrowserView(url):
    from gui.Scaleform.daapi.view.lobby.epicBattle.web_handlers import createFrontlineWebHandlers
    webHandlers = createFrontlineWebHandlers()
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BROWSER_VIEW, ctx={'url': url,
     'webHandlers': webHandlers,
     'returnAlias': VIEW_ALIAS.LOBBY_HANGAR}), EVENT_BUS_SCOPE.LOBBY)


class EPIC_PERF_GROUP(object):
    HIGH_RISK = 1
    MEDIUM_RISK = 2
    LOW_RISK = 3


class EPIC_META_GAME_LIMIT_TYPE(object):
    SYSTEM_DATA = 0
    HARDWARE_PARAMS = 1


PERFORMANCE_GROUP_LIMITS = {EPIC_PERF_GROUP.HIGH_RISK: [{EPIC_META_GAME_LIMIT_TYPE.SYSTEM_DATA: {'osBit': 1,
                                                                      'graphicsEngine': 0}}, {EPIC_META_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_MEMORY: 490}}, {EPIC_META_GAME_LIMIT_TYPE.SYSTEM_DATA: {'graphicsEngine': 0},
                              EPIC_META_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_RAM: 2900}}],
 EPIC_PERF_GROUP.MEDIUM_RISK: [{EPIC_META_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_SCORE: 150}}, {EPIC_META_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_CPU_SCORE: 50000}}]}

class EpicMetaGameSkillLevel(object):
    __slots__ = ('level', 'name', 'descr', 'shortDescr', 'longDescr', 'shortFilterAlert', 'longFilterAlert', 'icon', 'eqID')

    def __init__(self, lvl, eqID, name, descr, shortDescr, longDescr, shortFilterAlert, longFilterAlert, icon):
        self.level = lvl
        self.name = name
        self.descr = descr
        self.shortDescr = shortDescr
        self.longDescr = longDescr
        self.shortFilterAlert = shortFilterAlert
        self.longFilterAlert = longFilterAlert
        self.icon = icon
        self.eqID = eqID


class EpicMetaGameSkill(object):
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, skillID, maxLvl):
        self.skillID = skillID
        self.maxLvl = maxLvl
        self.levels = {}

    def isMastered(self):
        return self.epicMetaGameCtrl.getSkillLevels().get(self.skillID, None) == self.maxLvl

    def getMaxUnlockedSkillLevel(self):
        maxUnlockedLvl = self.epicMetaGameCtrl.getSkillLevels().get(self.skillID, None)
        return maxUnlockedLvl and self.levels[maxUnlockedLvl]

    def getAllUnlockedSkillLevels(self):
        maxUnlockedLvlIdx = self.epicMetaGameCtrl.getSkillLevels().get(self.skillID, 0)
        return (self.levels[lvl + 1] for lvl in xrange(maxUnlockedLvlIdx))


class _FrontLineSounds(object):
    __SELECT_EVENT = 'gui_eb_mode_enter'
    __DESELECT_EVENT = 'gui_eb_mode_exit'
    __STATE_GROUP = 'STATE_gamemode'
    __STATE_SELECTED = 'STATE_gamemode_frontline'
    __STATE_DESELECTED = 'STATE_gamemode_default'

    @staticmethod
    def onChange(isSelected):
        if isSelected:
            WWISE.WW_eventGlobal(_FrontLineSounds.__SELECT_EVENT)
            WWISE.WW_setState(_FrontLineSounds.__STATE_GROUP, _FrontLineSounds.__STATE_SELECTED)
        else:
            WWISE.WW_eventGlobal(_FrontLineSounds.__DESELECT_EVENT)
            WWISE.WW_setState(_FrontLineSounds.__STATE_GROUP, _FrontLineSounds.__STATE_DESELECTED)


class EpicBattleMetaGameController(IEpicBattleMetaGameController, Notifiable, SeasonProvider, IGlobalListener):
    itemsCache = dependency.descriptor(IItemsCache)
    battleResultsService = dependency.descriptor(IBattleResultsService)
    connectionMgr = dependency.descriptor(IConnectionManager)
    lobbyContext = dependency.descriptor(ILobbyContext)
    settingsCore = dependency.descriptor(ISettingsCore)
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(EpicBattleMetaGameController, self).__init__()
        self._setSeasonSettingsProvider(self.__getSettingsEpicBattles)
        self.onUpdated = Event.Event()
        self.onPrimeTimeStatusUpdated = Event.Event()
        self.__skillData = {}
        self.__playerMaxLevel = 0
        self.__playerMaxPrestigeLevel = 0
        self.__levelProgress = tuple()
        self.__isNow = False
        self.__inEpicPrebattle = False
        self.__performanceGroup = None
        self.__urlMacros = URLMacros()
        self.__baseUrl = GUI_SETTINGS.lookup('frontline')
        self.__isFrSoundMode = False
        self.__rankSettings = {}
        return

    def init(self):
        super(EpicBattleMetaGameController, self).init()
        self.addNotificator(SimpleNotifier(self.getTimer, self.__timerUpdate))

    def fini(self):
        self.__urlMacros.clear()
        self.__urlMacros = None
        self.onUpdated.clear()
        self.onPrimeTimeStatusUpdated.clear()
        self.clearNotification()
        self.stopGlobalListening()
        super(EpicBattleMetaGameController, self).fini()
        return

    def onLobbyInited(self, ctx):
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__updateEpicMetaGameSettings
        g_currentVehicle.onChanged += self.__invalidateBattleAbilities
        g_clientUpdateManager.addCallbacks({'epicMetaGame': self.__updateEpic,
         'inventory': self.__onInventoryUpdate})
        self.startGlobalListening()
        self.__setData()
        self.__invalidateBattleAbilities()
        self.startNotification()
        if self.getPerformanceGroup() == EPIC_PERF_GROUP.HIGH_RISK:
            self.lobbyContext.addFightButtonConfirmator(self.__confirmFightButtonPressEnabled)
        self.__isFrSoundMode = False
        self.__updateSounds()

    def onDisconnected(self):
        self.__clear()

    def onPrbEntitySwitched(self):
        self.__invalidateBattleAbilities()
        self.__updateSounds()

    def onAccountBecomePlayer(self):
        self.battleResultsService.onResultPosted += self.__showBattleResults

    def onAvatarBecomePlayer(self):
        self.__clear()
        self.battleResultsService.onResultPosted -= self.__showBattleResults

    def isEnabled(self):
        return self.__getSettingsEpicBattles().isEnabled

    @process
    def openURL(self, url=None):
        requestUrl = url or self.__baseUrl
        if requestUrl:
            parsedUrl = yield self.__urlMacros.parse(requestUrl)
            if parsedUrl:
                _showBrowserView(parsedUrl)

    def showCustomScreen(self, screen):
        if self.__baseUrl and screen in FRONTLINE_SCREENS.ALL():
            self.openURL(self.__baseUrl + screen)

    def getPerformanceGroup(self):
        if not self.__performanceGroup:
            self.__analyzeClientSystem()
            _logger.debug('Current performance group %s', self.__performanceGroup)
        return self.__performanceGroup

    def getMaxPlayerLevel(self):
        return self.__playerMaxLevel

    def getMaxPlayerPrestigeLevel(self):
        return self.__playerMaxPrestigeLevel

    def getRewardVehicles(self):
        return self.__rewardVehicles

    def getStageLimit(self):
        return self.__stageLimit

    def getPointsProgressForLevel(self, level):
        return self.__levelProgress[level]

    def getPointsForLevel(self, level):
        return sum((self.__levelProgress[level] for level in xrange(level - 1)))

    def getLevelProgress(self):
        return self.__levelProgress

    def getLevelForPoints(self, points):
        lvl = 0
        while points >= 0 and lvl <= self.__playerMaxLevel:
            points -= self.__levelProgress[lvl]
            lvl += 1

        return lvl - 1

    def getAllSkillsInformation(self):
        return self.__skillData

    def getPlayerLevelInfo(self):
        return self.itemsCache.items.epicMetaGame.playerLevelInfo

    def getPlayerRanksInfo(self):
        if not self.__rankSettings:
            famePtsByRank = self.__getSettings().metaLevel.get('famePtsByRank', {})
            rankSettings = getRankSettings()
            self.__rankSettings = {rankLvl:(extraFamePts, rankSettings.bonus.factor100ByRank[rankLvl]) for rankLvl, extraFamePts in famePtsByRank.iteritems()}
        return self.__rankSettings

    def getSeasonData(self):
        return self.itemsCache.items.epicMetaGame.seasonData

    def getSkillPoints(self):
        return self.itemsCache.items.epicMetaGame.skillPoints

    def getSkillLevels(self):
        return self.itemsCache.items.epicMetaGame.skillLevels

    def getSelectedSkills(self, vehicleCD):
        selected = self.itemsCache.items.epicMetaGame.selectedSkills(vehicleCD)
        numSlots = vehicles.ABILITY_SLOTS_BY_VEHICLE_CLASS[vehicles.getVehicleClass(vehicleCD)]
        while len(selected) < numSlots:
            selected.append(-1)

        return selected

    def hasSuitableVehicles(self):
        requiredLevel = self.__getSettingsEpicBattles().validVehicleLevels
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(requiredLevel))
        return len(vehs) > 0

    def isFrozen(self):
        for primeTime in self.getPrimeTimes().values():
            if primeTime.hasAnyPeriods():
                return False

        return True

    def getPrimeTimes(self):
        if not self.hasAnySeason():
            return {}
        epicBattlesConfig = self.lobbyContext.getServerSettings().epicBattles
        primeTimes = epicBattlesConfig.primeTimes
        peripheryIDs = epicBattlesConfig.peripheryIDs
        primeTimesPeriods = defaultdict(lambda : defaultdict(list))
        for primeTime in primeTimes:
            period = (primeTime['start'], primeTime['end'])
            weekdays = primeTime['weekdays']
            for pID in primeTime['peripheryIDs']:
                if pID not in peripheryIDs:
                    continue
                periphery = primeTimesPeriods[pID]
                for wDay in weekdays:
                    periphery[wDay].append(period)

        return {pID:PrimeTime(pID, {wDay:collapseIntervals(periods) for wDay, periods in pPeriods.iteritems()}) for pID, pPeriods in primeTimesPeriods.iteritems()}

    def getPrimeTimeStatus(self, peripheryID=None):
        if peripheryID is None:
            peripheryID = self.connectionMgr.peripheryID
        primeTime = self.getPrimeTimes().get(peripheryID)
        if primeTime is None:
            return (PrimeTimeStatus.NOT_SET, 0, False)
        elif not primeTime.hasAnyPeriods():
            return (PrimeTimeStatus.FROZEN, 0, False)
        else:
            season = self.getCurrentSeason() or self.getNextSeason()
            currTime = time_utils.getCurrentLocalServerTimestamp()
            if season and season.hasActiveCycle(currTime):
                self.__isNow, timeTillUpdate = primeTime.getAvailability(currTime, season.getCycleEndDate())
            else:
                timeTillUpdate = 0
                if season:
                    nextCycle = season.getNextByTimeCycle(currTime)
                    if nextCycle:
                        primeTimeStart = primeTime.getNextPeriodStart(nextCycle.startDate, season.getEndDate(), includeBeginning=True)
                        if primeTimeStart:
                            timeTillUpdate = max(primeTimeStart, nextCycle.startDate) - currTime
                self.__isNow = False
            return (PrimeTimeStatus.AVAILABLE, timeTillUpdate, self.__isNow) if self.__isNow else (PrimeTimeStatus.NOT_AVAILABLE, timeTillUpdate, False)

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        if self.connectionMgr.peripheryID == 0:
            hostsList.insert(0, (self.connectionMgr.url,
             self.connectionMgr.serverUserName,
             self.connectionMgr.serverUserNameShort,
             HOST_AVAILABILITY.IGNORED,
             0))
        primeTimes = self.getPrimeTimes()
        dayStart, dayEnd = time_utils.getDayTimeBoundsForLocal(selectedTime)
        dayEnd += 1
        serversPeriodsMapping = {}
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

    def hasAvailablePrimeTimeServers(self):
        if self.connectionMgr.isStandalone():
            allPeripheryIDs = {self.connectionMgr.peripheryID}
        else:
            allPeripheryIDs = set([ host.peripheryID for host in g_preDefinedHosts.hostsWithRoaming() ])
        for peripheryID in allPeripheryIDs:
            primeTimeStatus, _, _ = self.getPrimeTimeStatus(peripheryID)
            if primeTimeStatus == PrimeTimeStatus.AVAILABLE:
                return True

        return False

    def increaseSkillLevel(self, skillID):
        BigWorld.player().epicMetaGame.increaseAbility(skillID)

    def changeEquippedSkills(self, skillIDArray, vehicleCD, callback=None):
        if callback is None:
            BigWorld.player().epicMetaGame.setSelectedAbilities(skillIDArray, vehicleCD)
        else:
            BigWorld.player().epicMetaGame.setSelectedAbilities(skillIDArray, vehicleCD, callback)
        return

    def getCurrentCycleInfo(self):
        season = self.getCurrentSeason()
        if season is not None:
            if season.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp()):
                return (season.getCycleEndDate(), True)
            return (season.getCycleStartDate(), False)
        else:
            return (None, False)

    def getCycleInfo(self, cycleID=None):
        season = self.getCurrentSeason()
        if season is not None:
            cycleInfo = season.getCycleInfo(cycleID)
            if cycleInfo is not None:
                return cycleInfo
            _logger.warning('Cycle with id "%s" not found', cycleID)
        _logger.warning('No current season')
        return

    def getCycleOrdinalNumber(self, cycleID):
        cycleInfo = self.getCycleInfo(cycleID)
        return cycleInfo.ordinalNumber if cycleInfo else None

    def getSeasonTimeRange(self):
        season = self.getCurrentSeason()
        if season is not None:
            cycles = season.getAllCycles()
            if cycles:
                cycles = list(sorted(cycles.values(), key=lambda c: c.ordinalNumber))
                return (cycles[0].startDate, cycles[-1].endDate)
        return (0, 0)

    def getAllUnlockedSkillLevels(self):
        return chain.from_iterable((skill.getAllUnlockedSkillLevels() for skill in self.__skillData.itervalues()))

    def getAllUnlockedSkillLevelsBySkillId(self):
        return {skillID:skill.getAllUnlockedSkillLevels() for skillID, skill in self.__skillData.iteritems()}

    def getUnlockedAbilityIds(self):
        return (lvl.eqID for lvl in (skill.getMaxUnlockedSkillLevel() for skill in self.getAllSkillsInformation().itervalues()) if lvl is not None)

    def getStoredEpicDiscount(self):
        return BigWorld.player().epicMetaGame.getStoredDiscount()

    def isAvailable(self):
        return self.isEnabled() and not self.bootcampController.isInBootcamp() and self.getCurrentSeason() is not None and self.getCurrentCycleInfo()[1] and self.isInPrimeTime()

    def isInPrimeTime(self):
        _, _, isNow = self.getPrimeTimeStatus()
        return isNow

    def isWelcomeScreenUpToDate(self, serverSettings):
        lastSeen = serverSettings.getSectionSettings(GUI_START_BEHAVIOR, 'lastShownEpicWelcomeScreen')
        currentVersion = getCurrentWelcomeScreenVersion()
        return lastSeen >= currentVersion

    def getTimer(self):
        primeTimeStatus, timeLeft, _ = self.getPrimeTimeStatus()
        if primeTimeStatus != PrimeTimeStatus.AVAILABLE and not self.connectionMgr.isStandalone():
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

    def __invalidateBattleAbilities(self):
        self.__invalidateBattleAbilityItems()
        self.__invalidateBattleAbilitiesForVehicle()

    def __setData(self):
        self.__skillData = {}
        skills = self.__getSettings().rewards.get('combatReserves', {})
        maxSkillLvl = self.__getSettings().maxCombatReserveLevel
        eqs = vehicles.g_cache.equipments()
        if skills != {}:
            for key, value in skills.iteritems():
                self.__skillData[key] = EpicMetaGameSkill(key, maxSkillLvl)
                lvls = value['levels']
                lvlAmount = len(lvls)
                found = 0
                for eq in eqs.values():
                    if eq.name in lvls:
                        lvl = lvls.index(eq.name) + 1
                        self.__skillData[key].levels[lvl] = EpicMetaGameSkillLevel(lvl, eq.id[1], i18n.makeString(eq.userString), i18n.makeString(eq.description), i18n.makeString(eq.shortDescription), i18n.makeString(eq.longDescription), i18n.makeString(eq.shortFilterAlert), i18n.makeString(eq.longFilterAlert), eq.icon[0])
                        found += 1
                        if found == lvlAmount:
                            break

        self.__playerMaxLevel = self.__getSettings().metaLevel.get('maxLevel', 0)
        self.__playerMaxPrestigeLevel = self.__getSettings().metaLevel.get('maxPrestigeRewardLevel', 0)
        self.__rewardVehicles = self.__getSettings().rewards.get('vehicle', {})
        self.__stageLimit = self.__getSettings().metaLevel.get('stageLimit', -1)
        levelProgress = self.__getSettings().metaLevel.get('famePtsToProgress', [])[:]
        levelProgress.insert(0, 0)
        self.__levelProgress = tuple(levelProgress)

    def __clear(self):
        self.stopNotification()
        self.stopGlobalListening()
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__updateEpicMetaGameSettings
        g_currentVehicle.onChanged -= self.__invalidateBattleAbilities
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.getPerformanceGroup() == EPIC_PERF_GROUP.HIGH_RISK:
            self.lobbyContext.deleteFightButtonConfirmator(self.__confirmFightButtonPressEnabled)

    def __updateEpic(self, diff):
        changes = set(diff.keys())
        self.__invalidateBattleAbilities()
        if changes:
            self.onUpdated(diff)

    def __updateEpicMetaGameSettings(self, diff):
        if 'epic_config' in diff:
            self.__setData()
            self.onUpdated(diff)
            self.__resetTimer()

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onPrimeTimeStatusUpdated(status)

    def __showBattleResults(self, reusableInfo, _):
        if reusableInfo.common.arenaBonusType == ARENA_BONUS_TYPE.EPIC_BATTLE:
            event_dispatcher.showEpicBattlesAfterBattleWindow(reusableInfo)

    def __isInValidPrebattle(self):
        if g_prbLoader and g_prbLoader.getDispatcher() and g_prbLoader.getDispatcher().getEntity():
            currentPrbEntity = g_prbLoader.getDispatcher().getEntity().getEntityType()
            return currentPrbEntity in (QUEUE_TYPE.EPIC, PREBATTLE_TYPE.EPIC, PREBATTLE_TYPE.EPIC_TRAINING)
        else:
            return None

    def __invalidateBattleAbilityItems(self):
        data = self.itemsCache.items.getItems(GUI_ITEM_TYPE.BATTLE_ABILITY, REQ_CRITERIA.EMPTY)
        for item in data.values():
            if self.__isInValidPrebattle():
                newLevel = next((lvl.level for lvl in chain.from_iterable((skillInfo.levels.itervalues() for skillInfo in self.getAllSkillsInformation().itervalues())) if lvl.eqID == item.innationID), 0)
                item.setLevel(newLevel)
                item.isUnlocked = item.innationID in self.getUnlockedAbilityIds()
            item.setLevel(0)
            item.isUnlocked = False

    def getNumAbilitySlots(self, vehicleType):
        config = self.lobbyContext.getServerSettings().epicMetaGame
        vehClass = getVehicleClassFromVehicleType(vehicleType)
        return config.defaultSlots[vehClass]

    def __invalidateBattleAbilitiesForVehicle(self):
        vehicle = g_currentVehicle.item
        if vehicle is None or vehicle.descriptor.type.level not in self.lobbyContext.getServerSettings().epicBattles.validVehicleLevels or not self.__isInValidPrebattle():
            if vehicle is not None:
                vehicle.equipment.setBattleAbilityConsumables(BattleAbilityConsumables(*[]))
            return
        else:
            amountOfSlots = self.getNumAbilitySlots(vehicle.descriptor.type)
            selectedItems = [None] * amountOfSlots
            skillInfo = self.getAllSkillsInformation()
            slectedSkills = self.getSelectedSkills(vehicle.intCD)
            battleAbilities = self.itemsCache.items.getItems(GUI_ITEM_TYPE.BATTLE_ABILITY, REQ_CRITERIA.EMPTY)
            for item in battleAbilities.values():
                for index, skillID in enumerate(slectedSkills):
                    if skillID is not None and skillID >= 0:
                        if skillInfo[skillID].getMaxUnlockedSkillLevel() and item.innationID == skillInfo[skillID].getMaxUnlockedSkillLevel().eqID:
                            selectedItems[index] = item

            vehicle.equipment.setBattleAbilityConsumables(BattleAbilityConsumables(*selectedItems))
            return

    def __analyzeClientSystem(self):
        stats = BigWorld.wg_getClientStatistics()
        stats['graphicsEngine'] = self.settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE)
        self.__performanceGroup = EPIC_PERF_GROUP.LOW_RISK
        for groupName, conditions in PERFORMANCE_GROUP_LIMITS.iteritems():
            for currentLimit in conditions:
                condValid = True
                systemStats = currentLimit.get(EPIC_META_GAME_LIMIT_TYPE.SYSTEM_DATA, {})
                for key, limit in systemStats.iteritems():
                    currValue = stats.get(key, None)
                    if currValue is None or currValue != limit:
                        condValid = False

                hardwareParams = currentLimit.get(EPIC_META_GAME_LIMIT_TYPE.HARDWARE_PARAMS, {})
                for key, limit in hardwareParams.iteritems():
                    currValue = BigWorld.getAutoDetectGraphicsSettingsScore(key)
                    if currValue >= limit:
                        condValid = False

                if condValid:
                    self.__performanceGroup = groupName
                    return

        return

    def __onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.VEHICLE or GUI_ITEM_TYPE.BATTLE_ABILITY or GUI_ITEM_TYPE.CUSTOMIZATION in invDiff:
            self.__invalidateBattleAbilities()

    def __updateSounds(self):
        if self.prbEntity is None:
            return
        else:
            isFrSoundMode = bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.EPIC)
            if isFrSoundMode != self.__isFrSoundMode:
                _FrontLineSounds.onChange(isFrSoundMode)
                self.__isFrSoundMode = isFrSoundMode
            return

    @async
    @process
    def __confirmFightButtonPressEnabled(self, callback):
        if not self.__isInValidPrebattle():
            callback(True)
            return
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        filters = self.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        isEpicPerformanceWarningEnabled = not AccountSettings.getSettings('isEpicPerformanceWarningClicked')
        if isEpicPerformanceWarningEnabled:
            result, checkboxChecked = yield DialogsInterface.showI18nCheckBoxDialog('epicBattleConfirmDialog')
            filters['isEpicPerformanceWarningClicked'] = checkboxChecked
            AccountSettings.setSettings('isEpicPerformanceWarningClicked', checkboxChecked)
        else:
            result = True
        callback(result)

    @staticmethod
    def __getSettings():
        lobbyContext = dependency.instance(ILobbyContext)
        generalSettings = lobbyContext.getServerSettings().epicMetaGame
        return generalSettings

    @staticmethod
    def __getSettingsEpicBattles():
        lobbyContext = dependency.instance(ILobbyContext)
        generalSettings = lobbyContext.getServerSettings().epicBattles
        return generalSettings
