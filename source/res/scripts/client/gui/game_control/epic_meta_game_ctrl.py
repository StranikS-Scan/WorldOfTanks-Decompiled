# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/epic_meta_game_ctrl.py
from itertools import chain
from collections import defaultdict
import BigWorld
import Event
from shared_utils import collapseIntervals
from gui.ranked_battles.ranked_models import PrimeTime
from constants import ARENA_BONUS_TYPE, PREBATTLE_TYPE, QUEUE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import event_dispatcher
from helpers import dependency, i18n, time_utils
from items import vehicles
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.connection_mgr import IConnectionManager
from gui.ranked_battles.constants import PRIME_TIME_STATUS
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE
from CurrentVehicle import g_currentVehicle
from items.vehicles import getNumAbilitySlots
from gui.shared.gui_items.vehicle_equipment import BattleAbilityConsumables
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from gui.prb_control.entities.listener import IGlobalListener
from helpers.statistics import HARDWARE_SCORE_PARAMS
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY
from account_helpers.AccountSettings import AccountSettings, GUI_START_BEHAVIOR
from debug_utils import LOG_DEBUG
from gui import DialogsInterface
from adisp import async, process as adisp_process
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import GRAPHICS
_VALID_PREBATTLE_TYPES = [PREBATTLE_TYPE.EPIC, PREBATTLE_TYPE.EPIC_TRAINING]

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
    __slots__ = ('level', 'name', 'descr', 'shortDescr', 'longDescr', 'icon', 'eqID')

    def __init__(self, lvl, eqID, name, descr, shortDescr, longDescr, icon):
        self.level = lvl
        self.name = name
        self.descr = descr
        self.shortDescr = shortDescr
        self.longDescr = longDescr
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


class EpicBattleMetaGameController(IEpicBattleMetaGameController, Notifiable, IGlobalListener):
    itemsCache = dependency.descriptor(IItemsCache)
    battleResultsService = dependency.descriptor(IBattleResultsService)
    connectionMgr = dependency.descriptor(IConnectionManager)
    lobbyContext = dependency.descriptor(ILobbyContext)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(EpicBattleMetaGameController, self).__init__()
        self.onUpdated = Event.Event()
        self.onPrimeTimeStatusUpdated = Event.Event()
        self.__skillData = {}
        self.__playerMaxLevel = 0
        self.__levelProgress = []
        self.__isNow = False
        self.__inEpicPrebattle = False
        self.__performanceGroup = None
        return

    def init(self):
        super(EpicBattleMetaGameController, self).init()
        self.addNotificator(SimpleNotifier(self.__getTimer, self.__timerUpdate))

    def fini(self):
        self.onUpdated.clear()
        self.onPrimeTimeStatusUpdated.clear()
        self.clearNotification()
        self.stopGlobalListening()
        super(EpicBattleMetaGameController, self).fini()

    def onLobbyInited(self, ctx):
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__updateEpicMetaGameSettings
        g_currentVehicle.onChanged += self.__invalidateBattleAbilitiesForVehicle
        g_clientUpdateManager.addCallbacks({'epicMetaGame': self.__updateEpic})
        self.startGlobalListening()
        self.__getStaticData()
        self.__invalidateBattleAbilityItems()
        self.__invalidateBattleAbilitiesForVehicle()
        self.startNotification()
        if self.getPerformanceGroup() == EPIC_PERF_GROUP.HIGH_RISK:
            self.lobbyContext.addFightButtonConfirmator(self.__confirmFightButtonPressEnabled)

    def onDisconnected(self):
        self.__clear()

    def onPrbEntitySwitched(self):
        self.__invalidateBattleAbilityItems()
        self.__invalidateBattleAbilitiesForVehicle()

    def onAccountBecomePlayer(self):
        self.battleResultsService.onResultPosted += self.__showBattleResults

    def onAvatarBecomePlayer(self):
        self.__clear()
        self.battleResultsService.onResultPosted -= self.__showBattleResults

    def getPerformanceGroup(self):
        if not self.__performanceGroup:
            self.__analyzeClientSystem()
            LOG_DEBUG('Current performance group ', self.__performanceGroup)
        return self.__performanceGroup

    def getMaxPlayerLevel(self):
        return self.__playerMaxLevel

    def getPointsProgessForLevel(self, level):
        return self.__levelProgress[level]

    def getPointsForLevel(self, level):
        return sum((self.__levelProgress[level] for level in xrange(level - 1)))

    def getLevelForPoints(self, points):
        lvl = 0
        while points >= 0 and lvl <= self.__playerMaxLevel:
            points -= self.__levelProgress[lvl]
            lvl += 1

        return lvl - 1

    def getSkillInformation(self):
        return self.__skillData

    def getPlayerLevelInfo(self):
        return self.itemsCache.items.epicMetaGame.playerLevelInfo

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

    def hasAnySeason(self):
        return bool(self.__getSettingsEpicBattles().season)

    def isFrozen(self):
        peripheryPrimeTime = self.getPrimeTimes().get(self.connectionMgr.peripheryID)
        return True if peripheryPrimeTime is not None and not peripheryPrimeTime.hasAnyPeriods() else False

    def getPrimeTimes(self):
        if not self.hasAnySeason():
            return {}
        epicBattlesConfig = self.lobbyContext.getServerSettings().epicBattles
        primeTimes = epicBattlesConfig.season.get('primeTimes', {})
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
            return (PRIME_TIME_STATUS.NOT_SET, 0, False)
        elif not primeTime.hasAnyPeriods():
            return (PRIME_TIME_STATUS.FROZEN, 0, False)
        else:
            currentSeason = self.__getSettingsEpicBattles().season
            if not currentSeason:
                return (PRIME_TIME_STATUS.NO_SEASON, 0, False)
            time, inSeason = self.getSeasonEndTime()
            if inSeason:
                self.__isNow, timeLeft = primeTime.getAvailability(time_utils.getCurrentLocalServerTimestamp(), time)
            else:
                timeLeft = 0 if time is None else time - time_utils.getCurrentLocalServerTimestamp()
                self.__isNow = False
            return (PRIME_TIME_STATUS.AVAILABLE, timeLeft, self.__isNow) if self.__isNow else (PRIME_TIME_STATUS.NOT_AVAILABLE, timeLeft, self.__isNow)

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

    def increaseSkillLevel(self, skillID):
        BigWorld.player().epicMetaGame.increaseAbility(skillID)

    def changeEquippedSkills(self, skillIDArray, vehicleCD, callback=None):
        if callback is None:
            BigWorld.player().epicMetaGame.setSelectedAbilities(skillIDArray, vehicleCD)
        else:
            BigWorld.player().epicMetaGame.setSelectedAbilities(skillIDArray, vehicleCD, callback)
        return

    def getSeasonEndTime(self):
        generalSettings = self.lobbyContext.getServerSettings().epicBattles
        if time_utils.getCurrentLocalServerTimestamp() < generalSettings.season['start']:
            return (generalSettings.season['start'], False)
        else:
            return (None, False) if time_utils.getCurrentLocalServerTimestamp() > generalSettings.season['end'] else (generalSettings.season['end'], True)

    def getAllUnlockedSkillLevels(self):
        return chain.from_iterable((skill.getAllUnlockedSkillLevels() for skill in self.__skillData.itervalues()))

    def getAllUnlockedSkillLevelsBySkillId(self):
        return {skillID:skill.getAllUnlockedSkillLevels() for skillID, skill in self.__skillData.iteritems()}

    def getUnlockedAbilityIds(self):
        return (lvl.eqID for lvl in (skill.getMaxUnlockedSkillLevel() for skill in self.getSkillInformation().itervalues()) if lvl is not None)

    def isAvailable(self):
        isEpicEnabled = self.lobbyContext.getServerSettings().isEpicBattleEnabled()
        if not isEpicEnabled or not self.hasAnySeason():
            return False
        else:
            status, _ = self.getSeasonEndTime()
            return False if status is None else self.isInPrimeTime()

    def isInPrimeTime(self):
        _, _, isNow = self.getPrimeTimeStatus()
        return isNow

    def __getStaticData(self):
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
                        self.__skillData[key].levels[lvl] = EpicMetaGameSkillLevel(lvl, eq.id[1], i18n.makeString(eq.userString), i18n.makeString(eq.description), i18n.makeString(eq.shortDescription), i18n.makeString(eq.longDescription), eq.icon[0])
                        found += 1
                        if found == lvlAmount:
                            break

        self.__playerMaxLevel = self.__getSettings().metaLevel.get('maxLevel', 0)
        self.__levelProgress = self.__getSettings().metaLevel.get('famePtsToProgress', [])[:]
        self.__levelProgress.insert(0, 0)

    def __clear(self):
        self.stopNotification()
        self.stopGlobalListening()
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__updateEpicMetaGameSettings
        g_currentVehicle.onChanged -= self.__invalidateBattleAbilitiesForVehicle
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.getPerformanceGroup() == EPIC_PERF_GROUP.HIGH_RISK:
            self.lobbyContext.deleteFightButtonConfirmator(self.__confirmFightButtonPressEnabled)

    def __updateEpic(self, diff):
        changes = set(diff.keys())
        self.__invalidateBattleAbilityItems()
        self.__invalidateBattleAbilitiesForVehicle()
        if changes:
            self.onUpdated(diff)

    def __updateEpicMetaGameSettings(self, diff):
        if 'epic_config' in diff:
            self.onUpdated(diff)

    def __getTimer(self):
        _, timeLeft, _ = self.getPrimeTimeStatus()
        return timeLeft + 1 if timeLeft > 0 else time_utils.ONE_MINUTE

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onPrimeTimeStatusUpdated(status)

    def __showBattleResults(self, reusableInfo, composer):
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
                newLevel = next((lvl.level for lvl in chain.from_iterable((skillInfo.levels.itervalues() for skillInfo in self.getSkillInformation().itervalues())) if lvl.eqID == item.innationID), 0)
                item.setLevel(newLevel)
                item.isUnlocked = item.innationID in self.getUnlockedAbilityIds()
            item.setLevel(0)
            item.isUnlocked = False

    def __invalidateBattleAbilitiesForVehicle(self):
        vehicle = g_currentVehicle.item
        if vehicle is None or vehicle.descriptor.type.level not in self.lobbyContext.getServerSettings().epicBattles.validVehicleLevels or not self.__isInValidPrebattle():
            if vehicle is not None:
                vehicle.equipment.setBattleAbilityConsumables(BattleAbilityConsumables(*[]))
            return
        else:
            amountOfSlots = getNumAbilitySlots(vehicle.descriptor.type)
            selectedItems = [None] * amountOfSlots
            skillInfo = self.getSkillInformation()
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

    @async
    @adisp_process
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
    def __getSettings(cycleID=None):
        lobbyContext = dependency.instance(ILobbyContext)
        generalSettings = lobbyContext.getServerSettings().epicMetaGame
        return generalSettings

    @staticmethod
    def __getSettingsEpicBattles(cycleID=None):
        lobbyContext = dependency.instance(ILobbyContext)
        generalSettings = lobbyContext.getServerSettings().epicBattles
        return generalSettings
