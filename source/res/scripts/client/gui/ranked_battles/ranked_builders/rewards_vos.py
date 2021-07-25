# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/rewards_vos.py
import typing
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import icons, text_styles
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.ranked_battles.ranked_builders import shared_vos
from gui.ranked_battles.constants import STANDARD_POINTS_COUNT
if typing.TYPE_CHECKING:
    from gui.ranked_battles.ranked_models import Rank, Division
    from gui.ranked_battles.constants import YearAwardsNames

def getSeasonOnTabs(selectedLinkage, isYearRewardEnabled):
    result = [__getRanksTab(selectedLinkage == RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_RANKS_UI, True), __getLeaguesTab(selectedLinkage == RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_LEAGUES_UI, True)]
    if isYearRewardEnabled:
        result.append(__getYearRewardTab(selectedLinkage == RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_YEAR_UI, True))
    return result


def getSeasonOffTabs(isYearRewardEnabled):
    result = [__getRanksTab(False, False), __getLeaguesTab(False, False)]
    if isYearRewardEnabled:
        result.append(__getYearRewardTab(True, True))
    return result


def __getRanksTab(selected, enabled):
    return {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_RANKEDS_ID,
     'label': backport.text(R.strings.ranked_battles.rewardsView.tabs.ranks()),
     'linkage': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_RANKS_UI,
     'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_RANKS_UI,
     'selected': selected,
     'enabled': enabled}


def __getLeaguesTab(selected, enabled):
    return {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_LEAGUES_ID,
     'label': backport.text(R.strings.ranked_battles.rewardsView.tabs.leagues()),
     'linkage': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_LEAGUES_UI,
     'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_LEAGUES_UI,
     'selected': selected,
     'enabled': enabled}


def __getYearRewardTab(selected, enabled):
    return {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_YEAR_ID,
     'label': backport.text(R.strings.ranked_battles.rewardsView.tabs.year()),
     'linkage': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_YEAR_UI,
     'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_YEAR_UI,
     'selected': selected,
     'enabled': enabled}


def getDivisionVO(division):
    divisionVO = shared_vos.getDivisionVO(division)
    divisionVO.update({'name': text_styles.promoTitle(divisionVO['name'])})
    return divisionVO


def getRankRewardsVO(rank, bonuses, currentRankID):
    if rank.getID() == currentRankID:
        awardState = RANKEDBATTLES_CONSTS.RANKED_REWARDS_RANK_CURRENT
    elif rank.getID() == currentRankID + 1:
        awardState = RANKEDBATTLES_CONSTS.RANKED_REWARDS_RANK_NEXT
    elif rank.getID() < currentRankID:
        awardState = RANKEDBATTLES_CONSTS.RANKED_REWARDS_RANK_RECEIVED
    else:
        awardState = RANKEDBATTLES_CONSTS.RANKED_REWARDS_RANK_LOCKED
    return {'state': awardState,
     'rankID': rank.getID(),
     'levelStr': rank.getUserName(),
     'bonuses': bonuses}


def getLeagueRewardVO(leagueID, styleBonus, styleID, styleName, badgeID, isCurrent):
    descr = backport.text(R.strings.ranked_battles.rewardsView.tabs.leagues.awardDescr.style(), styleName=styleName, badgeName=backport.text(R.strings.badge.dyn('badge_{}'.format(badgeID))()))
    return {'leagueID': leagueID,
     'title': backport.text(R.strings.ranked_battles.rewardsView.tabs.leagues.dyn('league%s' % leagueID)()),
     'description': descr,
     'styleID': styleID,
     'isSpecial': styleBonus.isSpecial,
     'specialAlias': styleBonus.specialAlias,
     'isCurrent': isCurrent}


def getYearRewardDataVO(points, awards, rewardingComplete, awardType, compensation, exchange):
    if rewardingComplete:
        title = backport.text(R.strings.ranked_battles.rewardsView.tabs.year.title.awarded(), points=points)
    else:
        title = backport.text(R.strings.ranked_battles.rewardsView.tabs.year.title.notAwarded(), points=points)
    tooltipBody = backport.text(R.strings.tooltips.rankedBattleView.rewardsView.tabs.year.scorePoint.body.mainText())
    if exchange > 0:
        exchangePart = backport.text(R.strings.tooltips.rankedBattleView.rewardsView.tabs.year.scorePoint.body.exchangeText(), points=text_styles.stats(str(STANDARD_POINTS_COUNT)), rankedImg=icons.makeImageTag(backport.image(R.images.gui.maps.icons.rankedBattles.ranked_point_16x16()), 16, 16, -3), crystal=text_styles.stats(exchange), crystalImg=icons.crystal())
        tooltipBody = text_styles.concatStylesToMultiLine(tooltipBody, exchangePart)
    compensationText = ''
    if rewardingComplete and compensation > 0 and exchange > 0:
        if awardType is not None:
            compensationText = text_styles.mainBig(backport.text(R.strings.ranked_battles.rewardsView.tabs.year.compensation.extraPoints(), points=text_styles.highlightText(compensation), rankedImg=icons.makeImageTag(backport.image(R.images.gui.maps.icons.rankedBattles.ranked_point_16x16()), 16, 16, -3), crystal=text_styles.highlightText(compensation * exchange), crystalImg=icons.crystal()))
        else:
            compensationText = text_styles.mainBig(backport.text(R.strings.ranked_battles.rewardsView.tabs.year.compensation.notEnough(), crystal=text_styles.highlightText(compensation * exchange), crystalImg=icons.crystal()))
    return {'title': title,
     'titleIcon': backport.image(R.images.gui.maps.icons.rankedBattles.ranked_point_28x28()),
     'titleTooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattleView.rewardsView.tabs.year.scorePoint.header()), body=tooltipBody),
     'compensation': compensationText,
     'points': points,
     'rewards': awards}
