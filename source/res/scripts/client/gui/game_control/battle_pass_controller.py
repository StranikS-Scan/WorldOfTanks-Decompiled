# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/battle_pass_controller.py
import logging
from collections import namedtuple
from itertools import groupby
from operator import itemgetter
import typing
import constants
from Event import Event, EventManager
from battle_pass_common import BattlePassConsts, BattlePassState, getBattlePassPassTokenName, getBattlePassOnboardingGiftToken, getLevel, BATTLE_PASS_CONFIG_NAME, BattlePassConfig, BattlePassStatsCommon, BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER, BATTLE_PASS_TOKEN_NEW_DEVICE_GIFT_OFFER, getBattlePassOnboardingToken
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.battle_pass.battle_pass_award import awardsFactory, BattlePassAwardsManager
from gui.battle_pass.battle_pass_bonuses_helper import TROPHY_GIFT_TOKEN_BONUS_NAME, NEW_DEVICE_GIFT_TOKEN_BONUS_NAME, DeviceTokensContainer
from gui.battle_pass.battle_pass_helpers import getLevelProgression, getPointsInfoStringID
from gui.battle_pass.state_machine.delegator import FinalRewardLogic
from gui.battle_pass.state_machine.machine import FinalRewardStateMachine
from gui.battle_pass.undefined_bonuses import makeUndefinedBonus
from gui.battle_pass.voting_requester import BattlePassVotingRequester
from gui.battle_pass.non_selected_trophy_devices_notifier import NonSelectedTrophyDeviceNotifier
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from items import vehicles
from shared_utils import findFirst, first
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import DossierBonus
_logger = logging.getLogger(__name__)
TopPoints = namedtuple('TopPoints', ['label', 'winPoint', 'losePoint'])
PointsDifference = namedtuple('PointsDifference', ['bonus', 'top', 'textID'])

class BattlePassController(IBattlePassController):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self):
        self.__oldPoints = 0
        self.__oldLevel = 0
        self.__oldVoteOption = 0
        self.__badge = None
        self.__currentMode = None
        self.__deviceGiftTokensContainers = {TROPHY_GIFT_TOKEN_BONUS_NAME: DeviceTokensContainer(self, TROPHY_GIFT_TOKEN_BONUS_NAME),
         NEW_DEVICE_GIFT_TOKEN_BONUS_NAME: DeviceTokensContainer(self, NEW_DEVICE_GIFT_TOKEN_BONUS_NAME)}
        self.__eventsManager = EventManager()
        self.__seasonChangeNotifier = SimpleNotifier(self.__getTimeToNotifySeasonChange, self.__onNotifySeasonChange)
        self.__purchaseUnlockNotifier = SimpleNotifier(self.__getTimeToNotifyPurchaseUnlock, self.__onNotifyUnlock)
        self.onPointsUpdated = Event(self.__eventsManager)
        self.onLevelUp = Event(self.__eventsManager)
        self.onVoted = Event(self.__eventsManager)
        self.onBattlePassIsBought = Event(self.__eventsManager)
        self.onSeasonStateChange = Event(self.__eventsManager)
        self.onUnlimitedPurchaseUnlocked = Event(self.__eventsManager)
        self.onBattlePassSettingsChange = Event(self.__eventsManager)
        self.onFinalRewardStateChange = Event(self.__eventsManager)
        self.onOnboardingChange = Event(self.__eventsManager)
        self.onDeviceSelectChange = Event(self.__eventsManager)
        self.__votingRequester = BattlePassVotingRequester(self)
        self.__nonSelectedTrophyDeviceNotifier = NonSelectedTrophyDeviceNotifier(self)
        self.__finalRewardLogic = None
        self.__onboardingVehicles = None
        return

    def init(self):
        super(BattlePassController, self).init()
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__finalRewardLogic = FinalRewardLogic(self, FinalRewardStateMachine())
        BattlePassAwardsManager.init()

    def onLobbyInited(self, event):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.__seasonChangeNotifier.startNotification()
        self.__purchaseUnlockNotifier.startNotification()
        self.__finalRewardLogic.start()
        if self.__currentMode is None:
            self.__currentMode = self.__getConfig().mode
        else:
            self.onBattlePassSettingsChange(self.__getConfig().mode, self.__currentMode)
            self.__currentMode = self.__getConfig().mode
        self.__votingRequester.start()
        self.__nonSelectedTrophyDeviceNotifier.start()
        return

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()
        self.__clearFields()
        self.__finalRewardLogic.stop()

    def fini(self):
        self.__stop()
        self.__finalRewardLogic.stop()
        self.__clearFields()
        self.__eventsManager.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(BattlePassController, self).fini()

    def isBought(self, seasonID=None):
        if seasonID is None:
            seasonID = self.getSeasonID()
        token = self.__itemsCache.items.tokens.getTokens().get(getBattlePassPassTokenName(seasonID))
        return token is not None

    def isOnboardingActive(self):
        if not self.__isOnboardingEnabled():
            return False
        else:
            onboardingGiftToken = self.__itemsCache.items.tokens.getTokens().get(getBattlePassOnboardingGiftToken(self.getSeasonID()))
            return onboardingGiftToken is not None

    def isChooseDeviceEnabled(self):
        return self.__lobbyContext.getServerSettings().isOffersEnabled()

    def isEnabled(self):
        return self.__getConfig().isEnabled()

    def isActive(self):
        return self.__getConfig().isActive(time_utils.getServerUTCTime())

    def isVisible(self):
        return self.isSeasonStarted() and not self.isDisabled() and not self.isSeasonFinished()

    def isOffSeasonEnable(self):
        return (not self.isSeasonStarted() or self.isSeasonFinished()) and not self.isDisabled()

    def isDisabled(self):
        return self.__getConfig().isDisabled()

    def isPaused(self):
        return self.__getConfig().isPaused()

    def isPlayerVoted(self):
        return self.getVoteOption() != 0

    def isSeasonStarted(self):
        return self.__getConfig().seasonStart <= time_utils.getServerUTCTime()

    def isSeasonFinished(self):
        return self.__getConfig().seasonFinish <= time_utils.getServerUTCTime()

    def isSellAnyLevelsUnlocked(self):
        return self.__getConfig().isSellAnyUnlocked(time_utils.getServerUTCTime())

    def isValidBattleType(self, prbEntity):
        return prbEntity.getEntityType() == constants.ARENA_GUI_TYPE.RANDOM

    def getMaxLevel(self, isBase=True):
        return len(self.getLevelsConfig(isBase))

    def isRareLevel(self, level, isBase=True):
        realLevel = min(level, self.getMaxLevel(isBase))
        rewardType = BattlePassConsts.REWARD_PAID if isBase else BattlePassConsts.REWARD_POST
        tags = self.__getConfig().getTags(realLevel, rewardType)
        return BattlePassConsts.RARE_REWARD_TAG in tags

    def getTrophySelectTokensCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER)

    def getNewDeviceSelectTokensCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(BATTLE_PASS_TOKEN_NEW_DEVICE_GIFT_OFFER)

    def getVotingRequester(self):
        return self.__votingRequester

    def getFinalRewardLogic(self):
        return self.__finalRewardLogic

    def getSplitFinalAwards(self):
        freeReward = []
        paidReward = []
        awardsSettings = sorted(self.getFinalRewards().iteritems(), key=itemgetter(0))
        voteOption = self.getVoteOption()
        if voteOption != 0:
            for vote, config in awardsSettings:
                shared = BattlePassAwardsManager.composeBonuses([config.get('shared', {})])
                if vote == voteOption:
                    unique = BattlePassAwardsManager.composeBonuses([config.get('unique', {})])
                    freeReward.extend(shared)
                    freeReward.extend(unique)
                paidReward.extend(shared)

        else:
            configs = [ config for _, config in awardsSettings ]
            if len(configs) != 2:
                return (freeReward, paidReward)
            sharedA = BattlePassAwardsManager.composeBonuses([configs[0].get('shared', {})])
            sharedB = BattlePassAwardsManager.composeBonuses([configs[1].get('shared', {})])
            uniqueA = BattlePassAwardsManager.composeBonuses([configs[0].get('unique', {})])
            uniqueB = BattlePassAwardsManager.composeBonuses([configs[1].get('unique', {})])
            for optionA, optionB in zip(sharedA, sharedB):
                bonus = makeUndefinedBonus(optionA, optionB)
                freeReward.append(bonus)
                paidReward.append(bonus)

        for optionA, optionB in zip(uniqueA, uniqueB):
            bonus = makeUndefinedBonus(optionA, optionB)
            freeReward.append(bonus)

        return (freeReward, paidReward)

    def getFinalAwardsForPurchaseLevels(self):
        awards = []
        awardsSettings = sorted(self.getFinalRewards().iteritems(), key=itemgetter(0))
        configs = [ config for _, config in awardsSettings ]
        if len(configs) != 2:
            return awards
        awards.extend(BattlePassAwardsManager.composeBonuses([configs[0].get('shared', {})]))
        awards.extend(BattlePassAwardsManager.composeBonuses([configs[1].get('shared', {})]))
        uniqueA = BattlePassAwardsManager.composeBonuses([configs[0].get('unique', {})])
        uniqueB = BattlePassAwardsManager.composeBonuses([configs[1].get('unique', {})])
        for optionA, optionB in zip(uniqueA, uniqueB):
            bonus = makeUndefinedBonus(optionA, optionB)
            awards.append(bonus)

        return awards

    def getSingleAward(self, level, awardType=BattlePassConsts.REWARD_FREE, needSort=True):
        reward = {}
        if awardType in (BattlePassConsts.REWARD_FREE, BattlePassConsts.REWARD_PAID, BattlePassConsts.REWARD_POST):
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

    def getAwardsList(self, awardType=BattlePassConsts.REWARD_FREE):
        maxLevel = self.getMaxLevel(False if awardType == BattlePassConsts.REWARD_POST else True)
        return self.getAwardsInterval(1, maxLevel, awardType)

    def getPackedAwardsInterval(self, fromLevel, toLevel, awardType=BattlePassConsts.REWARD_FREE):
        result = []
        for level in range(fromLevel, toLevel + 1):
            result.extend(self.getSingleAward(level, awardType, False))

        return BattlePassAwardsManager.sortBonuses(result)

    def getLevelsConfig(self, isBase=True):
        return self.__getConfig().basePoints if isBase else self.__getConfig().postPoints

    def getFinalRewards(self):
        return self.__getConfig().finalReward

    def getFreeFinalRewardDict(self):
        return self.__getConfig().getRewardByType(self.getMaxLevel(), BattlePassConsts.REWARD_FREE)

    def getCurrentPoints(self, aligned=False):
        points = self.__itemsCache.items.battlePass.getPoints()
        return self.__getConfig().alignedPointsFromSumPoints(points) if aligned else points

    def getMaxPoints(self, isBase=True):
        return self.__getConfig().maxBasePoints if isBase else self.__getConfig().maxPostPoints

    def getCurrentLevel(self):
        return self.__itemsCache.items.battlePass.getCurrentLevel()

    def getState(self):
        return self.__itemsCache.items.battlePass.getState()

    def getMaxSoldLevelsBeforeUnlock(self):
        return self.__getConfig().maxSoldLevelsBeforeUnlock

    def getBoughtLevels(self):
        return self.__itemsCache.items.battlePass.getBoughtLevels()

    def getVoteOption(self):
        return self.__itemsCache.items.battlePass.getVoteOption()

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

    def getAlternativeVoteOption(self):
        voteOption = self.getVoteOption()
        if voteOption == 0:
            return 0
        voteOptions = self.getFinalRewards().keys()
        alternativeOption = findFirst(lambda option: option != voteOption, voteOptions, 0)
        return alternativeOption

    def getLevelPoints(self, level, isBase=True):
        levelsConfig = self.getLevelsConfig(isBase)
        return levelsConfig[0] if level <= 0 else levelsConfig[level] - levelsConfig[level - 1]

    def getLevelProgression(self):
        if self.isDisabled():
            return (0, 0)
        state = self.getState()
        if state == BattlePassState.COMPLETED:
            levelsConfig = self.getLevelsConfig(False)
            points = levelsConfig[-1] - levelsConfig[-2]
            return (points, points)
        level = self.getCurrentLevel()
        points = self.getCurrentPoints(aligned=True)
        levelsConfig = self.getLevelsConfig(state == BattlePassState.BASE)
        return getLevelProgression(level, points, levelsConfig)

    def getLevelByPoints(self, points):
        if points >= self.__getConfig().maxPostPoints + self.__getConfig().maxBasePoints:
            state = BattlePassState.COMPLETED
        elif points >= self.__getConfig().maxBasePoints:
            state = BattlePassState.POST
        else:
            state = BattlePassState.BASE
        if state == BattlePassState.COMPLETED:
            level = self.getMaxLevel(isBase=False)
        else:
            alignedPoints = points - self.__getConfig().maxBasePoints if state == BattlePassState.POST else points
            levelsConfig = self.getLevelsConfig(isBase=state == BattlePassState.BASE)
            level = getLevel(curPoints=alignedPoints, levelPoints=levelsConfig)
        return (state, level)

    def getProgressionByPoints(self, points, state, level):
        if state == BattlePassState.COMPLETED:
            levelsConfig = self.getLevelsConfig(isBase=False)
            levelPoints = fullLevelPoints = levelsConfig[-1] - levelsConfig[-2]
        else:
            alignedPoints = points - self.__getConfig().maxBasePoints if state == BattlePassState.POST else points
            levelsConfig = self.getLevelsConfig(isBase=state == BattlePassState.BASE)
            levelPoints, fullLevelPoints = getLevelProgression(level, alignedPoints, levelsConfig)
        return (levelPoints, fullLevelPoints)

    def getPerBattlePoints(self, vehCompDesc=None):
        winList = self.__getPackedBonusPointsList(vehTypeCompDescr=vehCompDesc)
        lostList = self.__getPackedBonusPointsList(vehTypeCompDescr=vehCompDesc, isWinner=False)
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

    def getBadgeData(self):
        if self.__badge is None:
            self.__extractBadgeInfo()
        return self.__badge

    def isSpecialVehicle(self, intCD):
        return self.__getConfig().isSpecialVehicle(intCD)

    def getSpecialVehicles(self):
        return self.__getConfig().getSpecialVehicles()

    def getPointsDiffForVehicle(self, intCD):
        defaultWinList = self.__getPackedBonusPointsList()
        diffWinList = self.__getPackedBonusPointsList(vehTypeCompDescr=intCD, isDiff=True)
        if not defaultWinList or not diffWinList:
            _logger.error('Failed to get bonus points information! Check server settings are correct.')
            return PointsDifference(0, 0, 0)
        defaultBlock = defaultWinList[-1]
        diffBlock = diffWinList[0]
        bonus = diffBlock[0]
        top = 0 if diffBlock[1] == BattlePassConfig.MAX_RANKS - defaultBlock[1] else diffBlock[1]
        textID = getPointsInfoStringID(top != 0)
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

    def getSellAnyLevelsUnlockTimeLeft(self):
        return max(0, self.getSellAnyLevelsUnlockTime() - time_utils.getServerUTCTime())

    def getFinalOfferTimeLeft(self):
        return max(0, self.getFinalOfferTime() - time_utils.getServerUTCTime())

    def getSeasonStartTime(self):
        return self.__getConfig().seasonStart

    def getSeasonFinishTime(self):
        return self.__getConfig().seasonFinish

    def getSellAnyLevelsUnlockTime(self):
        return self.__getConfig().sellAnyLevelsUnlockTime

    def hasMaxPointsOnVehicle(self, intCD):
        currentPoints, limitPoints = self.getVehicleProgression(intCD)
        return currentPoints >= limitPoints > 0

    def isProgressionOnVehiclePossible(self, intCD):
        cap = self.__getConfig().vehicleCapacity(intCD)
        return cap > 0

    def isPlayerNewcomer(self):
        if not self.__isOnboardingEnabled():
            return False
        if self.isBought():
            return False
        config = self.__getConfig()
        if self.getCurrentPoints() >= config.maxPointsForNewbie:
            return False
        allVehicles = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
        totalCap = 0
        newbiePoints = config.maxPointsForNewbie
        for vehicle in allVehicles.itervalues():
            intCD = vehicle.intCD
            if vehicle.isRented and (vehicle.rentalIsOver or intCD in self.__getOnboardingVehicles()):
                continue
            totalCap += config.vehicleContribution(vehicle.intCD)
            if totalCap >= newbiePoints:
                return False

        return True

    def canPlayerParticipate(self):
        criteria = REQ_CRITERIA.INVENTORY
        criteria |= ~REQ_CRITERIA.VEHICLE.EPIC_BATTLE
        criteria |= REQ_CRITERIA.CUSTOM(lambda veh: not self.hasMaxPointsOnVehicle(veh.intCD))
        criteria |= REQ_CRITERIA.CUSTOM(lambda veh: self.isProgressionOnVehiclePossible(veh.intCD))
        availableVehiclesToProgression = self.__itemsCache.items.getVehicles(criteria)
        return len(availableVehiclesToProgression) > 0

    def getSeasonID(self):
        return self.__itemsCache.items.battlePass.getSeasonID()

    def getFinalOfferTime(self):
        return self.__getConfig().finalOfferTime

    def getDeviceTokensContainer(self, bonusName):
        if self.__deviceGiftTokensContainers[bonusName].isEmpty:
            self.__extractTrophySelectTokensInfo()
        return self.__deviceGiftTokensContainers[bonusName]

    def getMaxLevelForNewbie(self):
        return self.__getConfig().maxLevelForNewbie

    def __stop(self):
        self.__seasonChangeNotifier.stopNotification()
        self.__purchaseUnlockNotifier.stopNotification()
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__votingRequester.stop()
        self.__nonSelectedTrophyDeviceNotifier.stop()

    def __getFrontierStep(self):
        return self.__getConfig().postPoints

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().getBattlePassConfig()

    def __onTokensUpdate(self, diff):
        if getBattlePassPassTokenName(self.getSeasonID()) in diff:
            self.onBattlePassIsBought()
        if getBattlePassOnboardingGiftToken(self.getSeasonID()) in diff:
            self.onOnboardingChange()
        if BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER in diff or BATTLE_PASS_TOKEN_NEW_DEVICE_GIFT_OFFER in diff:
            self.onDeviceSelectChange()

    def __getTimeUntilStart(self):
        return max(0, self.__getConfig().seasonStart - time_utils.getServerUTCTime())

    def __getTimeToNotifySeasonChange(self):
        if not self.isDisabled():
            if not self.isSeasonStarted():
                return self.__getTimeUntilStart()
            if not self.isSeasonFinished():
                return self.getSeasonTimeLeft()

    def __onNotifySeasonChange(self):
        self.onSeasonStateChange()

    def __getTimeToNotifyPurchaseUnlock(self):
        return self.getSellAnyLevelsUnlockTimeLeft() if not self.isDisabled() else 0

    def __onNotifyUnlock(self):
        self.onUnlimitedPurchaseUnlocked()

    def __onServerSettingsChange(self, diff):
        if BATTLE_PASS_CONFIG_NAME in diff:
            self.__seasonChangeNotifier.startNotification()
            self.__purchaseUnlockNotifier.startNotification()
            self.__votingRequester.start()
            newMode = None
            oldMode = self.__currentMode
            if 'mode' in diff[BATTLE_PASS_CONFIG_NAME]:
                newMode = diff[BATTLE_PASS_CONFIG_NAME]['mode']
                self.__currentMode = newMode
            self.__extractBadgeInfo()
            self.__extractTrophySelectTokensInfo()
            self.onBattlePassSettingsChange(newMode, oldMode)
        if 'isOffersEnabled' in diff:
            self.onOnboardingChange()
            self.__onboardingVehicles = set()
            self.onDeviceSelectChange()
        return

    def __onSyncCompleted(self, _, diff):
        if 'battlePass' in diff:
            newPoints = diff['battlePass'].get('sumPoints', self.__oldPoints)
            newLevel = diff['battlePass'].get('level', self.__oldLevel)
            newVoteOption = diff['battlePass'].get('voteOption', self.__oldVoteOption)
            if newPoints != self.__oldPoints:
                self.onPointsUpdated()
            if newLevel != self.__oldLevel:
                self.onLevelUp()
            if newVoteOption != self.__oldVoteOption:
                self.onVoted()
            self.__oldPoints = newPoints
            self.__oldLevel = newLevel
            self.__oldVoteOption = newVoteOption

    def __getPackedBonusPointsList(self, vehTypeCompDescr=None, isWinner=True, isDiff=False):
        if isDiff:
            pointsList = self.__getConfig().bonusPointsDiffList(vehTypeCompDescr=vehTypeCompDescr)
        else:
            pointsList = self.__getConfig().bonusPointsList(vehTypeCompDescr=vehTypeCompDescr, isWinner=isWinner)
        return [ (key, len(list(group))) for key, group in groupby(pointsList) ]

    def __extractBadgeInfo(self):
        config = self.__getConfig()
        for level in range(1, self.getMaxLevel() + 1):
            if self.__processRewardIsBadge(config.getFreeReward(level)):
                return

        for level in range(1, self.getMaxLevel(False) + 1):
            if self.__processRewardIsBadge(config.getPostReward(level)):
                return

        self.__badge = None
        return

    def __processRewardIsBadge(self, reward):
        if 'dossier' not in reward:
            return False
        bonuses = BattlePassAwardsManager.composeBonuses([reward])
        for bonus in bonuses:
            if bonus.getName() != 'dossier':
                continue
            if bonus.getBadges():
                self.__badge = bonus
                return True

        return False

    def __extractTrophySelectTokensInfo(self):
        config = self.__getConfig()
        for bonusName in (TROPHY_GIFT_TOKEN_BONUS_NAME, NEW_DEVICE_GIFT_TOKEN_BONUS_NAME):
            for level in range(1, self.getMaxLevel() + 1):
                if self.__checkIfRewardIsToken(bonusName, config.getFreeReward(level)):
                    self.__deviceGiftTokensContainers[bonusName].addFreeTokenPos(level)
                if self.__checkIfRewardIsToken(bonusName, config.getPaidReward(level)):
                    self.__deviceGiftTokensContainers[bonusName].addPaidTokenPos(level)

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
        self.__oldVoteOption = 0
        self.__badge = None
        self.__currentMode = None
        for container in self.__deviceGiftTokensContainers.values():
            container.clear()

        return

    def __isOnboardingEnabled(self):
        if not self.__lobbyContext.getServerSettings().isOffersEnabled():
            return False
        return False if not self.__getConfig().isOnboardingEnabled() else True

    def __getOnboardingVehicles(self):
        if self.__onboardingVehicles is not None:
            return self.__onboardingVehicles
        else:
            self.__onboardingVehicles = set()
            if self.__isOnboardingEnabled():
                onboardingToken = getBattlePassOnboardingToken(self.getSeasonID())
                offer = self.__offersProvider.getOfferByToken(onboardingToken)
                if offer is not None:
                    for gift in offer.getAllGifts():
                        intCD = gift.bonus.displayedItem.intCD
                        itemTypeID, _, _ = vehicles.parseIntCompactDescr(intCD)
                        if itemTypeID == vehicles.ITEM_TYPES.vehicle:
                            self.__onboardingVehicles.add(intCD)

            return self.__onboardingVehicles
