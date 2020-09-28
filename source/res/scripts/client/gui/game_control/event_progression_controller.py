# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/event_progression_controller.py
from collections import namedtuple
from enum import Enum, unique
from itertools import chain
import Event
from adisp import process
from constants import Configs, IS_CHINA
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.event_progression.after_battle_reward_view_helpers import getProgressionIconVODict
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.game_control.links import URLMacros
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.tooltips import formatters
from helpers import time_utils
from gui.shared.formatters import text_styles, icons
from helpers import dependency, int2roman
from gui.impl import backport
from items import makeIntCompactDescrByID
from items.components.c11n_constants import CustomizationType
from skeletons.gui.game_control import IEventProgressionController, IEpicBattleMetaGameController, IBattleRoyaleController, IQuestsController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from gui.impl.gen import R
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from constants import QUEUE_TYPE
from web.web_client_api.common import ItemPackType
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.shared.utils.functions import getRelativeUrl
from gui.shared.formatters import time_formatters
from skeletons.connection_mgr import IConnectionManager
from gui.ranked_battles.constants import PrimeTimeStatus
from predefined_hosts import g_preDefinedHosts
from shared_utils import first
EVENT_PROGRESSION_FINISH_TOKEN = 'epicmetagame:progression_finish'
EpicBattlesWidgetTooltipVO = namedtuple('EpicBattlesWidgetTooltipVO', 'progressBarData')
PlayerLevelInfo = namedtuple('PlayerLevelInfo', ('currentLevel', 'levelProgress'))

@unique
class EventProgressionScreens(Enum):
    MAIN = '?preview=1'
    FRONTLINE_RESERVES = 'reserves/'
    FRONTLINE_REWARDS = 'rewards/'

    @classmethod
    def hasValue(cls, value):
        return value in cls.__members__.values()


def _showBrowserView(url):
    from gui.Scaleform.daapi.view.lobby.event_progression.web_handlers import createEventProgressionWebHandlers
    webHandlers = createEventProgressionWebHandlers()
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BROWSER_VIEW, ctx={'url': url,
     'webHandlers': webHandlers,
     'returnAlias': VIEW_ALIAS.LOBBY_HANGAR,
     'onServerSettingsChange': _serverSettingsChangeBrowserHandler}), EVENT_BUS_SCOPE.LOBBY)


def _serverSettingsChangeBrowserHandler(browser, diff):
    eventConfigKeys = (Configs.BATTLE_ROYALE_CONFIG.value, Configs.EVENT_PROGRESSION_CONFIG.value)
    isDisabled = any([ diff.get(config, {}).get('isEnabled') is False for config in eventConfigKeys ])
    if isDisabled:
        browser.onCloseView()


def getLevelStr(level):
    txtId = R.strings.tooltips.eventProgression.level()
    return backport.text(txtId, level=level)


def getLevelData(plLevel):
    items = []
    levelMsgStr = text_styles.stats(getLevelStr(plLevel))
    items.append(formatters.packTextBlockData(text=levelMsgStr, useHtml=True, padding=formatters.packPadding(left=20, right=20, top=-10)))
    return formatters.packBuildUpBlockData(items)


def getTimeTo(timeStamp, textId):
    timeLeft = time_formatters.getTillTimeByResource(timeStamp, R.strings.menu.headerButtons.battle.types.ranked.availability, removeLeadingZeros=True)
    return backport.text(textId, value=text_styles.stats(timeLeft))


@dependency.replace_none_kwargs(eventProgression=IEventProgressionController)
def getTimeToLeftStr(timeStamp, eventProgression=None):
    return getTimeTo(timeStamp, R.strings.tooltips.eventProgression.timeToLeft.season() if eventProgression.getCurrentSeason().isSingleCycleSeason() else R.strings.tooltips.eventProgression.timeToLeft.cycle())


@dependency.replace_none_kwargs(eventProgression=IEventProgressionController)
def getTimeToStartStr(timeStamp, eventProgression=None):
    return getTimeTo(timeStamp, R.strings.tooltips.eventProgression.timeToStart.season() if (eventProgression.getCurrentSeason() or eventProgression.getNextSeason()).isSingleCycleSeason() else R.strings.tooltips.eventProgression.timeToStart.cycle())


class EventProgressionController(IEventProgressionController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __questController = dependency.descriptor(IQuestsController)
    onUpdated = Event.Event()

    def __init__(self):
        self.__urlMacros = URLMacros()
        self.__isEnabled = False
        self.__isFrontLine = False
        self.__isSteelHunter = False
        self.__url = ''
        self.__actualRewardPoints = 0
        self.__seasonRewardPoints = 0
        self.__maxRewardPoints = 0
        self.__rewardPointsTokenID = ''
        self.__seasonPointsTokenID = ''
        self.__rewardVehicles = []
        self.__rewardStyles = []
        self.__currentMode = None
        self.__questCardLevelTxtId = 0
        self.__progressionNameCycleTxtId = 0
        self.__progressionIconId = 0
        self.__selectorLabelTxtId = 0
        self.__selectorRibbonResId = 0
        self.__allCyclesWasEndedResId = 0
        self.__selectorData = 0
        self.__selectorType = 0
        self.__selectorQueueType = 0
        self.__questPrefix = ''
        self.__activeQuestIDs = []
        self.__primeTimeTitle = ''
        self.__primeTimeBg = ''
        return

    @property
    def isEnabled(self):
        return self.__isEnabled

    @property
    def isFrontLine(self):
        return self.__isEnabled and self.__isFrontLine

    @property
    def isSteelHunter(self):
        return self.__isEnabled and self.__isSteelHunter

    @property
    def url(self):
        return self.__url

    @property
    def questPrefix(self):
        return self.__questPrefix

    @property
    def actualRewardPoints(self):
        return self.__actualRewardPoints

    @property
    def seasonRewardPoints(self):
        dossier = self.__itemsCache.items.getAccountDossier()
        achievements = dossier.getDossierDescr().expand('epicSeasons')
        achievements = chain(achievements.items(), dossier.getDossierDescr().expand('battleRoyaleSeasons').items())
        seasonRewardPoints = self.__seasonRewardPoints
        for (seasonID, cycleID), cycleAchievements in achievements:
            if not self.validateSeasonData(seasonID, cycleID):
                continue
            _, _, awardPoints, _ = cycleAchievements
            seasonRewardPoints += awardPoints

        return seasonRewardPoints

    @property
    def maxRewardPoints(self):
        return self.__maxRewardPoints

    @property
    def rewardPointsTokenID(self):
        return self.__rewardPointsTokenID

    @property
    def rewardVehicles(self):
        return self.__rewardVehicles

    @property
    def rewardStyles(self):
        return self.__rewardStyles

    @property
    def questCardLevelTxtId(self):
        return self.__questCardLevelTxtId

    @property
    def flagIconId(self):
        return self.__flagIconId

    @property
    def questTooltipHeaderIconId(self):
        return self.__questTooltipHeaderIconId

    @property
    def questTooltipHeaderTxtId(self):
        return self.__questTooltipHeaderTxtId

    @property
    def selectorLabelTxtId(self):
        return self.__selectorLabelTxtId

    @property
    def selectorRibbonResId(self):
        return self.__selectorRibbonResId

    @property
    def aboutEventProgressionResId(self):
        if self.__currentMode:
            if self.__currentMode.getCurrentSeason() or self.__currentMode.getNextSeason():
                self.__allCyclesWasEndedResId = R.strings.event_progression.selectorTooltip.eventProgression.waitNext_cn() if IS_CHINA else R.strings.event_progression.selectorTooltip.eventProgression.waitNext()
            else:
                self.__allCyclesWasEndedResId = R.strings.event_progression.selectorTooltip.eventProgression.ended_cn() if IS_CHINA else R.strings.event_progression.selectorTooltip.eventProgression.ended()
        return self.__allCyclesWasEndedResId

    @property
    def selectorData(self):
        return self.__selectorData

    @property
    def selectorType(self):
        return self.__selectorType

    @property
    def selectorQueueType(self):
        return self.__selectorQueueType

    @process
    def openURL(self, url=None):
        requestUrl = url or self.__url
        if requestUrl:
            parsedUrl = yield self.__urlMacros.parse(requestUrl)
            if parsedUrl:
                _showBrowserView(parsedUrl)

    def getProgressionXPTokenID(self):
        return self.__currentController.PROGRESSION_XP_TOKEN if self.__currentController else ''

    def isAvailable(self):
        return self.isFrontLine or self.isSteelHunter

    def modeIsEnabled(self):
        return self.__currentController.getModeSettings().isEnabled if self.__currentController else False

    def modeIsAvailable(self):
        return self.isAvailable() and self.isInPrimeTime() and self.isActive()

    def isFrozen(self):
        if self.__currentController:
            for primeTime in self.getPrimeTimes().values():
                if primeTime.hasAnyPeriods():
                    return False

        return True

    def isActive(self):
        return self.modeIsEnabled() and self.__currentController.getCurrentSeason() is not None and self.__currentController.getCurrentCycleInfo()[1] if self.__currentController else False

    def isDailyQuestsRefreshAvailable(self):
        dayTimeLeft = time_utils.getDayTimeLeft()
        cycleTimeLeft = self.getCurrentCycleTimeLeft()
        currentPrimeTimeEnd = self.getCurrentPrimeTimeEnd()
        if currentPrimeTimeEnd is None:
            return False
        else:
            primeTimeTimeLeft = currentPrimeTimeEnd - time_utils.getCurrentLocalServerTimestamp()
            state1 = self.hasPrimeTimesLeft() or primeTimeTimeLeft > dayTimeLeft
            state2 = cycleTimeLeft > dayTimeLeft
            return state1 and state2

    def getPlayerLevelInfo(self):
        if not (self.isSteelHunter or self.isFrontLine):
            return PlayerLevelInfo(None, None)
        else:
            levelInfo = self.__currentController.getPlayerLevelInfo()
            if self.isFrontLine:
                levelInfo = self.__currentController.getPlayerLevelInfo()[1:]
            return PlayerLevelInfo(*levelInfo)

    def getActiveQuestIDs(self):
        self.__activeQuestIDs = [ q.getID() for q in self.getActiveQuestsAsDict().values() ]
        return self.__activeQuestIDs

    def getActiveQuestsAsDict(self):
        if not (self.__isEnabled and self.modeIsEnabled()):
            return {}
        quests = {k:v for k, v in self.__eventsCache.getQuests().items() if self.__isActiveQuest(v)}
        return quests

    def getQuestForVehicle(self, vehicle, sortByPriority=False, questIDs=None):
        questIDs = questIDs if questIDs is not None else self.getActiveQuestIDs()
        quests = [ q for q in self.__questController.getQuestForVehicle(vehicle) if q.getID() in questIDs ]
        if sortByPriority:
            quests.sort(key=lambda _q: _q.getPriority(), reverse=True)
        return quests

    def isUnavailableQuestByID(self, questID):
        if questID not in self.__activeQuestIDs:
            return False
        if self.__isFrontLine:
            if not self.__isMaxLevel():
                return True
        return False

    def getUnavailableQuestMessage(self, questID):
        if questID not in self.__activeQuestIDs:
            return ''
        if self.__isFrontLine:
            if not self.__isMaxLevel():
                idMsg = R.strings.event_progression.questsTooltip.frontLine.notReachLevel()
                return backport.text(idMsg, level=self.__currentController.getMaxPlayerLevel())

    def getRewardVehiclePrice(self, vehicleCD):
        return {intCD:price for intCD, price in self.__rewardVehicles}.get(vehicleCD, 0)

    def getRewardStylePrice(self, styleID):
        return {styleId:price for styleId, price in self.__rewardStyles}.get(styleID, 0)

    def getAllLevelAwards(self):
        awardsData = dict()
        abilityPts = None
        if self.isFrontLine:
            abilityPts = self.__lobbyContext.getServerSettings().epicMetaGame.metaLevel['abilityPointsForLevel']
        allQuests = self.__eventsCache.getAllQuests()
        for questKey, questData in allQuests.iteritems():
            if self.__currentController.TOKEN_QUEST_ID in questKey:
                _, _, questNum = questKey.partition(self.__currentController.TOKEN_QUEST_ID)
                if questNum:
                    questLvl = int(questNum)
                    questBonuses = questData.getBonuses()
                    awardsData[questLvl] = self.__packBonuses(questBonuses, questLvl, abilityPts)

        return awardsData

    def getLevelAwards(self, level):
        allAwards = self.getAllLevelAwards()
        return allAwards[level] if level in allAwards else []

    def showCustomScreen(self, screen):
        if self.__url and EventProgressionScreens.hasValue(screen):
            self.openURL('/'.join((self.__url.strip('/'), screen.value.strip('/'))))

    def getPrimeTimeTitle(self):
        return self.__primeTimeTitle

    def getPrimeTimeBg(self):
        return self.__primeTimeBg

    def onPrimeTimeStatusUpdatedAddEvent(self, event):
        if self.__currentController:
            self.__currentController.onPrimeTimeStatusUpdated += event

    def onPrimeTimeStatusUpdatedRemoveEvent(self, event):
        if self.__currentController:
            self.__currentController.onPrimeTimeStatusUpdated -= event

    def getTimer(self):
        return self.__currentController.getTimer()

    def isInPrimeTime(self):
        _, _, isNow = self.getPrimeTimeStatus()
        return isNow

    @classmethod
    def validateSeasonData(cls, seasonID, cycleID):
        seasonValidationData = {season.getSeasonID():[ cycle.ID for cycle in season.getAllCycles().values() ] for season in cls.getMostRelevantSeasons().itervalues()}
        return seasonID in seasonValidationData and cycleID in seasonValidationData.get(seasonID, [])

    @classmethod
    def getMostRelevantSeasons(cls):
        epicMetaGameCtrl = dependency.instance(IEpicBattleMetaGameController)
        battleRoyaleCtrl = dependency.instance(IBattleRoyaleController)
        seasons = {key:value for key, value in zip(('frontline', 'battle_royale'), (first(filter(None, (mode.getCurrentSeason(), mode.getNextSeason(), mode.getPreviousSeason()))) for mode in (epicMetaGameCtrl, battleRoyaleCtrl)))}
        return seasons

    @classmethod
    def getCalendarInfo(cls):
        calendarData = dict()
        for key, selectedSeason in cls.getMostRelevantSeasons().iteritems():
            if selectedSeason is not None:
                calendarData[key] = {}
                calendarData[key]['season'] = {'id': selectedSeason.getSeasonID(),
                 'start': selectedSeason.getStartDate(),
                 'end': selectedSeason.getEndDate()}
                calendarData[key]['cycles'] = [ {'id': cycle.ID,
                 'start': cycle.startDate,
                 'end': cycle.endDate,
                 'announce_only': cycle.announceOnly} for cycle in selectedSeason.getAllCycles().values() ]

        return calendarData

    def getCurrentSeason(self):
        return self.__currentController.getCurrentSeason() if self.__currentController else None

    def getNextSeason(self):
        return self.__currentController.getNextSeason() if self.__currentController else None

    def getPreviousSeason(self):
        return self.__currentController.getPreviousSeason() if self.__currentController else None

    def hasAnySeason(self):
        return self.__currentController.hasAnySeason() if self.__currentController else False

    def getCurrentOrNextActiveCycleNumber(self, season):
        return self.__currentController.getCurrentOrNextActiveCycleNumber(season) if self.__currentController else 0

    def getMaxPlayerLevel(self):
        return self.__currentController.getMaxPlayerLevel()

    def isNeedAchieveMaxLevelForDailyQuest(self):
        level, _ = self.getPlayerLevelInfo()
        return True if self.isFrontLine and level < self.getMaxPlayerLevel() else False

    def getCurrentCycleInfo(self):
        return self.__currentController.getCurrentCycleInfo() if self.__currentController else (None, False)

    def getPrimeTimeStatus(self, peripheryID=None):
        return self.__currentController.getPrimeTimeStatus(peripheryID) if self.__currentController else (PrimeTimeStatus.NOT_SET, 0, False)

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

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        return self.__currentController.getPrimeTimesForDay(selectedTime, groupIdentical)

    def getPrimeTimes(self):
        return self.__currentController.getPrimeTimes() if self.__currentController else (0, 0, False)

    def getPerformanceGroup(self):
        return self.__currentController.getPerformanceGroup() if self.__currentController else None

    def getCurrentCycleTimeLeft(self):
        currentCycleEndTime, isCycleActive = self.getCurrentCycleInfo()
        cycleTimeLeft = currentCycleEndTime - time_utils.getCurrentLocalServerTimestamp() if isCycleActive else None
        return cycleTimeLeft

    def getCurrentPrimeTimeEnd(self):
        primeTimes = self.getPrimeTimes()
        currentPrimeTimeEnd = None
        for primeTime in primeTimes.values():
            periods = primeTime.getPeriodsActiveForTime(time_utils.getCurrentLocalServerTimestamp())
            for period in periods:
                _, endTime = period
                currentPrimeTimeEnd = max(endTime, currentPrimeTimeEnd)

        return currentPrimeTimeEnd

    def hasPrimeTimesLeft(self):
        currentCycleEndTime, isCycleActive = self.getCurrentCycleInfo()
        if not isCycleActive:
            return False
        primeTimes = self.getPrimeTimes()
        return any([ primeTime.getNextPeriodStart(time_utils.getCurrentLocalServerTimestamp(), currentCycleEndTime) for primeTime in primeTimes.values() ])

    def getStats(self):
        return self.__currentController.getStats()

    def getPointsProgressForLevel(self, level):
        return self.__currentController.getPointsProgressForLevel(level)

    def getEpicMetascreenData(self):
        if self.isFrontLine:
            metaGameStats = self.getStats()
            data = {'average_xp': metaGameStats.averageXP,
             'is_reserves_available_in_fl_menu': self.__currentController.isReservesAvailableInFLMenu()}
            return data
        elif self.isSteelHunter:
            metaGameStats = self.getStats()
            data = {'kill_count': metaGameStats.killCount}
            return data
        else:
            return None

    def onLobbyInited(self, ctx):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__itemsCache.onSyncCompleted += self.__updatePlayerData
        self.__updateSettings()
        self.__updatePlayerData()

    def isCurrentSeasonInPrimeTime(self):
        season = self.getCurrentSeason()
        if season is None or season.getCycleInfo() is None:
            return False
        else:
            isInPrime = not self.isInPrimeTime()
            isEnable = self.modeIsEnabled()
            isAvailable = self.modeIsAvailable()
            return isInPrime and isEnable and not isAvailable and season.getCycleInfo()

    def getHeaderTooltipPack(self):
        items = [self.__getTopBackgroundTooltipWithTextData()]
        bottom = -30
        if not self.isCurrentSeasonInPrimeTime() and not self.modeIsAvailable():
            items.append(self.__getRewardStylesData() if IS_CHINA else self.__getRewardVehiclesData())
            bottom = 0
        return formatters.packBuildUpBlockData(items, padding=formatters.packPadding(bottom=bottom))

    def getSeasonInfoTooltipPack(self):
        season = self.getCurrentSeason() or self.getNextSeason()
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        isPrimeTime = self.isCurrentSeasonInPrimeTime()
        if season and season.isSingleCycleSeason():
            seasonsOverResID = R.strings.tooltips.eventProgression.allSeasonsAreOver.single()
        else:
            seasonsOverResID = R.strings.tooltips.eventProgression.allSeasonsAreOver.multi()
        if isPrimeTime or self.modeIsAvailable():
            cycle = season.getCycleInfo()
            getDate = lambda c: c.endDate
            getTimeToStr = getTimeToLeftStr
        else:
            cycle = season.getNextByTimeCycle(currentTime) if season else None
            getDate = lambda c: c.startDate
            getTimeToStr = getTimeToStartStr
        if cycle is not None:
            if self.modeIsEnabled() or IS_CHINA:
                if season.isSingleCycleSeason():
                    infoStrResID = R.strings.menu.headerButtons.battle.types.epic.extra.currentSeason_cn() if IS_CHINA else R.strings.menu.headerButtons.battle.types.epic.extra.currentSeason()
                    seasonResID = R.strings.epic_battle.season.num(season.getSeasonID())
                    name = backport.text(seasonResID.name()) if seasonResID else None
                else:
                    infoStrResID = self.__progressionNameCycleTxtId
                    name = self.getCurrentOrNextActiveCycleNumber(season)
                title = backport.text(infoStrResID, season=name)
            else:
                title = backport.text(self.__selectorLabelTxtId)
            description = getTimeToStr(getDate(cycle) - currentTime) if self.modeIsEnabled() else text_styles.error(backport.text(R.strings.tooltips.eventProgression.disabled()))
        else:
            title = ''
            description = ''
            if self.isFrontLine:
                title = backport.text(R.strings.tooltips.eventProgression.frontLine())
                description = backport.text(seasonsOverResID) if self.modeIsEnabled() else text_styles.error(backport.text(R.strings.tooltips.eventProgression.disabled()))
            elif self.isSteelHunter:
                title = backport.text(self.__allCyclesWasEndedResId)
        return formatters.packBuildUpBlockData([formatters.packImageTextBlockData(title=text_styles.middleTitle(title), txtPadding=formatters.packPadding(top=8, left=94), desc=text_styles.main(description), descPadding=formatters.packPadding(top=8, left=94), txtOffset=1, txtGap=-1, img=backport.image(self.__progressionIconId), imgPadding=formatters.packPadding(top=1, left=18))])

    def getCurrentModeAlias(self):
        return self.__currentController.MODE_ALIAS

    def getCycleStatusTooltipPack(self):
        items = []
        season = self.__currentController.getCurrentSeason() or self.__currentController.getNextSeason()
        levelInfo = self.getPlayerLevelInfo()
        cycleNumber = self.getCurrentOrNextActiveCycleNumber(season)
        if season.isSingleCycleSeason():
            infoStrResID = R.strings.menu.headerButtons.battle.types.epic.extra.currentSeason_cn() if IS_CHINA else R.strings.menu.headerButtons.battle.types.epic.extra.currentSeason()
            seasonResID = R.strings.epic_battle.season.num(season.getSeasonID())
            name = backport.text(seasonResID.name()) if seasonResID else None
        else:
            infoStrResID = self.__progressionNameCycleTxtId
            name = int2roman(cycleNumber)
        seasonDescr = text_styles.middleTitle(backport.text(infoStrResID, season=name))
        items.append(formatters.packTextBlockData(text=seasonDescr, useHtml=True, padding=formatters.packPadding(left=20, right=20)))
        currentCycle = season.getCycleInfo()
        tDiff = currentCycle.endDate - time_utils.getCurrentLocalServerTimestamp() if currentCycle is not None else 0
        timeLeft = text_styles.main(getTimeToLeftStr(tDiff))
        items.append(formatters.packTextBlockData(text=timeLeft, useHtml=True, padding=formatters.packPadding(left=20, right=20)))
        linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BATTLE_ROYALE_META_LEVEL_BLOCK_LINKAGE if self.isSteelHunter else BLOCKS_TOOLTIP_TYPES.TOOLTIP_EPIC_BATTLE_META_LEVEL_BLOCK_LINKAGE
        items.append(formatters.packBuildUpBlockData(blocks=[formatters.packBlockDataItem(linkage=linkage, data=getProgressionIconVODict(cycleNumber=cycleNumber, playerLevel=levelInfo.currentLevel))], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        items.append(getLevelData(levelInfo.currentLevel))
        if levelInfo.currentLevel < self.getMaxPlayerLevel():
            items.append(self.__getCurrentMaxProgress(playerLevel=levelInfo.currentLevel, playerFamePts=levelInfo.levelProgress))
            items.append(self.__getPlayerProgressToLevelBlock(playerLevel=levelInfo.currentLevel, playerFamePts=levelInfo.levelProgress))
        else:
            unlockedStr = backport.text(R.strings.tooltips.eventProgression.unlockedDailyMissions())
            items.append(formatters.packTextBlockData(text=text_styles.main(unlockedStr), useHtml=True, padding=formatters.packPadding(left=20, right=20, top=-7)))
        return formatters.packBuildUpBlockData(items)

    def getExchangeInfo(self):
        exchange = self.__lobbyContext.getServerSettings().eventProgression.exchange
        return {'expireTimestamp': exchange['expireTimestamp'],
         'exchangeRate': exchange['exchangeRate'],
         'loginDeadlineTimestamp': exchange['loginDeadlineTimestamp']}

    @property
    def __currentController(self):
        if self.__currentMode is None:
            self.__updateSettings()
        return self.__currentMode

    def __isMaxLevel(self):
        modeCtrl = self.__currentController
        levelInfo = self.getPlayerLevelInfo()
        maxLevel = modeCtrl.getMaxPlayerLevel()
        return levelInfo.currentLevel >= maxLevel

    def __isActiveQuest(self, q):
        if self.__questPrefix not in q.getID():
            return False
        if self.__isFrontLine:
            return True
        if self.__isSteelHunter:
            validationResult = q.isAvailable()
            isReqsAvailable = q.accountReqs.isAvailable()
            return (validationResult.isValid or validationResult.reason == 'dailyComplete') and isReqsAvailable
        return False

    def __packBonuses(self, bonuses, level, abilityPts):
        result = [{'id': 0,
          'type': ItemPackType.CUSTOM_SUPPLY_POINT,
          'value': abilityPts[level - 1],
          'icon': {AWARDS_SIZES.SMALL: getRelativeUrl(backport.image(R.images.gui.maps.icons.epicBattles.awards.c_48x48.abilityToken())),
                   AWARDS_SIZES.BIG: getRelativeUrl(backport.image(R.images.gui.maps.icons.epicBattles.awards.c_80x80.abilityToken()))}}] if abilityPts else []
        for bonus in bonuses:
            bonusList = bonus.getWrappedEpicBonusList()
            for bonusEntry in bonusList:
                bonusEntry['icon'] = {size:getRelativeUrl(path) for size, path in bonusEntry['icon'].iteritems()}

            result.extend(bonusList)

        return result

    def __getPlayerProgressToLevelBlock(self, playerLevel, playerFamePts):
        famePtsToProgress = self.getPointsProgressForLevel(playerLevel)
        data = EpicBattlesWidgetTooltipVO(progressBarData={'value': playerFamePts,
         'maxValue': famePtsToProgress})._asdict()
        res = formatters.packBlockDataItem(linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_META_LEVEL_PROGRESS_BLOCK_LINKAGE, data=data, padding=formatters.packPadding(left=20))
        return res

    def __getCurrentMaxProgress(self, playerLevel, playerFamePts):
        items = []
        famePtsToProgress = self.getPointsProgressForLevel(playerLevel)
        currentPoint = text_styles.stats(str(playerFamePts))
        fameTo = text_styles.main(str(famePtsToProgress))
        currentPointMaxPoint = text_styles.concatStylesWithSpace(currentPoint, text_styles.main('/'), fameTo)
        text = text_styles.main(currentPointMaxPoint)
        marginTop = 7
        icon = None
        if self.isFrontLine:
            marginTop = 0
            iconSrc = backport.image(R.images.gui.maps.icons.epicBattles.fame_point_tiny())
            icon = icons.makeImageTag(source=iconSrc, width=24, height=24)
        elif self.isSteelHunter:
            marginTop = 6
            iconSrc = backport.image(R.images.gui.maps.icons.battleRoyale.progression_point())
            icon = icons.makeImageTag(source=iconSrc, width=16, height=16)
        if icon is not None:
            text = text_styles.concatStylesWithSpace(text, icon)
        items.append(formatters.packAlignedTextBlockData(text=text, align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT, padding=formatters.packPadding(left=20, right=20, top=-35)))
        return formatters.packBuildUpBlockData(items, padding=formatters.packPadding(top=marginTop))

    def __getRewardVehiclesData(self):
        rewardVehiclesNames = [ text_styles.stats(v.shortUserName) for v in self.__getRewardVehicles() ]
        promo = R.strings.event_progression.selectorTooltip.eventProgression.promo
        text = backport.text(promo.multi() if len(rewardVehiclesNames) > 1 else promo.single(), vehicles=', '.join(rewardVehiclesNames[:-1]), vehicle=rewardVehiclesNames[-1])
        return formatters.packTextBlockData(text_styles.main(text), padding=formatters.packPadding(top=-10, left=20, right=25))

    def __getRewardStylesData(self):
        rewardStylesNames = [ text_styles.stats(s.userName) for s in self.__getRewardStyles() ]
        promo = R.strings.event_progression.selectorTooltip.eventProgression.promo
        text = backport.text(promo.multi_cn() if len(rewardStylesNames) > 1 else promo.single_cn(), styles=', '.join(rewardStylesNames[:-1]), style=rewardStylesNames[-1])
        return formatters.packTextBlockData(text_styles.main(text), padding=formatters.packPadding(top=-10, left=20, right=25))

    def __getTopBackgroundTooltipWithTextData(self):
        if IS_CHINA:
            headerResId = R.strings.tooltips.eventProgression.frontLine
            iconResId = R.images.gui.maps.icons.epicBattles.prestigePoints
            background = R.images.gui.maps.icons.epicBattles.backgrounds.widget_tooltip_background_cn
        else:
            headerResId = R.strings.tooltips.eventProgression.header
            iconResId = R.images.gui.maps.icons.epicBattles.rewardPoints
            background = R.images.gui.maps.icons.epicBattles.backgrounds.widget_tooltip_background
        header = text_styles.bonusLocalText(backport.text(headerResId()))
        iconSrc = backport.image(iconResId.c_16x16())
        iconCurrency = icons.makeImageTag(source=iconSrc, width=16, height=16, vSpace=-3)
        currency = text_styles.concatStylesWithSpace(self.__getCurrencyCurrentStr(), iconCurrency)
        return formatters.packImageTextBlockData(title=header, txtPadding=formatters.packPadding(top=16, left=20), desc=currency, descPadding=formatters.packPadding(top=6, left=20), txtOffset=1, txtGap=-1, img=backport.image(background()))

    def __getCurrencyCurrentStr(self):
        res = text_styles.main(backport.text(R.strings.tooltips.eventProgression.currency()) + ' ') + text_styles.stats(int(self.actualRewardPoints))
        return res

    def __getRewardVehicles(self):
        rewardVehiclesIds = [ intCD for intCD, _ in self.rewardVehicles ]
        rewardVehicles = self.__itemsCache.items.getVehicles(REQ_CRITERIA.IN_CD_LIST(rewardVehiclesIds))
        return [ rewardVehicles[intCD] for intCD in rewardVehiclesIds ]

    def __getRewardStyles(self):
        rewardStylesIds = [ makeIntCompactDescrByID('customizationItem', CustomizationType.STYLE, styleID) for styleID, _ in self.rewardStyles ]
        rewardStyles = self.__itemsCache.items.getStyles(REQ_CRITERIA.IN_CD_LIST(rewardStylesIds))
        return [ rewardStyles[intCD] for intCD in rewardStylesIds ]

    def __clear(self):
        self.__itemsCache.onSyncCompleted -= self.__updatePlayerData
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def __onServerSettingsChange(self, diff):
        if Configs.EVENT_PROGRESSION_CONFIG.value in diff:
            self.__updateSettings()
            self.onUpdated(diff)

    def __onSyncCompleted(self, *args, **kwargs):
        self.__updatePlayerData()
        self.onUpdated(args, kwargs)

    def __updateSettings(self):
        s = self.__lobbyContext.getServerSettings().eventProgression
        self.__isEnabled = s.isEnabled
        self.__isFrontLine = s.isFrontLine
        self.__isSteelHunter = s.isSteelHunter
        self.__url = s.url
        self.__maxRewardPoints = s.maxRewardPoints
        self.__rewardPointsTokenID = s.rewardPointsTokenID
        self.__seasonPointsTokenID = s.seasonPointsTokenID
        self.__rewardVehicles = s.rewardVehicles
        self.__rewardStyles = s.rewardStyles
        self.__questPrefix = s.questPrefix
        if self.isSteelHunter is True:
            self.__updateSteelHunterData()
        elif self.isFrontLine is True:
            self.__updateFrontLineData()
        else:
            self.__currentMode = None
        return

    def __updateFrontLineData(self):
        self.__currentMode = dependency.instance(IEpicBattleMetaGameController)
        self.__flagIconId = R.images.gui.maps.icons.library.hangarFlag.flag_epic()
        self.__questTooltipHeaderIconId = R.images.gui.maps.icons.quests.epic_quests_infotip()
        self.__questTooltipHeaderTxtId = R.strings.epic_battle.questsTooltip.epicBattle.header()
        self.__questCardLevelTxtId = R.strings.event_progression.questsCard.frontLine.getLevel()
        self.__progressionNameCycleTxtId = (R.strings.tooltips.eventProgression.season_cn if IS_CHINA else R.strings.tooltips.eventProgression.season)()
        self.__progressionIconId = R.images.gui.maps.icons.battleTypes.c_64x64.frontline()
        self.__selectorLabelTxtId = R.strings.menu.headerButtons.battle.types.epic()
        self.__selectorRibbonResId = R.images.gui.maps.icons.epicBattles.ribbon_small()
        self.__selectorData = PREBATTLE_ACTION_NAME.EPIC
        self.__selectorType = SELECTOR_BATTLE_TYPES.EVENT_PROGRESSION
        self.__selectorQueueType = QUEUE_TYPE.EPIC
        self.__primeTimeTitle = R.strings.epic_battle.primeTime.title()
        self.__primeTimeBg = R.images.gui.maps.icons.epicBattles.primeTime.prime_time_back_default()
        self.__allCyclesWasEndedResId = R.strings.event_progression.selectorTooltip.eventProgression.waitNext()

    def __updateSteelHunterData(self):
        self.__currentMode = dependency.instance(IBattleRoyaleController)
        self.__flagIconId = R.images.gui.maps.icons.library.hangarFlag.flag_epic_steelhunter()
        self.__questTooltipHeaderIconId = R.images.gui.maps.icons.quests.epic_steelhunter_quests_infotip()
        self.__questTooltipHeaderTxtId = R.strings.epic_battle.questsTooltip.epicBattle.steelhunter.header()
        self.__questCardLevelTxtId = R.strings.event_progression.questsCard.steelHunter.getLevel()
        self.__progressionNameCycleTxtId = R.strings.tooltips.eventProgression.steelHunter.season()
        self.__progressionIconId = R.images.gui.maps.icons.battleTypes.c_64x64.steelhunt()
        self.__selectorLabelTxtId = R.strings.menu.headerButtons.battle.types.battleRoyale()
        self.__selectorRibbonResId = R.images.gui.maps.icons.battleRoyale.ribbon_small()
        self.__selectorData = PREBATTLE_ACTION_NAME.BATTLE_ROYALE
        self.__selectorType = SELECTOR_BATTLE_TYPES.BATTLE_ROYALE
        self.__selectorQueueType = QUEUE_TYPE.BATTLE_ROYALE
        self.__primeTimeTitle = R.strings.epic_battle.primeTime.steelhunter.title()
        self.__primeTimeBg = R.images.gui.maps.icons.battleRoyale.primeTime.prime_time_back_default()
        self.__allCyclesWasEndedResId = R.strings.event_progression.selectorTooltip.eventProgression.ended()

    def __updatePlayerData(self, *_):
        t = self.__itemsCache.items.tokens.getTokens()
        self.__actualRewardPoints = t.get(self.__rewardPointsTokenID, (0, 0))[1]
        self.__seasonRewardPoints = t.get(self.__seasonPointsTokenID, (0, 0))[1]
