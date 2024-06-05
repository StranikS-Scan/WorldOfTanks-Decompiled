# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_helpers.py
import itertools
import logging
from collections import namedtuple
import typing
from enum import Enum
import nations
from account_helpers.AccountSettings import AccountSettings, IS_BATTLE_PASS_COLLECTION_SEEN, IS_BATTLE_PASS_EXTRA_STARTED, LAST_BATTLE_PASS_POINTS_SEEN
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from battle_pass_common import BattlePassConsts, BattlePassTankmenSource, HOLIDAY_SEASON_OFFSET, TANKMAN_QUEST_CHAIN_ENTITLEMENT_POSTFIX
from constants import ARENA_BONUS_TYPE, QUEUE_TYPE
from gui import GUI_SETTINGS
from gui.Scaleform.genConsts.SKILLS_CONSTANTS import SKILLS_CONSTANTS as SKILLS
from gui.battle_pass.sounds import AwardVideoSoundControl
from gui.impl.gen import R
from gui.impl.gen.view_models.common.price_model import PriceModel
from gui.impl.wrappers.user_compound_price_model import PriceModelBuilder
from gui.prb_control.dispatcher import g_prbLoader
from gui.server_events.bonuses import VehiclesBonus
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.event_dispatcher import showBattlePassDailyQuestsIntroWindow
from gui.shared.formatters import time_formatters
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from helpers import dependency, time_utils
from helpers.dependency import replace_none_kwargs
from items.tankmen import getNationGroups
from nations import INDICES
from shared_utils import findFirst, first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IBattlePassController
if typing.TYPE_CHECKING:
    from typing import Any, Dict, List, Set
    from gui.impl.wrappers.user_compound_price_model import UserCompoundPriceModel
    from gui.server_events.bonuses import TmanTemplateTokensBonus
    from gui.shared.gui_items.customization.c11n_items import Customization
_logger = logging.getLogger(__name__)
_CUSTOMIZATION_BONUS_NAME = 'customizations'
TANKMAN_BONUS_NAME = 'tmanToken'
TokenPositions = namedtuple('TokenPositions', ['free', 'paid'])

class BattlePassMediaPatterns(str, Enum):
    STYLE = 'style'
    MEDIA = 'media'
    CHAPTER = 'ch'
    LEVEL = 'lvl'
    PART = 'pt'


class ChapterType(str, Enum):
    COMMON = 'common'
    EXTRA = 'extra'
    HOLIDAY = 'holiday'


_BATTLE_PASS_PRICE_CURRENCY_PRIORITY = (Currency.GOLD,)

@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def getChapterType(chapterID, battlePass=None):
    if battlePass.isHoliday():
        return ChapterType.HOLIDAY
    return ChapterType.EXTRA if battlePass.isExtraChapter(chapterID) else ChapterType.COMMON


def isBattlePassActiveSeason():
    battlePassController = dependency.instance(IBattlePassController)
    return battlePassController.isVisible()


def getPointsInfoStringID(gameMode=ARENA_BONUS_TYPE.REGULAR):
    points = R.strings.battle_pass.points.top()
    if gameMode == ARENA_BONUS_TYPE.COMP7:
        points = R.strings.battle_pass.prestige.top()
    return points


def isSeasonEndingSoon():
    battlePassController = dependency.instance(IBattlePassController)
    return battlePassController.getFinalOfferTime() <= time_utils.getServerUTCTime()


def getFormattedTimeLeft(seconds):
    return time_formatters.getTillTimeByResource(seconds, R.strings.battle_pass.status.timeLeft, removeLeadingZeros=True)


def getBattlePassUrl(urlPathName):
    return ''.join((GUI_SETTINGS.baseUrls['webBridgeRootURL'], GUI_SETTINGS.battlePassUrls.get(urlPathName)))


def getInfoPageURL():
    return getBattlePassUrl('infoPage')


def getExtraInfoPageURL():
    return getBattlePassUrl('extraInfoPage')


def getIntroVideoURL():
    return getBattlePassUrl('introVideo')


def getExtraIntroVideoURL():
    return getBattlePassUrl('extraIntroVideo')


def getIntroSlidesNames():
    return GUI_SETTINGS.battlePassIntroSlides


def getSeasonVisualSettings():
    if 'season' not in GUI_SETTINGS.battlePassVisuals:
        _logger.warning('"season" section is missing in "battlePassVisuals" settings')
        return {}
    return GUI_SETTINGS.battlePassVisuals['season']


def isSeasonWithAdditionalBackground():
    hasAdditionalBackground = getSeasonVisualSettings().get('hasAdditionalBackground')
    if hasAdditionalBackground is None:
        _logger.warning('"hasAdditionalBackground" section is missing in "battlePassVisuals->season" settings')
        return False
    else:
        return hasAdditionalBackground


def isSeasonWithSpecialTankmenScreen():
    hasSpecialTankmenScreen = getSeasonVisualSettings().get('hasSpecialTankmenScreen')
    if hasSpecialTankmenScreen is None:
        _logger.warning('"hasSpecialTankmenScreen" section is missing in "battlePassVisuals->season" settings')
        return False
    else:
        return hasSpecialTankmenScreen


def chaptersWithLogoBg():
    if 'chapter' not in GUI_SETTINGS.battlePassVisuals:
        _logger.warning('"chapter" section is missing in "battlePassVisuals" settings')
        return set()
    else:
        chaptersInfo = GUI_SETTINGS.battlePassVisuals['chapter'].get('hasChapterLogoInBg')
        if chaptersInfo is None:
            _logger.warning('"hasChapterLogoInBg" section is missed in battlePassVisuals->chapter settings')
            return set()
        return {int(chapterID) for chapterID, hasLogo in chaptersInfo.iteritems() if hasLogo}


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def getChaptersNumbers(battlePass=None):
    return {chapterID:chapterNum for chapterNum, chapterID in enumerate(sorted(battlePass.getChapterIDs()), 1)}


def getSupportedArenaBonusTypeFor(queueType, isInUnit):
    if queueType == QUEUE_TYPE.BATTLE_ROYALE:
        arenaBonusType = ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD if isInUnit else ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO
    else:
        arenaBonusTypeByQueueType = {QUEUE_TYPE.RANDOMS: ARENA_BONUS_TYPE.REGULAR,
         QUEUE_TYPE.RANKED: ARENA_BONUS_TYPE.RANKED,
         QUEUE_TYPE.MAPBOX: ARENA_BONUS_TYPE.MAPBOX,
         QUEUE_TYPE.EPIC: ARENA_BONUS_TYPE.EPIC_BATTLE,
         QUEUE_TYPE.COMP7: ARENA_BONUS_TYPE.COMP7,
         QUEUE_TYPE.WINBACK: ARENA_BONUS_TYPE.WINBACK}
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


def getTankmanFirstNationGroup(tankmanGroupName):
    for nationID in nations.MAP.iterkeys():
        group = findFirst(lambda nationGroup: nationGroup.name == tankmanGroupName, itertools.chain(getNationGroups(nationID, True).itervalues(), getNationGroups(nationID, False).itervalues()))
        if group is not None:
            return group

    return


def makeProgressionStyleMediaName(chapterID, styleLevel):
    return '{}_{}{}_{}{}'.format(BattlePassMediaPatterns.STYLE, BattlePassMediaPatterns.CHAPTER, getChaptersNumbers()[chapterID], BattlePassMediaPatterns.LEVEL, styleLevel)


def makeChapterMediaName(chapterID, part=''):
    mediaName = '{}_{}{}'.format(BattlePassMediaPatterns.MEDIA, BattlePassMediaPatterns.CHAPTER, getChaptersNumbers().get(chapterID, 0))
    return '{}_{}{}'.format(mediaName, BattlePassMediaPatterns.PART, part) if part else mediaName


def asBPVideoName(filename):
    return '.'.join(('battle_pass', filename))


def showBPFullscreenVideo(videoName, audioName, onVideoClosed=None):
    from gui.impl.lobby.battle_pass.fullscreen_video_view import FullscreenVideoWindow
    window = FullscreenVideoWindow(videoName, audioName, onVideoClosed=onVideoClosed)
    window.load()


@replace_none_kwargs(battlePass=IBattlePassController)
def getAllFinalRewards(chapterID, battlePass=None):
    return battlePass.getFreeFinalRewardTypes(chapterID).union(battlePass.getPaidFinalRewardTypes(chapterID))


@replace_none_kwargs(battlePass=IBattlePassController)
def getRewardSourceByType(reward, chapter, battlePass=None):
    freeRewards = battlePass.getRewardTypes(chapter).get(BattlePassConsts.REWARD_FREE)
    paidRewards = battlePass.getRewardTypes(chapter).get(BattlePassConsts.REWARD_PAID)
    if reward in freeRewards:
        if reward in paidRewards:
            return BattlePassConsts.REWARD_BOTH
        return BattlePassConsts.REWARD_FREE
    else:
        return BattlePassConsts.REWARD_PAID if reward in paidRewards else None


@replace_none_kwargs(battlePass=IBattlePassController, c11nService=ICustomizationService)
def getStyleForChapter(chapter, battlePass=None, c11nService=None):
    stylesConfig = battlePass.getStylesConfig()
    if chapter not in stylesConfig:
        _logger.error('Invalid chapterID: %s', chapter)
        return None
    else:
        styleID = stylesConfig[chapter]
        return c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID) if styleID is not None else None


@replace_none_kwargs(battlePass=IBattlePassController)
def getStyleInfoForChapter(chapter, battlePass=None):
    style = getStyleForChapter(chapter, battlePass=battlePass)
    return (style.intCD, style.getProgressionLevel()) if style is not None else (None, None)


@replace_none_kwargs(battlePass=IBattlePassController, c11nService=ICustomizationService)
def getVehicleInfoForChapter(chapter, battlePass=None, c11nService=None, awardSource=BattlePassConsts.REWARD_PAID):
    rewards = battlePass.getSingleAward(chapter, battlePass.getMaxLevelInChapter(chapter), awardType=awardSource)
    for bonus in rewards:
        if bonus.getName() == VehiclesBonus.VEHICLES_BONUS:
            vehicle, vehInfo = bonus.getVehicles()[0]
            styleId = vehInfo.get('customization', {}).get('styleId')
            style = c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleId) if styleId is not None else None
            return (vehicle, style)

    _logger.error("In chapterID: %s in final level doesn't have vehicle", chapter)
    return (None, None)


def getSingleVehicleForCustomization(customization):
    itemFilter = customization.descriptor.filter
    if itemFilter is not None and itemFilter.include:
        vehicles = []
        for node in itemFilter.include:
            if node.nations or node.levels:
                return
            if node.vehicles:
                vehicles.extend(node.vehicles)

        if len(vehicles) == 1:
            return vehicles[0]
    return


@replace_none_kwargs(settingsCore=ISettingsCore)
def isBattlePassDailyQuestsIntroShown(settingsCore=None):
    return settingsCore.serverSettings.getBPStorage().get(BattlePassStorageKeys.DAILY_QUESTS_INTRO_SHOWN, False)


@replace_none_kwargs(settingsCore=ISettingsCore)
def setBattlePassDailyQuestsIntroShown(settingsCore=None):
    settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.DAILY_QUESTS_INTRO_SHOWN: True})


def showBattlePassDailyQuestsIntro():
    battlePassController = dependency.instance(IBattlePassController)
    if not battlePassController.isActive():
        return
    if not isBattlePassDailyQuestsIntroShown():
        showBattlePassDailyQuestsIntroWindow()
        setBattlePassDailyQuestsIntroShown()


def getRecruitNation(recruitInfo):
    nation = first(recruitInfo.getNations())
    return INDICES.get(nation, 0)


def getTankmanInfo(bonus):
    if bonus is None:
        return
    elif bonus.getName() != TANKMAN_BONUS_NAME:
        return
    else:
        tmanToken = first(bonus.getValue().keys())
        return None if tmanToken is None else getRecruitInfo(tmanToken)


def getDataByTankman(tankman):
    nation = getRecruitNation(tankman)
    iconName = tankman.getIconByNation(nation)
    tankmanName = tankman.getFullUserNameByNation(nation)
    skills = tankman.getAllKnownSkills()
    newSkillCount, _ = tankman.getNewSkillCount(onlyFull=True)
    groupName = tankman.getGroupName()
    if newSkillCount > 0:
        skills += [SKILLS.TYPE_NEW_SKILL] * (newSkillCount - skills.count(SKILLS.TYPE_NEW_SKILL))
    return (iconName,
     tankmanName,
     skills,
     groupName)


@replace_none_kwargs(battlePass=IBattlePassController)
def getReceivedTankmenCount(groupName, battlePass=None):
    entitlement = battlePass.getTankmenEntitlements().get(groupName)
    return entitlement.amount if entitlement is not None else 0


@replace_none_kwargs(battlePass=IBattlePassController)
def getTankmenShopPackages(battlePass=None):
    shopPackages = {}
    tankmen = battlePass.getSpecialTankmen()
    for tankman, tankmanInfo in tankmen.iteritems():
        source = tankmanInfo.get('source')
        if source == BattlePassTankmenSource.SHOP:
            shopPackages[tankman] = tankmanInfo.get('availableCount', 0)
        if source == BattlePassTankmenSource.QUEST_CHAIN:
            packageName = tankman + TANKMAN_QUEST_CHAIN_ENTITLEMENT_POSTFIX
            shopPackages[packageName] = tankmanInfo.get('availableCount', 0)

    return shopPackages


def getOfferTokenByGift(tokenID):
    return tokenID.replace('_gift', '')


def fillBattlePassCompoundPrice(compoundPriceModel, compoundPrice):
    prices = compoundPriceModel.getPrices()
    prices.clear()
    pricesData = compoundPrice.items()
    prices.reserve(len(pricesData))
    for priceID, price in pricesData:
        priceModel = PriceModel()
        PriceModelBuilder.fillPriceModel(priceModel, price, None, None, False, priceID)
        prices.addViewModel(priceModel)

    prices.invalidate()
    return


def getCompoundPriceDefaultID(compoundPrice):
    return next((priceID for currency in _BATTLE_PASS_PRICE_CURRENCY_PRIORITY for priceID, priceData in compoundPrice.iteritems() if currency in priceData and priceData[currency]))


@replace_none_kwargs(battlePass=IBattlePassController)
def getFinalTankmen(chapterID, awardType, battlePass=None):
    maxLevel = battlePass.getMaxLevelInChapter(chapterID)
    rewards = battlePass.getSingleAward(chapterID, maxLevel, awardType=awardType)
    characterBonuses = [ reward for reward in rewards if reward.getName() == TANKMAN_BONUS_NAME ]
    if not characterBonuses:
        _logger.warning('%s chapter does not have tankman at final level!', chapterID)
    return [ getTankmanInfo(bonus) for bonus in characterBonuses ]


@replace_none_kwargs(settingsCore=ISettingsCore, battlePass=IBattlePassController)
def updateBuyAnimationFlag(chapterID, settingsCore=None, battlePass=None):
    settings = settingsCore.serverSettings
    shownChapters = settings.getBPStorage().get(BattlePassStorageKeys.BUY_ANIMATION_WAS_SHOWN)
    chapter = 1 << battlePass.getChapterIndex(chapterID)
    if _isChapterShown(shownChapters, chapter):
        settings.saveInBPStorage({BattlePassStorageKeys.BUY_ANIMATION_WAS_SHOWN: shownChapters | chapter})
        return True
    return False


@replace_none_kwargs(battlePass=IBattlePassController)
def updateBattlePassSettings(data, battlePass=None):
    version = battlePass.getSeasonNum()
    versionStorageKey = BattlePassStorageKeys.FLAGS_VERSION
    if battlePass.isHoliday():
        version -= HOLIDAY_SEASON_OFFSET
        versionStorageKey = BattlePassStorageKeys.FLAGS_VERSION_HOLIDAY
    if data[versionStorageKey] != version:
        _updateClientSettings()
        _updateServerSettings(data)
        data[versionStorageKey] = version
        return True
    return False


def _updateClientSettings():
    AccountSettings.setSettings(LAST_BATTLE_PASS_POINTS_SEEN, {})
    AccountSettings.setSettings(IS_BATTLE_PASS_EXTRA_STARTED, False)
    AccountSettings.setSettings(IS_BATTLE_PASS_COLLECTION_SEEN, False)


def _updateServerSettings(data):
    data[BattlePassStorageKeys.INTRO_SHOWN] = False
    data[BattlePassStorageKeys.INTRO_VIDEO_SHOWN] = False
    data[BattlePassStorageKeys.BUY_ANIMATION_WAS_SHOWN] = 0
    data[BattlePassStorageKeys.DAILY_QUESTS_INTRO_SHOWN] = False
    data[BattlePassStorageKeys.EXTRA_CHAPTER_INTRO_SHOWN] = False
    data[BattlePassStorageKeys.EXTRA_CHAPTER_VIDEO_SHOWN] = False


def _isChapterShown(shownChapters, chapter):
    return shownChapters & chapter == 0
