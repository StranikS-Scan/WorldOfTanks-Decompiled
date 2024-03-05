# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_helpers.py
import logging
from collections import namedtuple
import typing
from shared_utils import first
from account_helpers.AccountSettings import AccountSettings, IS_BATTLE_PASS_MARATHON_STARTED, LAST_BATTLE_PASS_POINTS_SEEN, IS_BATTLE_PASS_COLLECTION_SEEN
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from constants import ARENA_BONUS_TYPE, QUEUE_TYPE
from gui import GUI_SETTINGS
from gui.Scaleform.genConsts.SKILLS_CONSTANTS import SKILLS_CONSTANTS as SKILLS
from gui.battle_pass.sounds import AwardVideoSoundControl
from gui.impl.gen import R
from gui.impl.gen.view_models.common.price_model import PriceModel
from gui.impl.wrappers.user_compound_price_model import PriceModelBuilder
from gui.prb_control.dispatcher import g_prbLoader
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.event_dispatcher import showBattlePassDailyQuestsIntroWindow
from gui.shared.formatters import time_formatters
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency, time_utils
from helpers.dependency import replace_none_kwargs
from nations import INDICES
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IBattlePassController
if typing.TYPE_CHECKING:
    from typing import Dict, List
    from gui.impl.wrappers.user_compound_price_model import UserCompoundPriceModel
    from gui.server_events.bonuses import TmanTemplateTokensBonus
    from gui.shared.gui_items.customization.c11n_items import Customization
_logger = logging.getLogger(__name__)
_CUSTOMIZATION_BONUS_NAME = 'customizations'
TANKMAN_BONUS_NAME = 'tmanToken'
TokenPositions = namedtuple('TokenPositions', ['free', 'paid'])

def chaptersIDsComparator(firstID, secondID):
    order = getChaptersOrder()
    return cmp(order.get(firstID), order.get(secondID))


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


def isIntroVideoExist():
    return bool(GUI_SETTINGS.battlePassUrls.get('introVideo'))


def isExtraIntroVideoExist():
    return bool(GUI_SETTINGS.battlePassUrls.get('extraIntroVideo'))


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def getChaptersOrder(battlePass=None):
    chapterIDs = [ chapter for chapter in battlePass.getChapterIDs() if not battlePass.isMarathonChapter(chapter) ]
    chapterIDs.sort()
    marathonChapterID = battlePass.getMarathonChapterID()
    if marathonChapterID:
        chapterIDs.append(marathonChapterID)
    return dict(zip(chapterIDs, GUI_SETTINGS.battlePassChaptersOrder))


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


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def showBPGamefaceVideo(chapter, level, battlePass=None, onVideoClosed=None):
    from gui.impl.lobby.battle_pass.style_video_view import StyleVideoViewWindow
    chapterIDs = battlePass.getChapterIDs()
    if chapter not in chapterIDs or level is None:
        _logger.error('Both chapter and level must be specified and correct!')
    else:
        window = StyleVideoViewWindow(chapter, level, onVideoClosed=onVideoClosed)
        window.load()
    return


@replace_none_kwargs(battlePass=IBattlePassController, c11nService=ICustomizationService)
def getStyleForChapter(chapter, battlePass=None, c11nService=None):
    stylesConfig = battlePass.getStylesConfig()
    if chapter not in stylesConfig:
        _logger.error('Invalid chapterID: %s', chapter)
        return None
    else:
        return c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, stylesConfig[chapter])


@replace_none_kwargs(battlePass=IBattlePassController)
def getStyleInfoForChapter(chapter, battlePass=None):
    style = getStyleForChapter(chapter, battlePass=battlePass)
    return (style.intCD, style.getProgressionLevel()) if style is not None else (None, None)


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
    if newSkillCount > 0:
        skills += [SKILLS.TYPE_NEW_SKILL] * (newSkillCount - skills.count(SKILLS.TYPE_NEW_SKILL))
    return (iconName, tankmanName, skills)


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
    if data[BattlePassStorageKeys.FLAGS_VERSION] != version:
        _updateClientSettings()
        _updateServerSettings(data)
        data[BattlePassStorageKeys.FLAGS_VERSION] = version
        return True
    return False


def _updateClientSettings():
    AccountSettings.setSettings(LAST_BATTLE_PASS_POINTS_SEEN, {})
    AccountSettings.setSettings(IS_BATTLE_PASS_MARATHON_STARTED, False)
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
