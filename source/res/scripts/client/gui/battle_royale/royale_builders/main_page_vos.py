# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_royale/royale_builders/main_page_vos.py
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.Scaleform.genConsts.BATTLEROYALE_CONSTS import BATTLEROYALE_CONSTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport.backport_system_locale import getLongDateFormat
from gui.impl.gen import R
from gui.shared.utils.functions import makeTooltip
from helpers import time_utils

def getBubbleLabel(counter):
    return '' if not bool(counter) else backport.text(R.strings.ranked_battles.rankedBattleMainView.emptyBubble())


def getCounterData(infoCounter):
    return [{'componentId': BATTLEROYALE_CONSTS.BATTLE_ROYALE_INFO_ID,
      'count': infoCounter}]


def getTabsItems(isMastered):
    if isMastered:
        mainMenuLinkage = BATTLEROYALE_ALIASES.BATTLE_ROYALE_PROGRESS_FINAL_UI
    else:
        mainMenuLinkage = BATTLEROYALE_ALIASES.BATTLE_ROYALE_PROGRESS_UI
    return [{'id': BATTLEROYALE_CONSTS.BATTLE_ROYALE_PROGRESS_ID,
      'viewId': mainMenuLinkage,
      'linkage': mainMenuLinkage,
      'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.battle_royale.viewStack.progress.header()), body=backport.text(R.strings.tooltips.battle_royale.viewStack.progress.body()))}, {'id': BATTLEROYALE_CONSTS.BATTLE_ROYALE_AWARDS_ID,
      'viewId': BATTLEROYALE_ALIASES.BATTLE_ROYALE_AWARDS_UI,
      'linkage': BATTLEROYALE_ALIASES.BATTLE_ROYALE_AWARDS_UI,
      'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.battle_royale.viewStack.rewards.header()), body=backport.text(R.strings.tooltips.battle_royale.viewStack.rewards.body()))}, {'id': BATTLEROYALE_CONSTS.BATTLE_ROYALE_INFO_ID,
      'viewId': BATTLEROYALE_ALIASES.BATTLE_ROYALE_INFO_UI,
      'linkage': BATTLEROYALE_ALIASES.BATTLE_ROYALE_INFO_UI,
      'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.battle_royale.viewStack.info.header()), body=backport.text(R.strings.tooltips.battle_royale.viewStack.info.body()))}]


def getBattleRoyaleHeader(currentSeason, nextSeason):
    if currentSeason:
        startDate = currentSeason.getStartDate()
        endDate = currentSeason.getEndDate()
        timeDelta = time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(endDate))
        if timeDelta > time_utils.ONE_WEEK:
            leftSideText = backport.text(R.strings.battle_royale.mainPage.date.period(), start=getLongDateFormat(startDate), finish=getLongDateFormat(endDate))
        else:
            leftSideText = backport.getTillTimeStringByRClass(timeDelta, R.strings.battle_royale.mainPage.currentSeason.date)
    elif nextSeason:
        startDate = nextSeason.getStartDate()
        timeDelta = time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(startDate))
        leftSideText = backport.getTillTimeStringByRClass(timeDelta, R.strings.battle_royale.mainPage.nextSeason.date)
    else:
        leftSideText = backport.text(R.strings.battle_royale.mainPage.seasonFinished())
    return {'title': backport.text(R.strings.battle_royale.progressMainPage.header()),
     'leftSideText': leftSideText,
     'rightSideText': '',
     'tooltip': TOOLTIPS_CONSTANTS.BATTLE_ROYALE_PRIME_TIMES}
