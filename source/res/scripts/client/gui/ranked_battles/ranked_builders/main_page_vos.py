# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/main_page_vos.py
import BigWorld
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.shared.utils.functions import makeTooltip
from helpers import time_utils

def getBubbleLabel(counter):
    return '' if not bool(counter) else backport.text(R.strings.ranked_battles.rankedBattleMainView.emptyBubble())


def getCountersData(awardsCounter, infoCounter):
    return [{'componentId': RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID,
      'count': awardsCounter}, {'componentId': RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID,
      'count': infoCounter}]


def getRankedMainSeasonOnItems(isMastered):
    if isMastered:
        mainMenuLinkage = RANKEDBATTLES_ALIASES.RANKED_BATTLES_LEAGUES_VIEW_UI
    else:
        mainMenuLinkage = RANKEDBATTLES_ALIASES.RANKED_BATTLES_DIVISIONS_VIEW_UI
    return [{'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID,
      'viewId': mainMenuLinkage,
      'linkage': mainMenuLinkage,
      'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
      'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.ranks.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.ranks.body()))},
     {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID,
      'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_UI,
      'linkage': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_UI,
      'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
      'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.rewards.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.rewards.body()))},
     {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID,
      'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_RAITING_ALIAS,
      'linkage': 'BrowserViewStackExPaddingUI',
      'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
      'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.rating.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.rating.body()))},
     {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID,
      'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_INFO_ALIAS,
      'linkage': 'BrowserViewStackExPaddingUI',
      'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.rewards()),
      'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.info.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.info.body()))}]


def getRankedMainSeasonOffItems():
    return [{'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID,
      'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_GAP_VIEW_UI,
      'linkage': RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_GAP_VIEW_UI,
      'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
      'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.ranks.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.ranks.body()))},
     {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID,
      'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_UI,
      'linkage': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_UI,
      'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
      'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.rewards.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.rewards.body()))},
     {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID,
      'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_RAITING_ALIAS,
      'linkage': 'BrowserViewStackExPaddingUI',
      'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
      'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.rating.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.rating.body()))},
     {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID,
      'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_INFO_ALIAS,
      'linkage': 'BrowserViewStackExPaddingUI',
      'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.rewards()),
      'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.info.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.info.body()))}]


def getRankedMainSeasonOnHeader(season, itemID):
    leftSideText = ''
    rightSideText = ''
    tooltip = TOOLTIPS_CONSTANTS.RANKED_CALENDAR_DAY_INFO
    if itemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID:
        leftSideText = backport.text(R.strings.ranked_battles.rankedBattleMainView.infoPage.header())
        tooltip = ''
    elif season is not None:
        startDate = season.getStartDate()
        endDate = season.getEndDate()
        timeDelta = time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(endDate))
        if timeDelta > time_utils.ONE_WEEK:
            leftSideText = backport.text(R.strings.ranked_battles.rankedBattleMainView.date.period(), start=BigWorld.wg_getLongDateFormat(startDate), finish=BigWorld.wg_getLongDateFormat(endDate))
        else:
            leftSideText = backport.getTillTimeStringByRClass(timeDelta, R.strings.ranked_battles.rankedBattleMainView.date)
        rightSideText = backport.text(R.strings.ranked_battles.rankedBattleMainView.season(), season=season.getUserName())
    return {'title': backport.text(R.strings.ranked_battles.rankedBattle.title()),
     'leftSideText': leftSideText,
     'rightSideText': rightSideText,
     'tooltip': tooltip}


def getRankedMainSeasonOffHeader():
    return {'title': backport.text(R.strings.ranked_battles.rankedBattle.title()),
     'leftSideText': '',
     'rightSideText': '',
     'tooltip': ''}
