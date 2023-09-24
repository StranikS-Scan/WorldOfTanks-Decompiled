# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/epic_meta_game_ctrl.py
from bisect import insort_right
from operator import itemgetter
import adisp
import typing
import logging
import BigWorld
import WWISE
import Event
from account_helpers.client_epic_meta_game import skipResponse
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from constants import ARENA_BONUS_TYPE, PREBATTLE_TYPE, QUEUE_TYPE, Configs
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.base.ctx import PrbAction
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showFrontlineContainerWindow
from gui.shared.utils import SelectorBattleTypesUtils
from helpers import dependency, i18n, time_utils
from items import vehicles
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from season_provider import SeasonProvider
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE
from CurrentVehicle import g_currentVehicle
from items.vehicles import getVehicleClassFromVehicleType
from items.components.supply_slot_categories import SlotCategories
from shared_utils import first
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier, PeriodicNotifier
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from helpers.statistics import HARDWARE_SCORE_PARAMS
from account_helpers.AccountSettings import AccountSettings, GUI_START_BEHAVIOR, EPIC_LAST_CYCLE_ID
from gui import DialogsInterface
from adisp import adisp_async, adisp_process
from account_helpers.settings_core.settings_constants import GRAPHICS
from player_ranks import getSettings as getRankSettings
from frontline_account_settings import isWelcomeScreenViewed, setWelcomeScreenViewed
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.offers import IOffersDataProvider
from gui.shared.event_dispatcher import showFrontlineWelcomeWindow
from epic_constants import EPIC_SELECT_BONUS_NAME, EPIC_CHOICE_REWARD_OFFER_GIFT_TOKENS, LEVELUP_TOKEN_TEMPLATE, CATEGORIES_ORDER
if typing.TYPE_CHECKING:
    from helpers.server_settings import EpicGameConfig
    from season_common import GameSeasonCycle
_logger = logging.getLogger(__name__)
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
    __slots__ = ('level', 'name', 'shortDescr', 'longDescr', 'shortFilterAlert', 'longFilterAlert', 'icon', 'eqID')

    def __init__(self, lvl, eqID, name, shortDescr, longDescr, shortFilterAlert, longFilterAlert, icon):
        self.level = lvl
        self.name = name
        self.shortDescr = shortDescr
        self.longDescr = longDescr
        self.shortFilterAlert = shortFilterAlert
        self.longFilterAlert = longFilterAlert
        self.icon = icon
        self.eqID = eqID


class EpicMetaGameSkill(object):
    __slots__ = ('skillID', 'maxLvl', 'tags', 'levels', 'price')
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, skillID, maxLvl, tags=None, price=0):
        self.skillID = skillID
        self.maxLvl = maxLvl
        self.tags = tags or []
        self.levels = {}
        self.price = price

    @property
    def isActivated(self):
        return self.epicMetaGameCtrl.getSkillLevels().get(self.skillID, 0) > 0

    @property
    def category(self):
        return first(SlotCategories.ALL.intersection(self.tags))

    def getSkillInfo(self):
        return self.levels.get(1)


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


class EpicBattleMetaGameController(Notifiable, SeasonProvider, IEpicBattleMetaGameController, IGlobalListener):
    bootcampController = dependency.descriptor(IBootcampController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __battleResultsService = dependency.descriptor(IBattleResultsService)
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    MAX_STORED_ARENAS_RESULTS = 20
    DAILY_QUEST_ID = 'front_line'
    FINAL_BADGE_QUEST_ID = 'epicmetagame:progression_finish'

    def __init__(self):
        super(EpicBattleMetaGameController, self).__init__()
        self.onUpdated = Event.Event()
        self.onPrimeTimeStatusUpdated = Event.Event()
        self.onEventEnded = Event.Event()
        self.onGameModeStatusTick = Event.Event()
        self.__skillData = {}
        self.__playerMaxLevel = 0
        self.__levelProgress = tuple()
        self.__abilityPointsForLevel = list()
        self.__performanceGroup = None
        self.__isEpicSoundMode = False
        self.__showedResultsForArenas = []
        self.__eventEndedNotifier = None
        return

    def init(self):
        super(EpicBattleMetaGameController, self).init()
        self.addNotificator(SimpleNotifier(self.getTimer, self.__timerUpdate))
        self.addNotificator(PeriodicNotifier(self.getTimer, self.__timerTick))
        self.__eventEndedNotifier = SimpleNotifier(self.getEventTimeLeft, self.__onEventEnded)
        self.addNotificator(self.__eventEndedNotifier)

    def fini(self):
        del self.__showedResultsForArenas[:]
        self.onUpdated.clear()
        self.onPrimeTimeStatusUpdated.clear()
        self.onGameModeStatusTick.clear()
        self.onEventEnded.clear()
        self.clearNotification()
        self.stopGlobalListening()
        super(EpicBattleMetaGameController, self).fini()

    def onLobbyInited(self, ctx):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__updateEpicMetaGameSettings
        g_currentVehicle.onChanged += self.__invalidateBattleAbilities
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        g_clientUpdateManager.addCallbacks({'epicMetaGame': self.__updateEpic,
         'inventory': self.__onInventoryUpdate,
         'tokens': self.__onTokensUpdate})
        self.startGlobalListening()
        self.__setData()
        self.__invalidateBattleAbilities()
        self.startNotification()
        if self.getPerformanceGroup() == EPIC_PERF_GROUP.HIGH_RISK:
            self.__lobbyContext.addFightButtonConfirmator(self.__confirmFightButtonPressEnabled)
        self.__isEpicSoundMode = False
        if self.prbEntity is not None:
            enableSound = bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.EPIC)
            self.__updateSounds(enableSound)
        return

    def onDisconnected(self):
        self.__clear()

    def onPrbEntitySwitching(self):
        if self.prbEntity is None:
            return
        else:
            switchedFromEpic = bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.EPIC)
            if switchedFromEpic:
                self.__updateSounds(False)
            return

    def onPrbEntitySwitched(self):
        self.__invalidateBattleAbilities()
        if self.prbEntity is None:
            return
        else:
            isEpicSoundMode = bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.EPIC)
            if isEpicSoundMode:
                self.__updateSounds(True)
            return

    def onAccountBecomePlayer(self):
        self.__battleResultsService.onResultPosted += self.__showBattleResults

    def onAvatarBecomePlayer(self):
        self.__clear()
        self.__battleResultsService.onResultPosted -= self.__showBattleResults

    def getModeSettings(self):
        return self.__lobbyContext.getServerSettings().epicBattles

    def isEnabled(self):
        return self.getModeSettings().isEnabled

    @property
    def enableWelcomeScreen(self):
        return self.getModeSettings().enableWelcomeScreen

    def isEpicPrbActive(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.EPIC)

    def isCurrentCycleActive(self):
        season = self.getCurrentSeason()
        return season.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp()) if season is not None else False

    def getLevelsToUpgradeAllReserves(self):
        return self.getModeSettings().levelsToUpgrateAllReserves

    def isBattlePassDataEnabled(self):
        return self.getModeSettings().battlePassDataEnabled

    def isUnlockVehiclesInBattleEnabled(self):
        return any(self.getUnlockableInBattleVehLevels())

    def isDailyQuestsUnlocked(self):
        currrentLevel, _ = self.getPlayerLevelInfo()
        return currrentLevel >= self.getMaxPlayerLevel()

    def isDailyQuestsRefreshAvailable(self):
        if self.hasPrimeTimesLeftForCurrentCycle():
            return True
        primeTimePeriodsForDay = self.getPrimeTimesForDay(time_utils.getCurrentLocalServerTimestamp())
        if primeTimePeriodsForDay:
            _, periodTimeEnd = max(primeTimePeriodsForDay.values(), key=itemgetter(1))
            periodTimeLeft = periodTimeEnd - time_utils.getCurrentLocalServerTimestamp()
            return periodTimeLeft > time_utils.getDayTimeLeft()
        return False

    def getPerformanceGroup(self):
        if not self.__performanceGroup:
            self.__analyzeClientSystem()
            _logger.debug('Current performance group %s', self.__performanceGroup)
        return self.__performanceGroup

    def getMaxPlayerLevel(self):
        return self.__playerMaxLevel

    def getStageLimit(self):
        return self.__stageLimit

    def getAbilityPointsForLevel(self):
        return self.__abilityPointsForLevel

    def getValidVehicleLevels(self):
        return self.getModeSettings().validVehicleLevels

    def getUnlockableInBattleVehLevels(self):
        return self.getModeSettings().unlockableInBattleVehLevels

    def getSuitableForQueueVehicleLevels(self):
        return set(self.getValidVehicleLevels()) - set(self.getUnlockableInBattleVehLevels())

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

    def getEpicSkills(self):
        return {skill.getSkillInfo().eqID:skill for skill in self.__skillData.values()}

    def getAllSkillsInformation(self):
        return self.__skillData

    def getOrderedSkillTree(self):
        result = {category:[] for category in CATEGORIES_ORDER}
        for _, skillData in self.getAllSkillsInformation().iteritems():
            result[skillData.category].append(skillData)

        return [ (category, sorted(result[category], key=lambda vo: vo.price)) for category in CATEGORIES_ORDER ]

    def getPlayerLevelInfo(self):
        return self.__itemsCache.items.epicMetaGame.playerLevelInfo

    def getTooltipData(self, tooltip):
        return self.getModeSettings().tooltips.get(tooltip)

    def getSkillLevelRanks(self):
        return self.getTooltipData('reserveLevels')

    def getPlayerRanksInfo(self):
        famePtsByRank = self.__metaSettings.metaLevel.get('famePtsByRank', {})
        return {rankLvl:(extraFamePts, getRankSettings().bonus.factor100ByRank[rankLvl]) for rankLvl, extraFamePts in famePtsByRank.iteritems()}

    def getPlayerRanksWithBonusInfo(self):
        famePtsByRank = self.__metaSettings.metaLevel.get('famePtsByRank', {})
        fameBonusByRank = self.__metaSettings.metaLevel.get('fameBonusByRank', {})
        return {rankLvl:(extraFamePts, getRankSettings().bonus.factor100ByRank[rankLvl], fameBonusByRank[rankLvl]) for rankLvl, extraFamePts in famePtsByRank.iteritems()}

    def isRandomReservesModeEnabled(self):
        return bool(self.__metaSettings.randomReservesMode)

    def getRandomReservesBonusProbability(self):
        return self.__metaSettings.randomReservesOpt['boardingVehAmmo']['extraWeight']

    def getSeasonData(self):
        return self.__itemsCache.items.epicMetaGame.seasonData

    def getCurrentSeasonID(self):
        currentSeason = self.getCurrentSeason()
        return currentSeason.getSeasonID() if currentSeason else 0

    def getSkillPoints(self):
        return self.__itemsCache.items.epicMetaGame.skillPoints

    def getSkillLevels(self):
        return self.__itemsCache.items.epicMetaGame.skillLevels

    def getSelectedSkills(self, vehicleCD):
        selected = self.__itemsCache.items.epicMetaGame.selectedSkills(vehicleCD)
        numSlots = self.getNumAbilitySlots(vehicles.getVehicleType(vehicleCD))
        while len(selected) < numSlots:
            selected.append(-1)

        return selected

    def hasSuitableVehicles(self):
        requiredLevel = self.getModeSettings().validVehicleLevels
        v = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(requiredLevel))
        return len(v) > 0

    def hasVehiclesToRent(self):
        notRentedVehicles = self.__itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.SPECIFIC_BY_NAME(self.getModeSettings().rentVehicles) | ~REQ_CRITERIA.INVENTORY)
        return len(notRentedVehicles) > 0

    def increaseSkillLevel(self, skillID, callback=skipResponse):
        BigWorld.player().epicMetaGame.increaseAbility(skillID, callback)

    def changeEquippedSkills(self, skillIDArray, vehicleCD, callback=None, classVehs=False):
        if classVehs:
            if callback is None:
                BigWorld.player().epicMetaGame.setSelectedAbilitiesVehsClass(skillIDArray, vehicleCD)
            else:
                BigWorld.player().epicMetaGame.setSelectedAbilitiesVehsClass(skillIDArray, vehicleCD, callback)
        elif callback is None:
            BigWorld.player().epicMetaGame.setSelectedAbilities(skillIDArray, vehicleCD)
        else:
            BigWorld.player().epicMetaGame.setSelectedAbilities(skillIDArray, vehicleCD, callback)
        return

    def getCycleInfo(self, cycleID=None):
        season = self.getCurrentSeason()
        if season is not None:
            return season.getCycleInfo(cycleID)
        else:
            _logger.warning('No current season')
            return

    def getCycleOrdinalNumber(self, cycleID):
        cycleInfo = self.getCycleInfo(cycleID)
        return cycleInfo.ordinalNumber if cycleInfo else None

    def getSeasonTimeRange(self):
        season = self.getActiveSeason()
        if season is not None:
            cycles = season.getAllCycles()
            if cycles:
                cycles = list(sorted(cycles.values(), key=lambda c: c.ordinalNumber))
                return (cycles[0].startDate, cycles[-1].endDate)
        return (0, 0)

    def getActiveSeason(self):
        return self.getCurrentSeason() or self.getNextSeason()

    def getAllUnlockedSkillInfoBySkillId(self):
        return {skillID:skill.getSkillInfo() for skillID, skill in self.__skillData.iteritems() if skill.isActivated}

    def getUnlockedAbilityIds(self):
        return (skill.getSkillInfo().eqID for skill in self.getAllSkillsInformation().itervalues() if skill.isActivated and skill.getSkillInfo() is not None)

    def getStoredEpicDiscount(self):
        return BigWorld.player().epicMetaGame.getStoredDiscount()

    def getEventTimeLeft(self):
        if not self.isEnabled():
            return 0
        timeLeft = self.getSeasonTimeRange()[1] - time_utils.getCurrentLocalServerTimestamp()
        return timeLeft + 1 if timeLeft > 0 else time_utils.ONE_MINUTE

    def getStats(self):
        return self.__itemsCache.items.epicMetaGame

    def showWelcomeScreenIfNeed(self):
        currentSeason = self.getActiveSeason()
        if self.enableWelcomeScreen and currentSeason is not None:
            seasonId = currentSeason.getSeasonID()
            if not isWelcomeScreenViewed(seasonId):
                showFrontlineWelcomeWindow()
                setWelcomeScreenViewed(seasonId)
                return True
        return False

    def getNumAbilitySlots(self, vehicleType):
        vehClass = getVehicleClassFromVehicleType(vehicleType)
        return self.__metaSettings.defaultSlots.get(vehClass, 0)

    def getAbilitySlotsOrder(self, vehicleType):
        vehClass = getVehicleClassFromVehicleType(vehicleType)
        return self.__metaSettings.slots.get(vehClass, (0, 0, 0))

    def getAbilitySlotsUnlockOrder(self, vehicleType):
        vehClass = getVehicleClassFromVehicleType(vehicleType)
        return self.__metaSettings.inBattleReservesByRank.get('slotActions').get(vehClass, [[0], [0], [0]])

    def getAllLevelRewards(self):
        rewardsData, _ = self.__getQuests()
        return rewardsData

    def getLevelRewards(self, level):
        rewardsData, _ = self.__getQuests()
        if level in rewardsData:
            bonuses = rewardsData[level].getBonuses()
            self.__addSkillPointsBonus(bonuses, level)
            return bonuses
        return []

    def getMergedLevelRewards(self):
        from frontline.gui.bonus import isBonusesEqual, mergeSelectable
        rewardsData, levels = self.__getQuests()
        if not levels:
            return []
        startLvl = levels.pop(0)
        startBonuses = rewardsData[startLvl].getBonuses()
        self.__addSkillPointsBonus(startBonuses, startLvl)
        bonusesByLvl = {startLvl: startBonuses}
        currentLevel, _ = self.getPlayerLevelInfo()
        result = [[startLvl, startLvl, startBonuses]]
        for level in levels:
            endBonus = rewardsData[level].getBonuses()
            self.__addSkillPointsBonus(endBonus, level)
            bonusesByLvl.update({level: endBonus})
            prevStartLvl, prevEndLvl, prevBonus = result[-1]
            if isBonusesEqual(prevBonus, endBonus):
                result[-1][1] = level
            mergeSelectable(currentLevel, prevStartLvl, prevEndLvl, prevBonus, bonusesByLvl)
            result.append([level, level, endBonus])

        return result

    def isNeedToTakeReward(self):
        currentLevel, _ = self.getPlayerLevelInfo()
        rewardsData = self.getAllLevelRewards()
        for bonuses in (rewards.getBonuses() for level, rewards in rewardsData.iteritems() if level <= currentLevel):
            for bonus in bonuses:
                if bonus.getName() == EPIC_SELECT_BONUS_NAME:
                    for tokenID in bonus.getTokens().iterkeys():
                        if self.__itemsCache.items.tokens.getToken(tokenID):
                            return True

        return False

    def getNotChosenRewardCount(self):
        count = 0
        for token in self.__itemsCache.items.tokens.getTokens().iterkeys():
            if not token.startswith(EPIC_CHOICE_REWARD_OFFER_GIFT_TOKENS):
                continue
            if not self.__offersProvider.getOfferByToken(token.replace('_gift', '')):
                continue
            if self.__itemsCache.items.tokens.isTokenAvailable(token):
                count += self.__itemsCache.items.tokens.getTokenCount(token)

        return count

    def getCombatReserves(self):
        return self.__metaSettings.rewards.get('combatReserves', {})

    def getReserveData(self, reserve):
        combatReserves = self.getCombatReserves()
        for combatReserve in combatReserves.values():
            for level in combatReserve['levels']:
                if level == reserve:
                    return combatReserve

        return {}

    def isReserveStack(self, reserve):
        data = self.getReserveData(reserve)
        return data.get('isStack', False)

    def getReserveCategory(self, reserve):
        data = self.getReserveData(reserve)
        return data.get('tags', [''] * 3)[1]

    def getReserveTechName(self, reserve):
        data = self.getReserveData(reserve)
        return data.get('name')

    def showProgressionDuringSomeStates(self, showDefaultTab=False):
        from frontline.gui.frontline_helpers import isHangarAvailable, getProperTabWhileHangarUnavailable
        if not isHangarAvailable():
            showFrontlineContainerWindow(getProperTabWhileHangarUnavailable() if not showDefaultTab else None)
        return

    @adisp.adisp_process
    def selectEpicBattle(self):
        dispatcher = self.prbDispatcher
        if dispatcher is None:
            _logger.error('Prebattle dispatcher is not defined')
            return
        else:
            yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.EPIC))
            return

    def hasAnyOfferGiftToken(self):
        return any((token.startswith(EPIC_CHOICE_REWARD_OFFER_GIFT_TOKENS) for token in self.__itemsCache.items.tokens.getTokens().iterkeys()))

    @staticmethod
    def hasBonusCap(cap):
        return hasattr(BigWorld.player(), 'arenaBonusType') and ARENA_BONUS_TYPE_CAPS.checkAny(BigWorld.player().arenaBonusType, cap)

    def replaceOfferByGift(self, bonuses):
        result = []
        for bonus in bonuses:
            gift = self.__getReceivedGift(bonus)
            if gift:
                result.extend(gift.bonuses)
            result.append(bonus)

        return result

    def replaceOfferByReward(self, bonuses):
        result = []
        for bonus in bonuses:
            if bool(self.__getReceivedGift(bonus)):
                bonus.updateContext({'isReceived': True})
            result.append(bonus)

        return result

    def __addSkillPointsBonus(self, bonuses, level):
        skillPoints = self.__abilityPointsForLevel[level - 1]
        if skillPoints > 0:
            from frontline.gui.bonus import FrontlineSkillBonus
            bonuses.append(FrontlineSkillBonus(skillPoints))

    def __getQuests(self):
        quests = dict()
        levels = []
        allQuests = self.__eventsCache.getAllQuests()
        for questKey, questData in allQuests.iteritems():
            if LEVELUP_TOKEN_TEMPLATE in questKey:
                _, _, questNum = questKey.partition(LEVELUP_TOKEN_TEMPLATE)
                if questNum:
                    questLvl = int(questNum)
                    insort_right(levels, questLvl)
                    quests[questLvl] = questData

        return (quests, levels)

    def storeCycle(self):
        lastCycleID = AccountSettings.getSettings(EPIC_LAST_CYCLE_ID)
        cycleID = self.getCurrentCycleID()
        if lastCycleID != cycleID and self.isCurrentCycleActive():
            AccountSettings.setSettings(EPIC_LAST_CYCLE_ID, cycleID)
            SelectorBattleTypesUtils.setBattleTypeAsUnknown(SELECTOR_BATTLE_TYPES.EPIC)

    def __getReceivedGift(self, bonus):
        if bonus.getName() == EPIC_SELECT_BONUS_NAME:
            bonus.updateContext({'isReceived': False})
            for tokenID in bonus.getTokens().iterkeys():
                offer = self.__offersProvider.getOfferByToken(tokenID.replace('_gift', ''))
                if offer:
                    receivedGifts = self.__offersProvider.getReceivedGifts(offer.id)
                    if receivedGifts:
                        for giftId, count in receivedGifts.iteritems():
                            if count > 0:
                                return offer.getGift(giftId)

        return None

    def __onSyncCompleted(self, _, invalidItems):
        if not invalidItems or GUI_ITEM_TYPE.BATTLE_ABILITY in invalidItems:
            self.__invalidateBattleAbilityItems()
        self.__invalidateBattleAbilitiesForVehicle()

    def __invalidateBattleAbilities(self, *_):
        if not self.__itemsCache.isSynced():
            return
        self.__invalidateBattleAbilityItems()
        self.__invalidateBattleAbilitiesForVehicle()

    def __setData(self):
        self.__skillData = {}
        skills = self.getCombatReserves()
        maxSkillLvl = self.__metaSettings.maxCombatReserveLevel
        eqs = vehicles.g_cache.equipments()
        if skills != {}:
            for key, value in skills.iteritems():
                self.__skillData[key] = EpicMetaGameSkill(key, maxSkillLvl, value.get('tags'), value.get('price', 0))
                lvls = value['levels']
                lvlAmount = len(lvls)
                found = 0
                for eq in eqs.values():
                    if eq.name in lvls:
                        lvl = lvls.index(eq.name) + 1
                        self.__skillData[key].levels[lvl] = EpicMetaGameSkillLevel(lvl, eq.id[1], i18n.makeString(eq.userString), i18n.makeString(eq.shortDescription), i18n.makeString(eq.longDescription), i18n.makeString(eq.shortFilterAlert), i18n.makeString(eq.longFilterAlert), eq.icon[0])
                        found += 1
                        if found == lvlAmount:
                            break

        metaLevel = self.__metaSettings.metaLevel
        self.__playerMaxLevel = metaLevel.get('maxLevel', 0)
        self.__stageLimit = metaLevel.get('stageLimit', -1)
        self.__abilityPointsForLevel = metaLevel.get('abilityPointsForLevel', [])
        levelProgress = metaLevel.get('famePtsToProgress', [])[:]
        levelProgress.insert(0, 0)
        self.__levelProgress = tuple(levelProgress)

    def __clear(self):
        self.stopNotification()
        self.stopGlobalListening()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__updateEpicMetaGameSettings
        g_currentVehicle.onChanged -= self.__invalidateBattleAbilities
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.getPerformanceGroup() == EPIC_PERF_GROUP.HIGH_RISK:
            self.__lobbyContext.deleteFightButtonConfirmator(self.__confirmFightButtonPressEnabled)

    def __updateEpic(self, diff):
        changes = set(diff.keys())
        self.__invalidateBattleAbilities()
        if changes:
            self.onUpdated(diff)

    def __updateEpicMetaGameSettings(self, diff):
        if 'epic_config' in diff:
            self.__setData()
            self.onUpdated(diff['epic_config'])
            self.__resetTimer()

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()
        self.__timerTick()

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onPrimeTimeStatusUpdated(status)

    def __timerTick(self):
        self.onGameModeStatusTick()

    def __onEventEnded(self):
        self.onEventEnded()
        self.__eventEndedNotifier.stopNotification()
        self.__eventEndedNotifier.clear()

    def __showBattleResults(self, reusableInfo, _, resultsWindow):
        if reusableInfo.common.arenaBonusType == ARENA_BONUS_TYPE.EPIC_BATTLE:
            arenaUniqueID = reusableInfo.arenaUniqueID
            if arenaUniqueID not in self.__showedResultsForArenas:
                self.__showedResultsForArenas.append(arenaUniqueID)
                self.__showedResultsForArenas = self.__showedResultsForArenas[-self.MAX_STORED_ARENAS_RESULTS:]
                extensionInfo = reusableInfo.personal.avatar.extensionInfo
                levelUpInfo = {'metaLevel': extensionInfo.get('metaLevel'),
                 'prevMetaLevel': extensionInfo.get('prevMetaLevel'),
                 'playerRank': extensionInfo.get('playerRank'),
                 'originalFlXP': extensionInfo.get('originalFlXP'),
                 'boosterFlXP': extensionInfo.get('boosterFlXP')}
                event_dispatcher.showEpicBattlesAfterBattleWindow(levelUpInfo, resultsWindow)

    def __isInValidPrebattle(self):
        if g_prbLoader and g_prbLoader.getDispatcher() is not None:
            entity = g_prbLoader.getDispatcher().getEntity()
            if entity is None:
                return
            currentPrbEntity = entity.getEntityType()
            return currentPrbEntity in (PREBATTLE_TYPE.EPIC, PREBATTLE_TYPE.EPIC_TRAINING) or entity.getQueueType() == QUEUE_TYPE.EPIC
        else:
            return

    def __invalidateBattleAbilityItems(self):
        data = self.__itemsCache.items.getItems(GUI_ITEM_TYPE.BATTLE_ABILITY, REQ_CRITERIA.EMPTY)
        vehicle = g_currentVehicle.item
        for item in data.values():
            if self.__isInValidPrebattle():
                item.isUnlocked = item.innationID in self.getUnlockedAbilityIds()
                if vehicle is not None:
                    mayInstall, _ = item.mayInstall(vehicle)
                    if not mayInstall:
                        item.isUnlocked = False
            item.isUnlocked = False

        return

    def __invalidateBattleAbilitiesForVehicle(self):
        vehicle = g_currentVehicle.item
        if vehicle is None or vehicle.descriptor.type.level not in self.__lobbyContext.getServerSettings().epicBattles.validVehicleLevels or not self.__isInValidPrebattle():
            return
        else:
            amountOfSlots = self.getNumAbilitySlots(vehicle.descriptor.type)
            selectedItems = [None] * amountOfSlots
            skillInfo = self.getAllSkillsInformation()
            selectedSkills = self.getSelectedSkills(vehicle.intCD)
            battleAbilities = self.__itemsCache.items.getItems(GUI_ITEM_TYPE.BATTLE_ABILITY, REQ_CRITERIA.EMPTY)
            for item in battleAbilities.values():
                for index, skillID in enumerate(selectedSkills):
                    if skillID is not None and skillID >= 0:
                        if skillInfo[skillID].getSkillInfo() and item.innationID == skillInfo[skillID].getSkillInfo().eqID:
                            selectedItems[index] = item

            vehicle.battleAbilities.setLayout(*selectedItems)
            vehicle.battleAbilities.setInstalled(*selectedItems)
            return

    def __analyzeClientSystem(self):
        stats = BigWorld.wg_getClientStatistics()
        stats['graphicsEngine'] = self.__settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE)
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
        items = {GUI_ITEM_TYPE.VEHICLE, GUI_ITEM_TYPE.BATTLE_ABILITY, GUI_ITEM_TYPE.CUSTOMIZATION}
        if items.intersection(invDiff):
            self.__invalidateBattleAbilities()

    def __updateSounds(self, isEpicSoundMode):
        if isEpicSoundMode != self.__isEpicSoundMode:
            _FrontLineSounds.onChange(isEpicSoundMode)
            self.__isEpicSoundMode = isEpicSoundMode

    @adisp_async
    @adisp_process
    def __confirmFightButtonPressEnabled(self, callback):
        if not self.__isInValidPrebattle():
            callback(True)
            return
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        filters = self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        isEpicPerformanceWarningEnabled = not AccountSettings.getSettings('isEpicPerformanceWarningClicked')
        if isEpicPerformanceWarningEnabled:
            result, checkboxChecked = yield DialogsInterface.showI18nCheckBoxDialog('epicBattleConfirmDialog')
            filters['isEpicPerformanceWarningClicked'] = checkboxChecked
            AccountSettings.setSettings('isEpicPerformanceWarningClicked', checkboxChecked)
        else:
            result = True
        callback(result)

    def __serverSettingsChangeBrowserHandler(self, browser, diff):
        if not diff.get(Configs.EPIC_CONFIG.value, {}).get('isEnabled'):
            browser.onCloseView()

    @property
    def __metaSettings(self):
        return self.__lobbyContext.getServerSettings().epicMetaGame

    def __onTokensUpdate(self, diff):
        if any((key.startswith(EPIC_CHOICE_REWARD_OFFER_GIFT_TOKENS) for key in diff.keys())):
            pass
