# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_helpers.py
import typing
import logging
from collections import namedtuple
from constants import ARENA_BONUS_TYPE, QUEUE_TYPE
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from battle_pass_common import BattlePassConsts, BattlePassState, BattlePassInBattleProgress, BattlePassRewardReason, getMaxAvalable3DStyleProgressInChapter, AWARD_TYPE_TO_TOKEN_POSTFIX, BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS, BATTLE_PASS_TOKEN_NEW_DEVICE_OFFER_2020, BATTLE_PASS_TOKEN_TROPHY_OFFER_2020
from gui import GUI_SETTINGS
from gui.battle_pass.battle_pass_bonuses_helper import TROPHY_GIFT_TOKEN_BONUS_NAME, NEW_DEVICE_GIFT_TOKEN_BONUS_NAME
from gui.battle_pass.sounds import AwardVideoSoundControl
from gui.impl.gen import R
from gui.prb_control.dispatcher import g_prbLoader
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.event_dispatcher import showOfferGiftsWindow, showBattlePassAwardsWindow, showBattlePassDailyQuestsIntroWindow
from gui.shared.formatters import time_formatters
from gui.Scaleform.genConsts.SKILLS_CONSTANTS import SKILLS_CONSTANTS as SKILLS
from helpers import dependency, time_utils
from helpers.dependency import replace_none_kwargs
from nations import INDICES
from shared_utils import first, findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import CustomizationsBonus, TmanTemplateTokensBonus
_logger = logging.getLogger(__name__)
_CUSTOMIZATION_BONUS_NAME = 'customizations'
_TANKMAN_BONUS_NAME = 'tmanToken'

class BattlePassProgressionSubTabs(object):
    BUY_TAB = 0
    BUY_TAB_FOR_SHOP = 1
    BUY_LEVELS_TAB = 2
    BUY_LEVELS_TAB_FROM_SHOP = 3
    SELECT_STYLE_TAB = 4


BattlePassSeasonHistory = namedtuple('BattlePassSeasonHistory', 'maxBaseLevel maxPostLevel rewardVehicles seasonNum')
TokenPositions = namedtuple('TokenPositions', ['free', 'paid'])

def isBattlePassActiveSeason():
    battlePassController = dependency.instance(IBattlePassController)
    return battlePassController.isVisible()


def getPointsInfoStringID():
    return R.strings.battle_pass.points.top()


def getLevelProgression(level, points, levelsConfig):
    if level <= 0:
        basePoints = 0
        limitPoints = levelsConfig[0]
    else:
        basePoints = levelsConfig[level - 1]
        limitPoints = levelsConfig[level] - basePoints
    levelPoints = points - basePoints
    return (levelPoints, limitPoints)


def isSeasonEndingSoon():
    battlePassController = dependency.instance(IBattlePassController)
    return battlePassController.getFinalOfferTime() <= time_utils.getServerUTCTime()


def isBattlePassBought():
    battlePassController = dependency.instance(IBattlePassController)
    return battlePassController.isBought()


def getFormattedTimeLeft(seconds):
    return time_formatters.getTillTimeByResource(seconds, R.strings.battle_pass.status.timeLeft, removeLeadingZeros=True)


def getSeasonHistory(seasonID):
    battlePassController = dependency.instance(IBattlePassController)
    seasonsHistory = battlePassController.getSeasonsHistory()
    prevSeasonHistory = seasonsHistory.get(seasonID)
    return None if prevSeasonHistory is None else BattlePassSeasonHistory(prevSeasonHistory.get('maxBaseLevel'), prevSeasonHistory.get('maxPostLevel'), prevSeasonHistory.get('rewardVehicles'), prevSeasonHistory.get('seasonNum'))


def getLevelFromStats(seasonStats, seasonHistory):
    if seasonStats.maxBase == seasonHistory.maxBaseLevel:
        level = seasonStats.maxPost
        state = BattlePassState.POST
    else:
        level = seasonStats.maxBase
        state = BattlePassState.BASE
    if seasonStats.maxPost >= seasonHistory.maxPostLevel:
        state = BattlePassState.COMPLETED
    return (state, level)


def getInfoPageURL():
    return GUI_SETTINGS.battlePass.get('infoPage')


def getIntroVideoURL():
    return GUI_SETTINGS.battlePass.get('introVideo')


def getSupportedArenaBonusTypeFor(queueType, isInUnit):
    if queueType == QUEUE_TYPE.BATTLE_ROYALE:
        arenaBonusType = ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD if isInUnit else ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO
    else:
        arenaBonusTypeByQueueType = {QUEUE_TYPE.RANDOMS: ARENA_BONUS_TYPE.REGULAR,
         QUEUE_TYPE.RANKED: ARENA_BONUS_TYPE.RANKED,
         QUEUE_TYPE.MAPBOX: ARENA_BONUS_TYPE.MAPBOX}
        arenaBonusType = arenaBonusTypeByQueueType.get(queueType, ARENA_BONUS_TYPE.UNKNOWN)
    return arenaBonusType


def getSupportedCurrentArenaBonusType(queueType=None):
    dispatcher = g_prbLoader.getDispatcher()
    isInUnit = False
    if dispatcher:
        state = dispatcher.getFunctionalState()
        isInUnit = state.isInUnit(state.entityTypeID)
        if queueType is None:
            queueType = dispatcher.getEntity().getQueueType()
    return getSupportedArenaBonusTypeFor(queueType, isInUnit)


def setInBattleProgress(section, basePoints, sumPoints, hasBattlePass, setIfEmpty, arenaBonusType):
    if BattlePassConsts.PROGRESSION_INFO in section or BattlePassConsts.PROGRESSION_INFO_PREV in section:
        return
    if not setIfEmpty and (basePoints <= 0 or sumPoints <= 0):
        return
    battlePassController = dependency.instance(IBattlePassController)
    if not battlePassController.isEnabled():
        return
    oldPoints = sumPoints - basePoints
    curChapter, curLevel = battlePassController.getLevelByPoints(points=sumPoints)
    oldChapter, oldLevel = battlePassController.getLevelByPoints(points=oldPoints)
    curNewPoints, curMaxPoints = battlePassController.getProgressionByPoints(points=sumPoints, level=curLevel)
    pointsDiff = basePoints
    isEnabled = battlePassController.isGameModeEnabled(arenaBonusType)
    if oldLevel != curLevel:
        pointsDiff = curNewPoints
        awards = []
        if hasBattlePass:
            awardType = BattlePassConsts.REWARD_BOTH
        else:
            awardType = BattlePassConsts.REWARD_FREE
        awards.extend(battlePassController.getSingleAward(oldLevel + 1, awardType))
        prevInfo = BattlePassInBattleProgress(oldChapter, oldLevel + 1, 0, 0, 0, True, basePoints, awards, isEnabled)
        section[BattlePassConsts.PROGRESSION_INFO_PREV] = prevInfo
    isMaxLevel = curLevel == battlePassController.getMaxLevel()
    hasProgress = curNewPoints > 0 and not isMaxLevel
    if hasProgress or setIfEmpty:
        progressInfo = BattlePassInBattleProgress(curChapter, curLevel + 1, curNewPoints, curMaxPoints, pointsDiff, isMaxLevel, basePoints, [], isEnabled)
        section[BattlePassConsts.PROGRESSION_INFO] = progressInfo


def showOfferGiftsWindowByToken(token, overrideSuccessCallback=None):
    offersProvider = dependency.instance(IOffersDataProvider)
    offer = first(offersProvider.getAvailableOffersByToken(token))
    if offer is None:
        _logger.warning('Offer with token="%s" is not available.', token)
        return
    else:
        showOfferGiftsWindow(offer.id, overrideSuccessCallback=overrideSuccessCallback)
        return


def showOfferTrophyDevices():

    def successCallback(offerID, giftID, **kwargs):
        showSelectDeviceRewardWindow(offerID, giftID, **kwargs)

    showOfferGiftsWindowByToken(BATTLE_PASS_TOKEN_TROPHY_OFFER_2020, overrideSuccessCallback=successCallback)


def showOfferNewDevices():

    def successCallback(offerID, giftID, **kwargs):
        showSelectDeviceRewardWindow(offerID, giftID, **kwargs)

    showOfferGiftsWindowByToken(BATTLE_PASS_TOKEN_NEW_DEVICE_OFFER_2020, overrideSuccessCallback=successCallback)


def showOfferByBonusName(bonusName):
    if bonusName == TROPHY_GIFT_TOKEN_BONUS_NAME:
        showOfferTrophyDevices()
    elif bonusName == NEW_DEVICE_GIFT_TOKEN_BONUS_NAME:
        showOfferNewDevices()


def showSelectDeviceRewardWindow(offerID, giftID, **kwargs):
    offersProvider = dependency.instance(IOffersDataProvider)
    offer = offersProvider.getOffer(offerID)
    if offer is None:
        _logger.warning('Offer with offerID="%s" is not available.', offerID)
        return
    else:
        gift = offer.getGift(giftID)
        bonusData = gift.bonus.displayedBonusData if gift.bonus else {}
        showBattlePassAwardsWindow([bonusData], {'reason': BattlePassRewardReason.SELECT_TROPHY_DEVICE})
        return


def showVideo(videoSource, onVideoClosed=None, isAutoClose=False):
    if not videoSource:
        _logger.error('videoSource is not specified!')
        if callable(onVideoClosed):
            onVideoClosed()
        return
    if not videoSource.exists():
        _logger.error('videoSource is invalid!')
        if callable(onVideoClosed):
            onVideoClosed()
        return
    from gui.impl.lobby.video.video_view import VideoViewWindow
    window = VideoViewWindow(videoSource(), onVideoClosed=onVideoClosed, isAutoClose=isAutoClose, soundControl=AwardVideoSoundControl(videoSource()))
    window.load()


def getNotificationStorageKey(bonusName):
    if bonusName == TROPHY_GIFT_TOKEN_BONUS_NAME:
        return BattlePassStorageKeys.TROPHY_NOTIFICATION_SHOWN
    return BattlePassStorageKeys.NEW_DEVICE_NOTIFICATION_SHOWN if bonusName == NEW_DEVICE_GIFT_TOKEN_BONUS_NAME else ''


def getOfferGiftToken(giftTokenPrefix, level, awardType):
    return giftTokenPrefix + AWARD_TYPE_TO_TOKEN_POSTFIX[awardType] + str(level)


def getOfferMainToken(mainTokenPrefix, level, awardType):
    return mainTokenPrefix + AWARD_TYPE_TO_TOKEN_POSTFIX[awardType] + str(level)


@replace_none_kwargs(itemsCache=IItemsCache, battlePass=IBattlePassController)
def isGiftTokenUsed(token, battlePass=None, itemsCache=None):
    if not token.startswith(BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS):
        _logger.warning('Offer gift token name should be start from %s', BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS)
        return False
    else:
        level = token.rsplit(':')[:-1]
        return battlePass.getCurrentLevel() >= level and itemsCache.items.tokens.getTokens().get(token) is None


@replace_none_kwargs(battlePass=IBattlePassController, itemsCache=IItemsCache)
def getNotChosen3DStylesCount(battlePass=None, itemsCache=None):
    chosenItems = itemsCache.items.battlePass.getChosenItems()
    return battlePass.getCurrentChapter() - len(chosenItems)


@replace_none_kwargs(itemsCache=IItemsCache)
def getStyleForChapter(chapter, itemsCache=None):
    chosenItems = itemsCache.items.battlePass.getChosenItems()
    if chosenItems is None or chapter not in chosenItems:
        return
    else:
        intCD, _ = chosenItems[chapter]
        return itemsCache.items.getItemByCD(intCD)


@replace_none_kwargs(itemsCache=IItemsCache)
def getStyleInfoForChapter(chapter, itemsCache=None):
    chosenItems = itemsCache.items.battlePass.getChosenItems()
    return (None, None) if chosenItems is None or chapter not in chosenItems else chosenItems[chapter]


@replace_none_kwargs(itemsCache=IItemsCache)
def getCurrentStyleLevel(seasonID, chapterLevel, itemsCache=None):
    _, level = getStyleInfoForChapter(chapterLevel, itemsCache=itemsCache)
    if level is not None:
        return level
    else:
        level = getMaxAvalable3DStyleProgressInChapter(seasonID, chapterLevel, itemsCache.items.tokens.getTokens().keys())
        return level or 1


def getStyleInfo(bonus):
    if bonus is None:
        return
    elif bonus.getName() != _CUSTOMIZATION_BONUS_NAME:
        return
    else:
        item = findFirst(lambda c: c.get('custType') == 'style', bonus.getCustomizations())
        return None if item is None else bonus.getC11nItem(item)


@replace_none_kwargs(settingsCore=ISettingsCore)
def isBattlePassDailyQuestsIntroShown(settingsCore=None):
    return settingsCore.serverSettings.getBPStorage().get(BattlePassStorageKeys.DAILY_QUESTS_INTRO_SHOWN, False)


def showBattlePassDailyQuestsIntro():
    battlePassController = dependency.instance(IBattlePassController)
    if not battlePassController.isActive():
        return
    settingsCore = dependency.instance(ISettingsCore)
    if not isBattlePassDailyQuestsIntroShown(settingsCore=settingsCore):
        showBattlePassDailyQuestsIntroWindow()
        settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.DAILY_QUESTS_INTRO_SHOWN: True})


def getRecruitNation(recruitInfo):
    nation = first(recruitInfo.getNations())
    return INDICES.get(nation, 0)


def getTankmanInfo(bonus):
    if bonus is None:
        return
    elif bonus.getName() != _TANKMAN_BONUS_NAME:
        return
    else:
        tmanToken = first(bonus.getValue().keys())
        return None if tmanToken is None else getRecruitInfo(tmanToken)


def getDataByTankman(tankman):
    nation = getRecruitNation(tankman)
    iconName = tankman.getIconByNation(nation)
    tankmanName = tankman.getFullUserNameByNation(nation)
    skills = tankman.getLearntSkills()
    newSkillCount, _ = tankman.getNewSkillCount(onlyFull=True)
    if newSkillCount > 0:
        skills += [SKILLS.TYPE_NEW_SKILL] * (newSkillCount - skills.count(SKILLS.TYPE_NEW_SKILL))
    return (iconName, tankmanName, skills)


def getOfferTokenByGift(tokenID):
    return tokenID.replace('_gift', '')
