# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_helpers.py
import logging
from collections import namedtuple
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from battle_pass_common import BattlePassConsts, BattlePassState, BattlePassInBattleProgress, BattlePassRewardReason, BATTLE_PASS_TOKEN_TROPHY_OFFER, BATTLE_PASS_TOKEN_NEW_DEVICE_OFFER
from gui import GUI_SETTINGS
from gui.battle_pass.battle_pass_bonuses_helper import TROPHY_GIFT_TOKEN_BONUS_NAME, NEW_DEVICE_GIFT_TOKEN_BONUS_NAME
from gui.battle_pass.sounds import AwardVideoSoundControl
from gui.impl.gen import R
from gui.shared.event_dispatcher import showOfferGiftsWindow, showBattlePassAwardsWindow
from gui.shared.formatters import time_formatters
from helpers import dependency, time_utils
from helpers.http.url_formatters import addParamsToUrlQuery
from shared_utils import first
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.offers import IOffersDataProvider
_logger = logging.getLogger(__name__)

class BattlePassProgressionSubTabs(object):
    BUY_TAB = 0
    BUY_TAB_FOR_SHOP = 1
    VOTING_TAB = 2
    ONBOARDING_TAB = 3


BattlePassSeasonHistory = namedtuple('BattlePassSeasonHistory', 'maxBaseLevel maxPostLevel rewardVehicles')
TokenPositions = namedtuple('TokenPositions', ['free', 'paid'])

class BackgroundPositions(object):
    LEFT = 0
    RIGHT = 1
    UNKNOWN = 2


def isBattlePassActiveSeason():
    battlePassController = dependency.instance(IBattlePassController)
    return battlePassController.isVisible()


def getPointsInfoStringID(hasTop):
    path = R.strings.battle_pass_2020.points
    return path.top() if hasTop else path.any()


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


def isNeededToVote():
    battlePassController = dependency.instance(IBattlePassController)
    return not battlePassController.isPlayerVoted() and battlePassController.getState() != BattlePassState.BASE


def isPlayerVoted(*_):
    battlePassController = dependency.instance(IBattlePassController)
    return battlePassController.isPlayerVoted()


def isBattlePassBought():
    battlePassController = dependency.instance(IBattlePassController)
    return battlePassController.isBought()


def isCurrentBattlePassStateBase():
    battlePassController = dependency.instance(IBattlePassController)
    return battlePassController.getState() == BattlePassState.BASE


def getFormattedTimeLeft(seconds):
    return time_formatters.getTillTimeByResource(seconds, R.strings.battle_pass_2020.status.timeLeft, removeLeadingZeros=True)


def getSeasonHistory(seasonID):
    battlePassController = dependency.instance(IBattlePassController)
    seasonsHistory = battlePassController.getSeasonsHistory()
    prevSeasonHistory = seasonsHistory.get(seasonID)
    return None if prevSeasonHistory is None else BattlePassSeasonHistory(prevSeasonHistory.get('maxBaseLevel'), prevSeasonHistory.get('maxPostLevel'), prevSeasonHistory.get('rewardVehicles'))


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


def getExtrasVideoPageURL():
    battlePassController = dependency.instance(IBattlePassController)
    url = GUI_SETTINGS.battlePass.get('extrasVideoPage').replace('$SEASON_ID', str(battlePassController.getSeasonID()))
    params = {'level': battlePassController.getCurrentLevel(),
     'has_bp': int(battlePassController.isBought())}
    if battlePassController.isPlayerVoted():
        params['vote'] = battlePassController.getVoteOption()
    return addParamsToUrlQuery(url, params)


def getInfoPageURL():
    return GUI_SETTINGS.battlePass.get('infoPage')


def getIntroVideoURL():
    return GUI_SETTINGS.battlePass.get('introVideo')


def setInBattleProgress(section, basePoints, sumPoints, hasBattlePass):
    if basePoints <= 0 or sumPoints <= 0 or BattlePassConsts.PROGRESSION_INFO in section or BattlePassConsts.PROGRESSION_INFO_PREV in section:
        return
    battlePassController = dependency.instance(IBattlePassController)
    if not battlePassController.isEnabled():
        return
    oldPoints = sumPoints - basePoints
    curState, curLevel = battlePassController.getLevelByPoints(points=sumPoints)
    oldState, oldLevel = battlePassController.getLevelByPoints(points=oldPoints)
    curNewPoints, curMaxPoints = battlePassController.getProgressionByPoints(points=sumPoints, state=curState, level=curLevel)
    pointsDiff = basePoints
    if oldLevel != curLevel:
        pointsDiff = curNewPoints
        awards = []
        if oldState == BattlePassState.BASE:
            if hasBattlePass:
                awardType = BattlePassConsts.REWARD_BOTH
            else:
                awardType = BattlePassConsts.REWARD_FREE
        else:
            awardType = BattlePassConsts.REWARD_POST
        awards.extend(battlePassController.getSingleAward(oldLevel + 1, awardType))
        prevInfo = BattlePassInBattleProgress(oldState, oldLevel + 1, 0, 0, 0, True, basePoints, awards)
        section[BattlePassConsts.PROGRESSION_INFO_PREV] = prevInfo
    if curNewPoints > 0 and curLevel < battlePassController.getMaxLevel(curState == BattlePassState.BASE):
        progressInfo = BattlePassInBattleProgress(curState, curLevel + 1, curNewPoints, curMaxPoints, pointsDiff, False, basePoints, [])
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
        battlePassController = dependency.instance(IBattlePassController)
        battlePassController.getDeviceTokensContainer(TROPHY_GIFT_TOKEN_BONUS_NAME).saveChosenToken()
        showSelectDeviceRewardWindow(offerID, giftID, **kwargs)

    showOfferGiftsWindowByToken(BATTLE_PASS_TOKEN_TROPHY_OFFER, overrideSuccessCallback=successCallback)


def showOfferNewDevices():

    def successCallback(offerID, giftID, **kwargs):
        battlePassController = dependency.instance(IBattlePassController)
        battlePassController.getDeviceTokensContainer(NEW_DEVICE_GIFT_TOKEN_BONUS_NAME).saveChosenToken()
        showSelectDeviceRewardWindow(offerID, giftID, **kwargs)

    showOfferGiftsWindowByToken(BATTLE_PASS_TOKEN_NEW_DEVICE_OFFER, overrideSuccessCallback=successCallback)


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
        return
    else:
        from gui.impl.lobby.video.video_view import VideoViewWindow
        battlePassController = dependency.instance(IBattlePassController)
        logic = battlePassController.getFinalRewardLogic()
        if not videoSource.exists():
            logic.postNextState()
            return
        if onVideoClosed is None:
            onVideoClosed = logic.postNextState
        videoSource = videoSource()
        window = VideoViewWindow(videoSource, onVideoClosed=onVideoClosed, isAutoClose=isAutoClose, soundControl=AwardVideoSoundControl(videoSource))
        window.load()
        return


def getStorageKey(bonusName):
    if bonusName == TROPHY_GIFT_TOKEN_BONUS_NAME:
        return BattlePassStorageKeys.CHOSEN_TROPHY_DEVICES
    return BattlePassStorageKeys.CHOSEN_NEW_DEVICES if bonusName == NEW_DEVICE_GIFT_TOKEN_BONUS_NAME else ''


def getNotificationStorageKey(bonusName):
    if bonusName == TROPHY_GIFT_TOKEN_BONUS_NAME:
        return BattlePassStorageKeys.TROPHY_NOTIFICATION_SHOWN
    return BattlePassStorageKeys.NEW_DEVICE_NOTIFICATION_SHOWN if bonusName == NEW_DEVICE_GIFT_TOKEN_BONUS_NAME else ''
