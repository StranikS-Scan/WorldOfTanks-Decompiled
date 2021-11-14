# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/main_page_vos.py
from constants import CURRENT_REALM
from gui.ranked_battles.ranked_helpers import getRankedBattlesInfoPageUrl
from ranked_common import SwitchState
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.shared.utils.functions import makeTooltip
from helpers import time_utils
_EMPTY_WEB_PAGES = {RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID, RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID}

def _getYearLeaderboardBG():
    defaultBG = R.images.gui.maps.icons.rankedBattles.bg.lb_default
    leaderboardBG = R.images.gui.maps.icons.rankedBattles.bg.dyn('lb_{}'.format(CURRENT_REALM), defaultBG)
    return backport.image(leaderboardBG())


def _getSeasonOnMain(isMastered):
    mainMenuLinkage = RANKEDBATTLES_ALIASES.RANKED_BATTLES_DIVISIONS_VIEW_UI
    if isMastered:
        mainMenuLinkage = RANKEDBATTLES_ALIASES.RANKED_BATTLES_LEAGUES_VIEW_UI
    return {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID,
     'viewId': mainMenuLinkage,
     'linkage': mainMenuLinkage,
     'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
     'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.ranks.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.ranks.body()))}


def _getSeasonOffMain(isYearLBEnabled):
    mainLinkage = 'BrowserViewStackExPaddingUI'
    mainViewId = RANKEDBATTLES_ALIASES.RANKED_BATTLES_WEB_SEASON_GAP_ALIAS
    if not isYearLBEnabled:
        mainLinkage = RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_GAP_VIEW_UI
        mainViewId = RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_GAP_VIEW_UI
    return {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID,
     'viewId': mainViewId,
     'linkage': mainLinkage,
     'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
     'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.ranks.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.ranks.body()))}


def _getRewardsPage(isSeasonOff=False, isYearRewardEnabled=True):
    enabled = True
    viewID = RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_UI
    if isSeasonOff:
        enabled = isYearRewardEnabled
        viewID = RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_SEASON_OFF_ALIAS
    return {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID,
     'viewId': viewID,
     'linkage': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_UI,
     'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
     'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.rewards.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.rewards.body() if enabled else R.strings.tooltips.rankedBattlesView.rewards.body.seasonOff())),
     'enabled': enabled}


def _getShopPage(isRankedShop):
    return ({'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_SHOP_ID,
      'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_SHOP_ALIAS,
      'linkage': 'BrowserViewStackExPaddingUI',
      'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.shop_bg()),
      'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.shop.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.shop.body()))},) if isRankedShop else ()


def _getRatingPage():
    return {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID,
     'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_RAITING_ALIAS,
     'linkage': 'BrowserViewStackExPaddingUI',
     'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
     'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.rating.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.rating.body()))}


def _getYearRatingPage(isYearLBVisible, yearLBSize, disabled):
    body = R.strings.tooltips.rankedBattlesView.yearRating.body
    return ({'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID,
      'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_YEAR_RAITING_ALIAS,
      'linkage': 'BrowserViewStackExPaddingUI',
      'background': _getYearLeaderboardBG(),
      'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.yearRating.header(), amount=yearLBSize), body=backport.text(body.disabled()) if disabled else backport.text(body())),
      'enabled': not disabled},) if isYearLBVisible else ()


def _getInfoPage():
    return {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID,
     'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_INFO_ALIAS,
     'linkage': 'BrowserViewStackExPaddingUI',
     'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
     'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.info.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.info.body()))}


def getBubbleLabel(counter):
    return '' if not bool(counter) else backport.text(R.strings.ranked_battles.rankedBattleMainView.emptyBubble())


def getCountersData(rankedController, awardsCounter, infoCounter, yearRatingCounter, shopCounter):
    result = [{'componentId': RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID,
      'count': infoCounter}]
    if rankedController.isYearRewardEnabled():
        result.append({'componentId': RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID,
         'count': awardsCounter})
    if rankedController.isYearLBEnabled():
        result.append({'componentId': RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID,
         'count': yearRatingCounter})
    if rankedController.isRankedShopEnabled():
        result.append({'componentId': RANKEDBATTLES_CONSTS.RANKED_BATTLES_SHOP_ID,
         'count': shopCounter})
    return result


def getRankedMainSeasonOnItems(isRankedShop, yearLBState, isYearRewardEnabled, yearLBSize, isMastered):
    result = list()
    result.append(_getSeasonOnMain(isMastered))
    result.append(_getRewardsPage(isYearRewardEnabled=isYearRewardEnabled))
    result.extend(getRankedMainSeasonAllItems(isRankedShop, yearLBState, yearLBSize))
    return result


def getRankedMainSeasonOffItems(isRankedShop, yearLBState, isYearRewardEnabled, yearLBSize):
    result = list()
    result.append(_getSeasonOffMain(yearLBState == SwitchState.ENABLED))
    result.append(_getRewardsPage(True, isYearRewardEnabled))
    result.extend(getRankedMainSeasonAllItems(isRankedShop, yearLBState, yearLBSize))
    return result


def getRankedMainSeasonAllItems(isRankedShop, yearLBState, yearLBSize):
    result = list()
    result.extend(_getShopPage(isRankedShop))
    result.append(_getRatingPage())
    result.extend(_getYearRatingPage(yearLBState != SwitchState.HIDDEN, yearLBSize, disabled=yearLBState == SwitchState.DISABLED))
    if getRankedBattlesInfoPageUrl():
        result.append(_getInfoPage())
    return result


def getRankedMainSeasonOnHeader(season, itemID):
    title = backport.text(R.strings.ranked_battles.rankedBattle.title())
    leftSideText = ''
    rightSideText = ''
    tooltip = TOOLTIPS_CONSTANTS.RANKED_CALENDAR_DAY_INFO
    if itemID in _EMPTY_WEB_PAGES:
        title = ''
        tooltip = ''
    elif itemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID:
        leftSideText = backport.text(R.strings.ranked_battles.rankedBattleMainView.infoPage.header())
        tooltip = ''
    elif season is not None:
        startDate = season.getStartDate()
        endDate = season.getEndDate()
        timeDelta = time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(endDate))
        if timeDelta > time_utils.ONE_WEEK:
            leftSideText = backport.text(R.strings.ranked_battles.rankedBattleMainView.date.period(), start=backport.getLongDateFormat(startDate), finish=backport.getLongDateFormat(endDate))
        else:
            leftSideText = backport.getTillTimeStringByRClass(timeDelta, R.strings.ranked_battles.rankedBattleMainView.date)
        rightSideText = backport.text(R.strings.ranked_battles.rankedBattleMainView.season(), season=season.getUserName())
    return {'title': title,
     'leftSideText': leftSideText,
     'rightSideText': rightSideText,
     'tooltip': tooltip}


def getRankedMainSeasonOffHeader(prevSeason, nextSeason, isYearGap, itemID):
    title = backport.text(R.strings.ranked_battles.rankedBattle.title())
    leftSideText = ''
    rightSideText = ''
    if itemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID and isYearGap:
        rightSideText = backport.text(R.strings.ranked_battles.rankedBattleMainView.yearGap.header())
    elif itemID in _EMPTY_WEB_PAGES:
        title = ''
    elif itemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID:
        rightSideText = backport.text(R.strings.ranked_battles.rankedBattleMainView.infoPage.header())
    else:
        rightSideText = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonCompleteSingle(), season=prevSeason.getUserName())
        if nextSeason is not None:
            rightSideText = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonComplete(), season=prevSeason.getUserName())
            leftSideText = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap(), newSeason=nextSeason.getUserName(), date=backport.getLongDateFormat(nextSeason.getStartDate()))
    return {'title': title,
     'leftSideText': leftSideText,
     'rightSideText': rightSideText,
     'tooltip': ''}
