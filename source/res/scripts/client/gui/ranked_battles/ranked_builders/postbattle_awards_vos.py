# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/postbattle_awards_vos.py
import typing
from collections import namedtuple
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_builders import shared_vos
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.shared.formatters import text_styles
if typing.TYPE_CHECKING:
    from gui.ranked_battles.ranked_models import Rank, PostBattleRankInfo
AwardBlock = namedtuple('AwardBlock', 'rankID, awards')

def getVOsSequence(awardBlocks, ranks, rankedInfo):
    result = []
    awardBlocks.sort(key=lambda x: x.rankID)
    for awardBlock in awardBlocks:
        rank = ranks[awardBlock.rankID]
        result.append(_getRankCongVO(awardBlock, rank))
        if rank.isInitialForNextDivision():
            result.append(_getDivisionCongVO(awardBlock, ranks, rankedInfo))
        if rank.isFinal():
            result.append(_getLeagueCongVO(rankedInfo))

    return result


def _getRankCongVO(awardBlock, rank):
    return _getBlockVO(RANKEDBATTLES_ALIASES.AWARD_VIEW_RANK_STATE, backport.text(R.strings.ranked_battles.awards.gotRank()), rankVO=shared_vos.buildRankVO(rank=rank, imageSize=RANKEDBATTLES_ALIASES.WIDGET_HUGE, isEnabled=True, shieldStatus=rank.getShieldStatus()), awards=awardBlock.awards)


def _getDivisionCongVO(awardBlock, ranks, rankedInfo):
    division = ranks[awardBlock.rankID].getDivision()
    newDivision = ranks[awardBlock.rankID + 1].getDivision()
    return _getBlockVO(RANKEDBATTLES_ALIASES.AWARD_VIEW_DIVISION_STATE, backport.text(R.strings.ranked_battles.awards.gotDivision()), divisionVO=_getDivisionVO(division, newDivision, rankedInfo.additionalBonusBattles))


def _getLeagueCongVO(rankedInfo):
    return _getBlockVO(RANKEDBATTLES_ALIASES.AWARD_VIEW_LEAGUE_STATE, backport.text(R.strings.ranked_battles.awards.gotLeague()), leagueVO=_getLeagueVO(rankedInfo.additionalBonusBattles))


def _getDivisionVO(division, newDivision, bonusBattlesDiff):
    return {'division': division.getID(),
     'divisionName': text_styles.middleTitle(backport.text(R.strings.ranked_battles.division.dyn(division.getUserID())())),
     'newDivision': newDivision.getID(),
     'newDivisionName': text_styles.middleTitle(backport.text(R.strings.ranked_battles.division.dyn(newDivision.getUserID())())),
     'additionalBonusBattles': _getBonusBattlesDiffLabel(bonusBattlesDiff)}


def _getLeagueVO(bonusBattlesDiff):
    return {'additionalBonusBattles': _getBonusBattlesDiffLabel(bonusBattlesDiff)}


def _getBonusBattlesDiffLabel(bonusBattlesDiff):
    label = ''
    if bonusBattlesDiff > 0:
        label = text_styles.highlightText(backport.text(R.strings.ranked_battles.awards.additionalBonusBattles(), count=bonusBattlesDiff))
    return label


def _getBlockVO(state, subTitle='', rankVO=None, divisionVO=None, leagueVO=None, awards=None):
    return {'state': state,
     'subTitle': subTitle,
     'rankVO': rankVO,
     'divisionVO': divisionVO,
     'leagueVO': leagueVO,
     'awards': awards}
