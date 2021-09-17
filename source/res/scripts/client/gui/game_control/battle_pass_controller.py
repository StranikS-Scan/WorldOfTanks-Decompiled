# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/battle_pass_controller.py
import logging
from collections import namedtuple
from itertools import groupby
import typing
import constants
from Event import Event, EventManager
from battle_pass_common import BattlePassConsts, getBattlePassPassTokenName, getLevel, BATTLE_PASS_CONFIG_NAME, BattlePassConfig, BattlePassStatsCommon, BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER_2020, BATTLE_PASS_TOKEN_NEW_DEVICE_GIFT_OFFER_2020, BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS, BATTLE_PASS_SELECT_BONUS_NAME, BATTLE_PASS_STYLE_PROGRESS_BONUS_NAME, getMaxAvalable3DStyleProgressInChapter, BATTLE_PASS_OFFER_TOKEN_PREFIX
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.battle_pass.battle_pass_award import awardsFactory, BattlePassAwardsManager
from gui.battle_pass.battle_pass_helpers import getLevelProgression, getPointsInfoStringID, getOfferTokenByGift
from gui.battle_pass.state_machine.delegator import BattlePassRewardLogic
from gui.battle_pass.state_machine.machine import BattlePassStateMachine
from gui.battle_pass.non_selected_trophy_devices_notifier import NonSelectedOldTrophyDeviceNotifier
from gui.battle_pass.state_machine.state_machine_helpers import getStylesToChooseUntilChapter
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from shared_utils import first
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import TokensBonus, BattlePassStyleProgressTokenBonus
    from account_helpers.offers.events_data import OfferEventData, OfferGift
_logger = logging.getLogger(__name__)
TopPoints = namedtuple('TopPoints', ['label', 'winPoint', 'losePoint'])
BattleRoyaleTopPoints = namedtuple('BattleRoyaleTopPoints', ['label', 'points'])
PointsDifference = namedtuple('PointsDifference', ['bonus', 'top', 'textID'])

class BattlePassController(IBattlePassController):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self):
        self.__oldPoints = 0
        self.__oldLevel = 0
        self.__currentMode = None
        self.__eventsManager = EventManager()
        self.__seasonChangeNotifier = SimpleNotifier(self.__getTimeToNotifySeasonChange, self.__onNotifySeasonChange)
        self.onPointsUpdated = Event(self.__eventsManager)
        self.onLevelUp = Event(self.__eventsManager)
        self.onBattlePassIsBought = Event(self.__eventsManager)
        self.onSeasonStateChange = Event(self.__eventsManager)
        self.onBattlePassSettingsChange = Event(self.__eventsManager)
        self.onFinalRewardStateChange = Event(self.__eventsManager)
        self.onDeviceSelectChange = Event(self.__eventsManager)
        self.onOffersUpdated = Event(self.__eventsManager)
        self.onRewardSelectChange = Event(self.__eventsManager)
        self.__nonSelectedOldTrophyDeviceNotifier = NonSelectedOldTrophyDeviceNotifier(self)
        self.__rewardLogic = None
        return

    def init(self):
        super(BattlePassController, self).init()
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__rewardLogic = BattlePassRewardLogic(BattlePassStateMachine())
        BattlePassAwardsManager.init()

    def onLobbyInited(self, event):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.__offersProvider.onOffersUpdated += self.__onOffersUpdated
        self.__seasonChangeNotifier.startNotification()
        self.__rewardLogic.start()
        if self.__currentMode is None:
            self.__currentMode = self.__getConfig().mode
        else:
            self.onBattlePassSettingsChange(self.__getConfig().mode, self.__currentMode)
            self.__currentMode = self.__getConfig().mode
        self.__nonSelectedOldTrophyDeviceNotifier.start()
        return

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
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(BattlePassController, self).fini()

    def isBought(self, seasonID=None, chapter=None):
        if seasonID is None:
            seasonID = self.getSeasonID()
        if chapter is None:
            chapter = self.getCurrentChapter()
        tokenForAllBP = self.__itemsCache.items.tokens.getTokens().get(getBattlePassPassTokenName(seasonID, 0))
        if tokenForAllBP is not None:
            return True
        else:
            token = self.__itemsCache.items.tokens.getTokens().get(getBattlePassPassTokenName(seasonID, chapter))
            return token is not None

    def isOfferEnabled(self):
        return self.__lobbyContext.getServerSettings().isOffersEnabled()

    def isEnabled(self):
        return self.__getConfig().isEnabled()

    def isActive(self):
        return self.__getConfig().isActive(time_utils.getServerUTCTime())

    def isVisible(self):
        return self.isSeasonStarted() and not self.isDisabled() and not self.isSeasonFinished()

    def isOffSeasonEnable(self):
        return False

    def isDisabled(self):
        return not self.isActive() and not self.isPaused()

    def isPaused(self):
        return self.__getConfig().isPaused()

    def isSeasonStarted(self):
        return self.__getConfig().seasonStart <= time_utils.getServerUTCTime()

    def isSeasonFinished(self):
        return self.__getConfig().seasonFinish <= time_utils.getServerUTCTime()

    def isValidBattleType(self, prbEntity):
        return prbEntity.getQueueType() in (constants.QUEUE_TYPE.RANDOMS, constants.QUEUE_TYPE.MAPBOX)

    def isGameModeEnabled(self, arenaBonusType):
        return self.__getConfig().isGameModeEnabled(arenaBonusType)

    def getSupportedArenaBonusTypes(self):
        return [ arenaBonusType for arenaBonusType in self.__getConfig().points ]

    def getMaxLevel(self):
        return self.__getConfig().maxBaseLevel

    def isRareLevel(self, level):
        realLevel = min(level, self.getMaxLevel())
        tags = self.__getConfig().getTags(realLevel, BattlePassConsts.REWARD_PAID)
        return BattlePassConsts.RARE_REWARD_TAG in tags

    def isFinalLevel(self, level):
        realLevel = min(level, self.getMaxLevel())
        return realLevel in self.getChapterConfig()

    def getOldTrophySelectTokensCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER_2020)

    def getOldNewDeviceSelectTokensCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(BATTLE_PASS_TOKEN_NEW_DEVICE_GIFT_OFFER_2020)

    def getRewardLogic(self):
        return self.__rewardLogic

    def getSingleAward(self, level, awardType=BattlePassConsts.REWARD_FREE, needSort=True):
        reward = {}
        if awardType in (BattlePassConsts.REWARD_FREE, BattlePassConsts.REWARD_PAID):
            reward = self.__getConfig().getRewardByType(level, awardType)
        elif awardType == BattlePassConsts.REWARD_BOTH:
            rewards = [self.__getConfig().getFreeReward(level), self.__getConfig().getPaidReward(level)]
            return BattlePassAwardsManager.hideInvisible(BattlePassAwardsManager.composeBonuses(rewards))
        if needSort:
            rewards = BattlePassAwardsManager.composeBonuses([reward])
        else:
            rewards = awardsFactory(reward)
        return BattlePassAwardsManager.hideInvisible(rewards, needSplit=not needSort)

    def getAwardsInterval(self, fromLevel, toLevel, awardType=BattlePassConsts.REWARD_FREE):
        result = {}
        for level in range(fromLevel, toLevel + 1):
            result[level] = self.getSingleAward(level, awardType, True)

        return result

    def getPackedAwardsInterval(self, fromLevel, toLevel, awardType=BattlePassConsts.REWARD_FREE):
        result = []
        for level in range(fromLevel, toLevel + 1):
            result.extend(self.getSingleAward(level, awardType, False))

        return BattlePassAwardsManager.sortBonuses(result)

    def isNeedToTakeReward(self, awardType, level):
        bonuses = self.getSingleAward(level, awardType)
        if level > self.getCurrentLevel():
            return False
        else:
            for bonus in bonuses:
                if bonus.getName() in (BATTLE_PASS_SELECT_BONUS_NAME, BATTLE_PASS_STYLE_PROGRESS_BONUS_NAME):
                    for tokenID in bonus.getTokens().iterkeys():
                        if self.__itemsCache.items.tokens.getToken(tokenID) is not None:
                            return True

            return False

    def replaceOfferByReward(self, bonuses):
        result = []
        for bonus in bonuses:
            if bonus.getName() == BATTLE_PASS_SELECT_BONUS_NAME:
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

    def isChooseRewardEnabled(self, awardType, level):
        if level > self.getCurrentLevel():
            return False
        else:
            bonuses = self.getSingleAward(level, awardType)
            for bonus in bonuses:
                if bonus.getName() == BATTLE_PASS_STYLE_PROGRESS_BONUS_NAME:
                    return True
                if bonus.getName() == BATTLE_PASS_SELECT_BONUS_NAME:
                    for tokenID in bonus.getTokens().iterkeys():
                        if self.__itemsCache.items.tokens.getToken(tokenID) is not None:
                            return self.isOfferEnabled() and self.__offersProvider.getOfferByToken(getOfferTokenByGift(tokenID)) is not None

            return False

    def canChooseAnyReward(self):
        return False if not self.isOfferEnabled() else any((token.startswith(BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS) for token in self.__itemsCache.items.tokens.getTokens().iterkeys() if self.__offersProvider.getOfferByToken(getOfferTokenByGift(token)) is not None))

    def getLevelsConfig(self):
        return self.__getConfig().basePoints

    def getFinalRewards(self):
        return {}

    def getFreeFinalRewardDict(self):
        return self.__getConfig().getRewardByType(self.getMaxLevel(), BattlePassConsts.REWARD_FREE)

    def getCurrentPoints(self):
        return self.__itemsCache.items.battlePass.getPoints()

    def getMaxPoints(self):
        return self.__getConfig().maxBasePoints

    def getCurrentLevel(self):
        return self.__itemsCache.items.battlePass.getCurrentLevel()

    def getCurrentChapter(self):
        return self.__getConfig().getChapter(self.getCurrentLevel())

    def getChapterByLevel(self, level):
        return self.__getConfig().getChapter(level)

    def getState(self):
        return self.__itemsCache.items.battlePass.getState()

    def getPrevSeasonsStats(self):
        packedStats = self.__itemsCache.items.battlePass.getPackedStats()
        if not packedStats:
            return None
        else:
            unpackStats, _ = BattlePassStatsCommon.unpackAllSeasonStats(packedStats)
            return unpackStats

    def getLastFinishedSeasonStats(self):
        allSeasonStats = self.getPrevSeasonsStats()
        if not allSeasonStats:
            seasons = sorted(self.getSeasonsHistory().keys(), reverse=True)
            return BattlePassStatsCommon.makeSeasonStats(first(seasons), {}, BattlePassStatsCommon.initialSeasonStatsData())
        return allSeasonStats[-1]

    def getSeasonsHistory(self):
        return self.__getConfig().seasonsHistory

    def getLevelPoints(self, level):
        levelsConfig = self.getLevelsConfig()
        return levelsConfig[0] if level <= 0 else levelsConfig[level] - levelsConfig[level - 1]

    def getFullChapterPoints(self, chapter, includeCurrent):
        levelsConfig = self.getLevelsConfig()
        minLevel, maxLevel = self.getChapterLevelInterval(chapter)
        if minLevel == maxLevel == 0:
            return 0
        if includeCurrent:
            return levelsConfig[maxLevel - 1]
        return 0 if minLevel <= 1 else levelsConfig[minLevel - 2]

    def getLevelProgression(self):
        if self.isDisabled():
            return (0, 0)
        level = self.getCurrentLevel()
        if level >= self.getMaxLevel():
            levelsConfig = self.getLevelsConfig()
            points = levelsConfig[-1] - levelsConfig[-2]
            return (points, points)
        points = self.getCurrentPoints()
        levelsConfig = self.getLevelsConfig()
        return getLevelProgression(level, points, levelsConfig)

    def getLevelByPoints(self, points):
        if points >= self.getMaxPoints():
            level = self.getMaxLevel()
        else:
            levelsConfig = self.getLevelsConfig()
            level = getLevel(curPoints=points, levelPoints=levelsConfig)
        chapter = self.__getConfig().getChapter(level)
        return (chapter, level)

    def getProgressionByPoints(self, points, level):
        levelsConfig = self.getLevelsConfig()
        if level >= self.getMaxLevel():
            levelPoints = fullLevelPoints = levelsConfig[-1] - levelsConfig[-2]
        else:
            levelPoints, fullLevelPoints = getLevelProgression(level, points, levelsConfig)
        return (levelPoints, fullLevelPoints)

    def getPerBattlePoints(self, gameMode=constants.ARENA_BONUS_TYPE.REGULAR, vehCompDesc=None):
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

    def getPerBattleRoyalePoints(self, gameMode=constants.ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, vehCompDesc=None):
        winList = self.__getPackedBonusPointsList(vehTypeCompDescr=vehCompDesc, gameMode=gameMode)
        pointList = self.__getPackedBonusPointsList(vehTypeCompDescr=vehCompDesc, isWinner=False, gameMode=gameMode)
        count = 0
        result = []
        if not winList or not pointList:
            _logger.error('Failed to get bonus points information! Check server settings are correct for Battle Royale.')
            return result
        pointList[0] = winList[0]
        for item in pointList:
            points, pointsCount = item
            count += pointsCount
            if points > 0:
                result.append(BattleRoyaleTopPoints(count, points))

        return result

    def getChapterConfig(self):
        return self.__getConfig().finalLevelsInChapter

    def getChapterLevelInterval(self, chapter):
        chapterConfig = self.getChapterConfig()
        if chapter < BattlePassConsts.MINIMAL_CHAPTER_NUMBER or chapter > len(chapterConfig):
            return (0, 0)
        fromLevel = 1 if chapter == BattlePassConsts.MINIMAL_CHAPTER_NUMBER else chapterConfig[chapter - 2] + 1
        toLevel = chapterConfig[chapter - 1]
        return (fromLevel, toLevel)

    def isSpecialVehicle(self, intCD):
        return self.__getConfig().isSpecialVehicle(intCD)

    def getSpecialVehicles(self):
        return self.__getConfig().getSpecialVehicles()

    def getPointsDiffForVehicle(self, intCD, gameMode=constants.ARENA_BONUS_TYPE.REGULAR):
        defaultWinList = self.__getPackedBonusPointsList(gameMode=gameMode)
        diffWinList = self.__getPackedBonusPointsList(vehTypeCompDescr=intCD, isDiff=True, gameMode=gameMode)
        if not defaultWinList or not diffWinList:
            _logger.error('Failed to get bonus points information! Check server settings are correct.')
            return PointsDifference(0, 0, 0)
        diffBlock = diffWinList[0]
        bonus = diffBlock[0]
        top = diffBlock[1]
        textID = getPointsInfoStringID()
        return PointsDifference(bonus, top, textID)

    def getVehicleProgression(self, intCD):
        points = self.__itemsCache.items.battlePass.getPointsForVehicle(intCD, 0)
        cap = self.__getConfig().vehicleCapacity(intCD)
        return (points, cap)

    def getVehicleCapBonus(self, intCD):
        vehicle = self.__itemsCache.items.getItemByCD(intCD)
        if vehicle is None:
            return 0
        else:
            bonus = self.__getConfig().capBonus(vehicle.level)
            return bonus

    def getCapacityList(self):
        capacities = self.__getConfig().capacityList()
        return enumerate(capacities, 1)

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
        cap = self.__getConfig().vehicleCapacity(intCD)
        return cap > 0

    def getSeasonID(self):
        return self.__itemsCache.items.battlePass.getSeasonID()

    def getSeasonNum(self):
        return self.__getConfig().seasonNum

    def getFinalOfferTime(self):
        return self.__getConfig().finalOfferTime

    def getStylesConfig(self):
        rewards = self.__getConfig().selectedReward
        return BattlePassAwardsManager.composeBonuses([rewards]) if rewards else BattlePassAwardsManager.composeBonuses([])

    def getNotChosenRewardCount(self):
        return sum((token.startswith(BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS) for token in self.__itemsCache.items.tokens.getTokens().iterkeys() if self.__offersProvider.getOfferByToken(getOfferTokenByGift(token)) is not None))

    def hasAnyOfferGiftToken(self):
        return any((token.startswith(BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS) for token in self.__itemsCache.items.tokens.getTokens().iterkeys()))

    def takeRewardForLevel(self, level):
        chapter = self.getChapterByLevel(level - 1)
        isBought = self.isBought(chapter=chapter)
        awardType = BattlePassConsts.REWARD_BOTH if isBought else BattlePassConsts.REWARD_FREE
        isOfferEnabled = self.isOfferEnabled()
        bonuses = self.getSingleAward(level, awardType)
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
        self.getRewardLogic().startManualFlow(rewardsToChoose, stylesToChoose)
        return

    def takeAllRewards(self):
        if self.isOfferEnabled():
            rewardsToChoose = [ token for token in self.__itemsCache.items.tokens.getTokens().iterkeys() if token.startswith(BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS) and self.__offersProvider.getOfferByToken(getOfferTokenByGift(token)) is not None ]
            rewardsToChoose.sort(key=lambda x: (int(x.split(':')[-1]), x.split(':')[-2]))
        else:
            rewardsToChoose = []
        chapter = self.getCurrentChapter()
        stylesToChoose = getStylesToChooseUntilChapter(chapter + 1)
        self.getRewardLogic().startManualFlow(rewardsToChoose, stylesToChoose)
        return

    def getChapterStyleProgress(self, chapter):
        return getMaxAvalable3DStyleProgressInChapter(self.getSeasonID(), chapter, self.__itemsCache.items.tokens.getTokens().keys())

    def __stop(self):
        self.__seasonChangeNotifier.stopNotification()
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__offersProvider.onOffersUpdated -= self.__onOffersUpdated
        self.__nonSelectedOldTrophyDeviceNotifier.stop()

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().getBattlePassConfig()

    def __onTokensUpdate(self, diff):
        for chapter, _ in enumerate(self.getChapterConfig(), BattlePassConsts.MINIMAL_CHAPTER_NUMBER):
            if getBattlePassPassTokenName(self.getSeasonID(), chapter) in diff:
                self.onBattlePassIsBought()
                break

        if BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER_2020 in diff or BATTLE_PASS_TOKEN_NEW_DEVICE_GIFT_OFFER_2020 in diff:
            self.onDeviceSelectChange()

    def __getTimeUntilStart(self):
        return max(0, self.__getConfig().seasonStart - time_utils.getServerUTCTime())

    def __getTimeToNotifySeasonChange(self):
        if not self.isPaused():
            if not self.isSeasonStarted():
                return self.__getTimeUntilStart()
            if not self.isSeasonFinished():
                return self.getSeasonTimeLeft()

    def __onNotifySeasonChange(self):
        self.onSeasonStateChange()

    def __onServerSettingsChange(self, diff):
        if BATTLE_PASS_CONFIG_NAME in diff:
            self.__seasonChangeNotifier.startNotification()
            newMode = None
            oldMode = self.__currentMode
            if 'mode' in diff[BATTLE_PASS_CONFIG_NAME]:
                newMode = diff[BATTLE_PASS_CONFIG_NAME]['mode']
                self.__currentMode = newMode
            self.onBattlePassSettingsChange(newMode, oldMode)
        if 'isOffersEnabled' in diff:
            self.__onOffersUpdated()
            self.onDeviceSelectChange()
        return

    def __onSyncCompleted(self, _, diff):
        if 'battlePass' in diff:
            newPoints = diff['battlePass'].get('sumPoints', self.__oldPoints)
            newLevel = diff['battlePass'].get('level', self.__oldLevel)
            if newPoints != self.__oldPoints:
                self.onPointsUpdated()
            if newLevel != self.__oldLevel:
                self.onLevelUp()
            self.__oldPoints = newPoints
            self.__oldLevel = newLevel

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

    def __getPackedBonusPointsList(self, vehTypeCompDescr=None, isWinner=True, isDiff=False, gameMode=constants.ARENA_BONUS_TYPE.REGULAR):
        if isDiff:
            pointsList = self.__bonusPointsDiffList(vehTypeCompDescr=vehTypeCompDescr, config=self.__getConfig(), gameMode=gameMode)
        else:
            pointsList = self.__getConfig().bonusPointsList(vehTypeCompDescr=vehTypeCompDescr, isWinner=isWinner, gameMode=gameMode)
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
