# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_helpers.py
import logging
from collections import namedtuple
from battle_pass_common import BattlePassConsts, BattlePassState, BattlePassInBattleProgress
from gui import GUI_SETTINGS
from gui.battle_pass.sounds import AwardVideoSoundControl
from gui.impl.gen import R
from gui.shared.formatters import time_formatters
from helpers import dependency, time_utils
from helpers.http.url_formatters import addParamsToUrlQuery
from skeletons.gui.game_control import IBattlePassController
_logger = logging.getLogger(__name__)

class BattlePassProgressionSubTabs(object):
    BUY_TAB = 0
    BUY_TAB_FOR_SHOP = 1
    VOTING_TAB = 2


BattlePassSeasonHistory = namedtuple('BattlePassSeasonHistory', 'maxBaseLevel maxPostLevel rewardVehicles')

class BackgroundPositions(object):
    LEFT = 0
    RIGHT = 1


VEHICLES_BACKGROUND_POSITIONS = {22017: BackgroundPositions.LEFT,
 15697: BackgroundPositions.RIGHT,
 2417: BackgroundPositions.LEFT,
 14113: BackgroundPositions.RIGHT}

def getVehicleBackgroundPosition(vehCD):
    return VEHICLES_BACKGROUND_POSITIONS.get(vehCD)


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


def showVideo(videoSource, onVideoClosed=None, isAutoClose=False):
    if not videoSource:
        _logger.error('videoSource is not specified!')
        return
    from gui.impl.lobby.video.video_view import VideoViewWindow
    window = VideoViewWindow(videoSource, onVideoClosed=onVideoClosed, isAutoClose=isAutoClose, soundControl=AwardVideoSoundControl(videoSource))
    window.load()
