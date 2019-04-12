# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/rewards_vos.py
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles

def getDivisionVO(division):
    return {'id': division.getUserID(),
     'name': text_styles.promoTitle(division.getUserName()),
     'isCompleted': division.isCompleted(),
     'isLocked': not division.isUnlocked(),
     'isCurrent': division.isCurrent()}


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


def getLeagueRewardVO(leagueID, styleBonus, isCurrent):
    return {'leagueID': leagueID,
     'title': backport.text(R.strings.ranked_battles.rewardsView.tabs.leagues.dyn('league%s' % leagueID)()),
     'description': backport.text(R.strings.ranked_battles.rewardsView.tabs.leagues.awardDescr()),
     'isCurrent': isCurrent,
     'isSpecial': styleBonus.isSpecial,
     'specialAlias': styleBonus.specialAlias,
     'specialArgs': styleBonus.specialArgs}
