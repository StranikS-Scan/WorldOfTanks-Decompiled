# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/postbattle_awards_vos.py
from collections import namedtuple
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_builders import shared_vos
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.shared.formatters import text_styles
AwardBlock = namedtuple('AwardBlock', 'rankID, awards')

def getVOsSequence(awardBlocks, ranks):
    result = []
    awardBlocks.sort(key=lambda x: x.rankID)
    for awardBlock in awardBlocks:
        rank = ranks[awardBlock.rankID]
        result.append(_getRankCongVO(awardBlock, rank))
        if rank.isInitialForNextDivision():
            result.append(_getDivisionCongVO(awardBlock, ranks))
        if rank.isFinal():
            result.append(_getLeagueCongVO())

    return result


def _getRankCongVO(awardBlock, rank):
    return _getBlockVO(RANKEDBATTLES_ALIASES.AWARD_VIEW_RANK_STATE, backport.text(R.strings.ranked_battles.awards.gotRank()), rankVO=shared_vos.buildRankVO(rank=rank, imageSize=RANKEDBATTLES_ALIASES.WIDGET_HUGE, isEnabled=True, shieldStatus=rank.getShieldStatus()), awards=awardBlock.awards)


def _getDivisionCongVO(awardBlock, ranks):
    division = ranks[awardBlock.rankID].getDivision()
    newDivision = ranks[awardBlock.rankID + 1].getDivision()
    return _getBlockVO(RANKEDBATTLES_ALIASES.AWARD_VIEW_DIVISION_STATE, backport.text(R.strings.ranked_battles.awards.gotDivision()), divisionVO=_getDivisionVO(division, newDivision))


def _getLeagueCongVO():
    return _getBlockVO(RANKEDBATTLES_ALIASES.AWARD_VIEW_LEAGUE_STATE, backport.text(R.strings.ranked_battles.awards.gotLeague()))


def _getDivisionVO(division, newDivision):
    return {'division': division.getID(),
     'divisionName': text_styles.middleTitle(backport.text(R.strings.ranked_battles.division.dyn(division.getUserID())())),
     'newDivision': newDivision.getID(),
     'newDivisionName': text_styles.middleTitle(backport.text(R.strings.ranked_battles.division.dyn(newDivision.getUserID())()))}


def _getBlockVO(state, subTitle='', rankVO=None, divisionVO=None, awards=None):
    return {'state': state,
     'subTitle': subTitle,
     'rankVO': rankVO,
     'divisionVO': divisionVO,
     'awards': awards}
