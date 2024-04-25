# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/battle_pass_controller.py
import bisect
import logging
from collections import namedtuple
from copy import deepcopy
from itertools import groupby
from Event import Event, EventManager
from PlayerEvents import g_playerEvents
from adisp import adisp_process
from battle_pass_common import BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS, BATTLE_PASS_CONFIG_NAME, BATTLE_PASS_OFFER_TOKEN_PREFIX, BATTLE_PASS_PDATA_KEY, BATTLE_PASS_SELECT_BONUS_NAME, BATTLE_PASS_STYLE_PROGRESS_BONUS_NAME, BattlePassConfig, BattlePassConsts, BattlePassState, getBattlePassPassTokenName, BattlePassChapterType, getMaxAvalable3DStyleProgressInChapter
from constants import ARENA_BONUS_TYPE, OFFERS_ENABLED_KEY, QUEUE_TYPE
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager, awardsFactory
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_helpers import getOfferTokenByGift, getPointsInfoStringID
from gui.battle_pass.state_machine.delegator import BattlePassRewardLogic
from gui.battle_pass.state_machine.machine import BattlePassStateMachine
from gui.shared.gui_items.processors.battle_pass import BattlePassActivateChapterProcessor
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from helpers.events_handler import EventsHandler
from helpers.server_settings import serverSettingsChangeListener
from shared_utils import findFirst, first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
TopPoints = namedtuple('TopPoints', ['label', 'winPoint', 'losePoint'])
BattleRoyaleTopPoints = namedtuple('BattleRoyaleTopPoints', ['label', 'points'])
PointsDifference = namedtuple('PointsDifference', ['bonus', 'top', 'textID'])

class BattlePassController(IBattlePassController, EventsHandler):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__oldPoints = 0
        self.__oldLevel = 0
        self.__currentMode = None
        self.__eventsManager = EventManager()
        self.__seasonChangeNotifier = SimpleNotifier(self.__getTimeToNotifySeasonChanged, self.__onNotifySeasonChanged)
        self.__marathonChapterNotifier = SimpleNotifier(self.__getTimeToMarathonChapterExpired, self.__onNotifyMarathonChapterExpired)
        self.onPointsUpdated = Event(self.__eventsManager)
        self.onLevelUp = Event(self.__eventsManager)
        self.onBattlePassIsBought = Event(self.__eventsManager)
        self.onSelectTokenUpdated = Event(self.__eventsManager)
        self.onSeasonStateChanged = Event(self.__eventsManager)
        self.onMarathonChapterExpired = Event(self.__eventsManager)
        self.onBattlePassSettingsChange = Event(self.__eventsManager)
        self.onFinalRewardStateChange = Event(self.__eventsManager)
        self.onOffersUpdated = Event(self.__eventsManager)
        self.onRewardSelectChange = Event(self.__eventsManager)
        self.onChapterChanged = Event(self.__eventsManager)
        self.__rewardLogic = None
        return

    def init(self):
        super(BattlePassController, self).init()
        g_playerEvents.onClientUpdated += self.__onTokensUpdate
        self.__rewardLogic = BattlePassRewardLogic(BattlePassStateMachine())
        BattlePassAwardsManager.init()

    def onLobbyInited(self, event):
        self._subscribe()
        self.__seasonChangeNotifier.startNotification()
        if any((self.isMarathonChapter(chapterID) for chapterID in self.getChapterIDs())):
            self.__marathonChapterNotifier.startNotification()
        self.__rewardLogic.start()
        self.onBattlePassSettingsChange(self.__getConfig().mode, self.__currentMode)
        self.__currentMode = self.__getConfig().mode
        storageData = self.__settingsCore.serverSettings.getBPStorage()
        self.__settingsCore.serverSettings.updateBPStorageData(storageData)

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()
        self.__clearFields()
        self.__rewardLogic.stop()

    def fini(self):
        self.__stop()
        self.__rewardLogic.stop()
        self.__clearFields()
        self.__eventsManager.clear()
        g_playerEvents.onClientUpdated -= self.__onTokensUpdate
        super(BattlePassController, self).fini()

    def isBought(self, chapterID, seasonID=None):

        def getTokens(season, chapter):
            return self.__itemsCache.items.tokens.getTokens().get(getBattlePassPassTokenName(season, chapter))

        if seasonID is None:
            seasonID = self.getSeasonID()
        if chapterID is None:
            chapterID = self.getCurrentChapterID()
            if not chapterID:
                return False
        if not self.isMarathonChapter(chapterID) and bool(getTokens(seasonID, 0)):
            return True
        else:
            token = getTokens(seasonID, chapterID)
            return token is not None

    def isOfferEnabled(self):
        return self.__lobbyContext.getServerSettings().isOffersEnabled()

    def isEnabled(self):
        return self.__getConfig().isEnabled()

    def isActive(self):
        return self.__getConfig().isActive(time_utils.getServerUTCTime())

    def isVisible(self):
        return self.isSeasonStarted() and not self.isDisabled() and not self.isSeasonFinished()

    def isDisabled(self):
        return not self.isActive() and not self.isPaused()

    def isPaused(self):
        return self.__getConfig().isPaused()

    def isSeasonStarted(self):
        return self.__getConfig().seasonStart <= time_utils.getServerUTCTime()

    def isSeasonFinished(self):
        return self.__getConfig().seasonFinish <= time_utils.getServerUTCTime()

    def isValidBattleType(self, prbEntity):
        return prbEntity.getQueueType() in (QUEUE_TYPE.RANDOMS, QUEUE_TYPE.MAPBOX, QUEUE_TYPE.WINBACK)

    def isGameModeEnabled(self, arenaBonusType):
        return self.__getConfig().isGameModeEnabled(arenaBonusType)

    def isCompleted(self):
        return self.getState() == BattlePassState.COMPLETED

    def isResourceCompleted(self):
        return self.isChapterCompleted(self.getResourceChapterID()) if self.hasResource() else True

    def getSupportedArenaBonusTypes(self):
        return [ arenaBonusType for arenaBonusType in self.__getConfig().points ]

    def getMaxLevelInChapter(self, chapterId=None):
        if chapterId is None:
            chapterId = first(self.getChapterIDs())
        return self.__getConfig().getMaxChapterLevel(chapterId)

    def hasMarathon(self):
        isMarathonChapter = self.isMarathonChapter
        return any((isMarathonChapter(chID) for chID in self.getChapterIDs()))

    def hasResource(self):
        isResourceChapter = self.isResourceChapter
        return any((isResourceChapter(chID) for chID in self.getChapterIDs()))

    def isValidChapterID(self, chapterID):
        return chapterID in self.__getConfig().chapters.keys()

    def getChapterType(self, chapterID):
        chapterType = findFirst(lambda chapters: chapterID in chapters[1], self.__getConfig().getGroupChapterByType().iteritems(), default=(BattlePassChapterType.DEFAULT.value, 0))
        return chapterType[0]

    def getAvailableChapterTypes(self):
        return list(self.__getConfig().getGroupChapterByType().keys())

    def getRegularChapterIds(self):
        return self.__getConfig().getRegularChapterIds()

    def getMarathonChapterID(self):
        return findFirst(self.isMarathonChapter, self.getChapterIDs(), 0)

    def getResourceChapterID(self):
        return findFirst(self.isResourceChapter, self.getChapterIDs(), 0)

    def getRewardType(self, chapterID):
        return self.__getConfig().getRewardType(chapterID)

    def isChapterExists(self, chapterID):
        return chapterID in self.getChapterIDs()

    def getChapterIDs(self):

        def isActive(chID):
            expireTimestamp = self.__getConfig().getChapterExpireTimestamp(chID)
            return not expireTimestamp or time_utils.getServerUTCTime() < expireTimestamp

        return [ chapterID for chapterID in self.__getConfig().getChapterIDs() if isActive(chapterID) ]

    def isMarathonChapter(self, chapterID):
        return self.__getConfig().isMarathonChapter(chapterID)

    def allRegularChaptersPurchased(self):
        return all((self.isBought(chID) for chID in self.__getConfig().getRegularChapterIds()))

    def isResourceChapter(self, chapterID):
        return self.__getConfig().isResourceChapter(chapterID)

    def isResourceChapterAvailable(self):

        def isChapterCompeted(chapterID):
            return self.getLevelInChapter(chapterID) >= self.getMaxLevelInChapter(chapterID)

        return BattlePassChapterType.RESOURCE.value in self.getAvailableChapterTypes() and all((isChapterCompeted(chapterID) for chapterID in self.__getConfig().getRegularChapterIds()))

    def getBattlePassCost(self, chapterID):
        return deepcopy(self.__getConfig().getbattlePassCost(chapterID))

    def getChapterExpiration(self, chapterID):
        return self.__getConfig().getChapterExpireTimestamp(chapterID) if self.isMarathonChapter(chapterID) else 0

    def getChapterRemainingTime(self, chapterID):
        remainingTime = 0
        if self.isMarathonChapter(chapterID):
            remainingTime = max(0, self.getChapterExpiration(chapterID) - time_utils.getServerUTCTime())
        return remainingTime

    def isRareLevel(self, chapterID, level):
        realLevel = min(level, self.getMaxLevelInChapter(chapterID))
        tags = self.__getConfig().getTags(chapterID, realLevel, BattlePassConsts.REWARD_PAID)
        return BattlePassConsts.RARE_REWARD_TAG in tags

    def isFinalLevel(self, chapterID, level):
        return level >= self.getMaxLevelInChapter(chapterID)

    def getRewardLogic(self):
        return self.__rewardLogic

    def getSingleAward(self, chapterId, level, awardType=BattlePassConsts.REWARD_FREE, needSort=True):
        reward = {}
        if awardType in (BattlePassConsts.REWARD_FREE, BattlePassConsts.REWARD_PAID):
            reward = self.__getConfig().getRewardByType(chapterId, level, awardType)
        elif awardType == BattlePassConsts.REWARD_BOTH:
            rewards = [self.__getConfig().getFreeReward(chapterId, level), self.__getConfig().getPaidReward(chapterId, level)]
            return BattlePassAwardsManager.hideInvisible(BattlePassAwardsManager.composeBonuses(rewards))
        if needSort:
            rewards = BattlePassAwardsManager.composeBonuses([reward])
        else:
            rewards = awardsFactory(reward)
        return BattlePassAwardsManager.hideInvisible(rewards, needSplit=not needSort)

    def getAwardsInterval(self, chapterId, fromLevel, toLevel, awardType=BattlePassConsts.REWARD_FREE):
        result = {}
        for level in range(fromLevel, toLevel + 1):
            result[level] = self.getSingleAward(chapterId, level, awardType, True)

        return result

    def getPackedAwardsInterval(self, chapterId, fromLevel, toLevel, awardType=BattlePassConsts.REWARD_FREE):
        result = []
        for level in range(fromLevel, toLevel + 1):
            result.extend(self.getSingleAward(chapterId, level, awardType, False))

        return BattlePassAwardsManager.sortBonuses(result)

    def isNeedToTakeReward(self, chapterId, awardType, level):
        bonuses = self.getSingleAward(chapterId, level, awardType)
        if level > self.getLevelInChapter(chapterId):
            return False
        else:
            for bonus in bonuses:
                if bonus.getName() == BATTLE_PASS_SELECT_BONUS_NAME:
                    for tokenID in bonus.getTokens().iterkeys():
                        if self.__itemsCache.items.tokens.getToken(tokenID) is not None:
                            return True

            return False

    def replaceOfferByReward(self, bonuses):
        result = []
        for bonus in bonuses:
            if bonus.getName() == BATTLE_PASS_SELECT_BONUS_NAME:
                bonus.updateContext({'isReceived': False})
                hasGift = False
                for tokenID in bonus.getTokens().iterkeys():
                    offerToken = getOfferTokenByGift(tokenID)
                    offer = self.__offersProvider.getOfferByToken(offerToken)
                    if offer is not None:
                        receivedGifts = self.__offersProvider.getReceivedGifts(offer.id)
                        if receivedGifts:
                            for giftId, count in receivedGifts.iteritems():
                                if count > 0:
                                    gift = offer.getGift(giftId)
                                    if gift is not None:
                                        hasGift = True
                                        result.extend(gift.bonuses)

                if not hasGift:
                    result.append(bonus)
            result.append(bonus)

        return result

    def isChooseRewardEnabled(self, awardType, chapterId, level):
        if level > self.getLevelInChapter(chapterId):
            return False
        else:
            bonuses = self.getSingleAward(chapterId, level, awardType)
            for bonus in bonuses:
                if bonus.getName() == BATTLE_PASS_SELECT_BONUS_NAME:
                    for tokenID in bonus.getTokens().iterkeys():
                        if self.__itemsCache.items.tokens.getToken(tokenID) is not None:
                            return self.isOfferEnabled() and self.__offersProvider.getOfferByToken(getOfferTokenByGift(tokenID)) is not None

            return False

    def canChooseAnyReward(self):
        return self.isOfferEnabled() and any((token.startswith(BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS) for token in self.__itemsCache.items.tokens.getTokens().iterkeys() if self.__offersProvider.getOfferByToken(getOfferTokenByGift(token)) is not None))

    def getChapterIndex(self, chapterID):
        sortedChapterIDs = sorted(self.getChapterIDs())
        return sortedChapterIDs.index(chapterID)

    def getLevelsConfig(self, chapterID):
        return self.__getConfig().getChapterLevels(chapterID)

    def getPointsInChapter(self, chapterID):
        return self.__itemsCache.items.battlePass.getPointsByChapterID(chapterID)

    def getLevelInChapter(self, chapterID):
        return self.__itemsCache.items.battlePass.getCurrentLevelByChapterID(chapterID)

    def getCurrentLevel(self):
        return self.getLevelInChapter(self.getCurrentChapterID())

    def getCurrentChapterID(self):
        activeChapter = self.__itemsCache.items.battlePass.getActiveChapterID()
        if activeChapter not in self.getChapterIDs():
            activeChapter = 0
        return activeChapter

    def hasActiveChapter(self):
        return bool(self.getCurrentChapterID())

    @adisp_process
    def activateChapter(self, chapterID, seasonID=None):
        yield BattlePassActivateChapterProcessor(chapterID, seasonID or self.getSeasonID()).request()

    def getFreePoints(self):
        return self.__itemsCache.items.battlePass.getNonChapterPoints()

    def getState(self):
        return self.__itemsCache.items.battlePass.getState()

    def getSeasonsHistory(self):
        return {}

    def getLevelPoints(self, chapterID, level):
        levelsConfig = self.getLevelsConfig(chapterID)
        return levelsConfig[0] if level <= 0 else levelsConfig[level] - levelsConfig[level - 1]

    def getChapterState(self, chapterID):
        if self.getLevelInChapter(chapterID) >= self.getMaxLevelInChapter(chapterID):
            state = ChapterState.COMPLETED
        elif self.getCurrentChapterID() is not None and self.getCurrentChapterID() == chapterID:
            state = ChapterState.ACTIVE
        elif chapterID in self.__itemsCache.items.battlePass.getChapterStats():
            state = ChapterState.PAUSED
        elif self.isResourceChapter(chapterID) and not self.isCompleted():
            state = ChapterState.DISABLED
        else:
            state = ChapterState.NOT_STARTED
        return state

    def isChapterActive(self, chapterID):
        return self.getChapterState(chapterID) == ChapterState.ACTIVE

    def isChapterCompleted(self, chapterID):
        return self.getChapterState(chapterID) == ChapterState.COMPLETED

    def getFullChapterPoints(self, chapterID):
        levelsConfig = self.getLevelsConfig(chapterID)
        _, maxLevel = self.getChapterLevelInterval(chapterID)
        return levelsConfig[maxLevel - 1]

    def getLevelProgression(self, chapterID):
        if self.isDisabled():
            return (0, 0)
        if not chapterID:
            return (0, 0)
        level = self.getLevelInChapter(chapterID)
        points = self.getPointsInChapter(chapterID)
        return self.getProgressionByPoints(chapterID, points, level)

    def getLevelByPoints(self, chapterID, points):
        return self.getMaxLevelInChapter(chapterID) if points >= self.getLevelsConfig(chapterID)[-1] else bisect.bisect_right(self.getLevelsConfig(chapterID), points)

    def getProgressionByPoints(self, chapterID, points, level):
        levelsConfig = self.getLevelsConfig(chapterID)
        if level >= self.getMaxLevelInChapter(chapterID):
            points = levelsConfig[-1] - levelsConfig[-2]
            return (points, points)
        if level <= 0:
            basePoints = 0
            limitPoints = levelsConfig[0]
        else:
            basePoints = levelsConfig[level - 1]
            limitPoints = levelsConfig[level] - basePoints
        levelPoints = points - basePoints
        return (levelPoints, limitPoints)

    def getPerBattlePoints(self, gameMode=ARENA_BONUS_TYPE.REGULAR, vehCompDesc=None):
        winList = self.__getPackedBonusPointsList(vehTypeCompDescr=vehCompDesc, gameMode=gameMode)
        lostList = self.__getPackedBonusPointsList(vehTypeCompDescr=vehCompDesc, isWinner=False, gameMode=gameMode)
        count = 0
        result = []
        for winInfo, lostInfo in zip(winList, lostList):
            pointsWin, pointsCount = winInfo
            pointsLost, _ = lostInfo
            count += pointsCount
            if pointsWin > 0:
                item = TopPoints(count, pointsWin, pointsLost)
                result.append(item)

        return result

    def getPerBattleRoyalePoints(self, gameMode=ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, vehCompDesc=None):
        winList = self.__getConfig().bonusPointsList(vehCompDesc, isWinner=True, gameMode=gameMode)
        pointsList = list(self.__getConfig().bonusPointsList(vehCompDesc, isWinner=False, gameMode=gameMode))
        pointsList[0] = winList[0]
        pointList = [ (key, len(list(group))) for key, group in groupby(pointsList) ]
        count = 0
        result = []
        if not winList or not pointList:
            _logger.error('Failed to get bonus points information! Check server settings are correct for Battle Royale.')
            return result
        for item in pointList:
            points, pointsCount = item
            count += pointsCount
            if points > 0:
                result.append(BattleRoyaleTopPoints(count, points))

        return result

    def getChapterConfig(self):
        return [ self.getMaxLevelInChapter(chapter) for chapter in self.getChapterIDs() ]

    def getChapterLevelInterval(self, chapterID):
        return self.__getConfig().getChapterBorders(chapterID)

    def isSpecialVehicle(self, intCD):
        return self.__getConfig().isSpecialVehicle(intCD)

    def getSpecialVehicles(self):
        return self.__getConfig().getSpecialVehicles()

    def getPointsDiffForVehicle(self, intCD, gameMode=ARENA_BONUS_TYPE.REGULAR):
        defaultWinList = self.__getPackedBonusPointsList(gameMode=gameMode)
        diffWinList = self.__getPackedBonusPointsList(vehTypeCompDescr=intCD, isDiff=True, gameMode=gameMode)
        if not defaultWinList or not diffWinList:
            _logger.error('Failed to get bonus points information! Check server settings are correct.')
            return PointsDifference(0, 0, 0)
        diffBlock = diffWinList[0]
        bonus = diffBlock[0]
        top = diffBlock[1]
        textID = getPointsInfoStringID(gameMode)
        return PointsDifference(bonus, top, textID)

    def getVehicleProgression(self, intCD):
        points = self.__itemsCache.items.battlePass.getPointsForVehicle(intCD, 0)
        cap = self.__getConfig().vehicleCapacity(intCD)
        return (points, cap)

    def getSpecialVehicleCapBonus(self):
        return self.__getConfig().vehicleCapacity(first(self.getSpecialVehicles()))

    def getVehicleCapBonus(self, intCD):
        vehicle = self.__itemsCache.items.getItemByCD(intCD)
        return 0 if vehicle is None else self.__getConfig().capBonus(vehicle.level)

    def getSeasonTimeLeft(self):
        return max(0, self.getSeasonFinishTime() - time_utils.getServerUTCTime())

    def getFinalOfferTimeLeft(self):
        return max(0, self.getFinalOfferTime() - time_utils.getServerUTCTime())

    def getSeasonStartTime(self):
        return self.__getConfig().seasonStart

    def getSeasonFinishTime(self):
        return self.__getConfig().seasonFinish

    def hasMaxPointsOnVehicle(self, intCD):
        currentPoints, limitPoints = self.getVehicleProgression(intCD)
        return currentPoints >= limitPoints > 0

    def isProgressionOnVehiclePossible(self, intCD):
        return self.__getConfig().vehicleCapacity(intCD) > 0

    def getSeasonID(self):
        return self.__itemsCache.items.battlePass.getSeasonID()

    def getSeasonNum(self):
        return self.__getConfig().seasonNum

    def getCurrentCollectionId(self):
        return self.__getConfig().currentCollectionId

    def getFinalOfferTime(self):
        return self.__getConfig().finalOfferTime

    def getShopOfferFinishTimeLeft(self):
        return max(0, self.__getConfig().shopOfferFinishTime - time_utils.getServerUTCTime())

    def isShopOfferActive(self):
        return bool(self.getShopOfferFinishTimeLeft())

    def getStylesConfig(self):
        return {chapterID:chapterInfo.get('styleId') for chapterID, chapterInfo in self.__getConfig().chapters.iteritems()}

    def getNotChosenRewardCount(self):
        return sum((token.startswith(BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS) for token in self.__itemsCache.items.tokens.getTokens().iterkeys())) if not self.isOfferEnabled() else sum((token.startswith(BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS) for token in self.__itemsCache.items.tokens.getTokens().iterkeys() if self.__offersProvider.getOfferByToken(getOfferTokenByGift(token)) is not None))

    def hasAnyOfferGiftToken(self):
        return any((token.startswith(BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS) for token in self.__itemsCache.items.tokens.getTokens().iterkeys()))

    def takeRewardForLevel(self, chapterID, level):
        isBought = self.isBought(chapterID=chapterID)
        awardType = BattlePassConsts.REWARD_BOTH if isBought else BattlePassConsts.REWARD_FREE
        isOfferEnabled = self.isOfferEnabled()
        bonuses = self.getSingleAward(chapterID, level, awardType)
        rewardsToChoose = []
        stylesToChoose = []
        for bonus in bonuses:
            bonusName = bonus.getName()
            if bonusName == BATTLE_PASS_SELECT_BONUS_NAME and isOfferEnabled:
                for tokenID in bonus.getTokens().iterkeys():
                    if self.__itemsCache.items.tokens.getToken(tokenID) is not None and self.__offersProvider.getOfferByToken(getOfferTokenByGift(tokenID)) is not None:
                        rewardsToChoose.append(tokenID)

            if bonusName == BATTLE_PASS_STYLE_PROGRESS_BONUS_NAME:
                for tokenID in bonus.getTokens().iterkeys():
                    if self.__itemsCache.items.tokens.getToken(tokenID) is not None:
                        chapter = bonus.getChapter()
                        if chapter not in stylesToChoose:
                            stylesToChoose.append(chapter)

        rewardsToChoose.sort(key=lambda x: (int(x.split(':')[-1]), x.split(':')[-2]))
        self.getRewardLogic().startManualFlow(rewardsToChoose, chapterID, level)
        return

    def takeAllRewards(self):
        if self.isOfferEnabled():
            rewardsToChoose = [ token for token in self.__itemsCache.items.tokens.getTokens().iterkeys() if token.startswith(BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS) and self.__offersProvider.getOfferByToken(getOfferTokenByGift(token)) is not None ]
            rewardsToChoose.sort(key=lambda x: (int(x.split(':')[-1]), x.split(':')[-2]))
        else:
            rewardsToChoose = []
        self.getRewardLogic().startManualFlow(rewardsToChoose, 0)
        return

    def getChapterStyleProgress(self, chapter):
        return getMaxAvalable3DStyleProgressInChapter(self.getSeasonID(), chapter, self.__itemsCache.items.tokens.getTokens().keys())

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onConfigChanged),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onOffersStateChanged),
         (self.__itemsCache.onSyncCompleted, self.__onSyncCompleted),
         (self.__offersProvider.onOffersUpdated, self.__onOffersUpdated))

    def __stop(self):
        self.__seasonChangeNotifier.stopNotification()
        self.__marathonChapterNotifier.stopNotification()
        self._unsubscribe()

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().getBattlePassConfig()

    def __onTokensUpdate(self, diff, _):
        tokens = diff.get('tokens', {})
        if not tokens:
            return
        for chapter in self.getChapterIDs():
            if getBattlePassPassTokenName(self.getSeasonID(), chapter) in tokens:
                self.onBattlePassIsBought()
                break

        if any((tokenID.startswith(BATTLE_PASS_OFFER_TOKEN_PREFIX) for tokenID, token in tokens.iteritems())):
            self.onSelectTokenUpdated()

    def __getTimeUntilStart(self):
        return max(0, self.__getConfig().seasonStart - time_utils.getServerUTCTime())

    def __getTimeToNotifySeasonChanged(self):
        if not self.isPaused():
            if not self.isSeasonStarted():
                return self.__getTimeUntilStart()
            if not self.isSeasonFinished():
                return self.getSeasonTimeLeft()

    def __getTimeToMarathonChapterExpired(self):
        marathonChapterID = findFirst(self.isMarathonChapter, self.getChapterIDs(), 0)
        return max(0, self.getChapterExpiration(marathonChapterID) - time_utils.getServerUTCTime())

    def __onNotifySeasonChanged(self):
        self.onSeasonStateChanged()

    def __onNotifyMarathonChapterExpired(self):
        self.onMarathonChapterExpired()

    @serverSettingsChangeListener(BATTLE_PASS_CONFIG_NAME)
    def __onConfigChanged(self, diff):
        config = diff[BATTLE_PASS_CONFIG_NAME]
        isMarathonChapter = self.isMarathonChapter
        self.__seasonChangeNotifier.startNotification()
        chapters = config.get('season', {}).get('chapters', {})
        if any((isMarathonChapter(chapterID) for chapterID in chapters)):
            self.__marathonChapterNotifier.stopNotification()
            self.__marathonChapterNotifier = SimpleNotifier(self.__getTimeToMarathonChapterExpired, self.__onNotifyMarathonChapterExpired)
            self.__marathonChapterNotifier.startNotification()
        else:
            self.__marathonChapterNotifier.stopNotification()
        newMode = None
        oldMode = self.__currentMode
        if 'mode' in config:
            newMode = config['mode']
            self.__currentMode = newMode
        self.onBattlePassSettingsChange(newMode, oldMode)
        return

    @serverSettingsChangeListener(OFFERS_ENABLED_KEY)
    def __onOffersStateChanged(self, diff):
        self.__onOffersUpdated()

    def __onSyncCompleted(self, _, diff):
        if BATTLE_PASS_PDATA_KEY not in diff:
            return
        data = diff[BATTLE_PASS_PDATA_KEY]
        newPoints = data.get('sumPoints', self.__oldPoints)
        newLevel = data.get('level', self.__oldLevel)
        if newPoints != self.__oldPoints:
            self.onPointsUpdated()
        if newLevel != self.__oldLevel:
            self.onLevelUp()
        self.__oldPoints = newPoints
        self.__oldLevel = newLevel
        if 'chapterID' in data:
            self.onChapterChanged()

    def __onOffersUpdated(self):
        self.__validateOffers()
        self.onOffersUpdated()

    def __validateOffers(self):
        for offer in self.__offersProvider.iAvailableOffers(False):
            if not offer.token.startswith(BATTLE_PASS_OFFER_TOKEN_PREFIX):
                continue
            counts = {gift.giftCount for gift in offer.getAllGifts()}
            if len(counts) > 1:
                _logger.error('Wrong bonus count in gifts. Offer token %s', offer.token)

    @staticmethod
    def __bonusPointsDiffList(vehTypeCompDescr, config, gameMode):
        defaultPoints = config.points.get(gameMode, {})
        defaultDiff = [0] * len(defaultPoints.get('win', []))
        if vehTypeCompDescr in defaultPoints and 'win' in defaultPoints:
            specialPoints = defaultPoints[vehTypeCompDescr]
            defaultPoints = defaultPoints['win']
            specialPoints = specialPoints['win']
            return [ a - b for a, b in zip(specialPoints, defaultPoints) ]
        return defaultDiff

    def __getPackedBonusPointsList(self, vehTypeCompDescr=None, isWinner=True, isDiff=False, gameMode=ARENA_BONUS_TYPE.REGULAR):
        if isDiff:
            pointsList = self.__bonusPointsDiffList(vehTypeCompDescr, self.__getConfig(), gameMode)
        else:
            pointsList = self.__getConfig().bonusPointsList(vehTypeCompDescr, isWinner, gameMode)
        return [ (key, len(list(group))) for key, group in groupby(pointsList) ]

    @staticmethod
    def __checkIfRewardIsToken(bonusName, reward):
        if 'tokens' not in reward:
            return False
        bonuses = BattlePassAwardsManager.composeBonuses([reward])
        for bonus in bonuses:
            if bonus.getName() == bonusName:
                return True

        return False

    def __clearFields(self):
        self.__oldPoints = 0
        self.__oldLevel = 0
        self.__currentMode = None
        return
