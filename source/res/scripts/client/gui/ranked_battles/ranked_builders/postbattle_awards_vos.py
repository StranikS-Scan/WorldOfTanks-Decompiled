# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/postbattle_awards_vos.py
import typing
from collections import namedtuple
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_builders import shared_vos
from gui.ranked_battles.ranked_helpers import getBonusBattlesIncome
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
if typing.TYPE_CHECKING:
    from gui.ranked_battles.ranked_models import Rank, PostBattleRankInfo
AwardBlock = namedtuple('AwardBlock', 'rankID, awards')

def getVOsSequence(awardBlocks, ranks, rankedInfo):
    result = []
    awardBlocks.sort(key=lambda x: x.rankID)
    for awardBlock in awardBlocks:
        rank = ranks[awardBlock.rankID]
        if rank.isQualification():
            result.append(_getQualificationCongVO(awardBlock, ranks, rankedInfo))
        result.append(_getRankCongVO(awardBlock, rank))
        if rank.isInitialForNextDivision():
            result.append(_getDivisionCongVO(awardBlock, ranks, rankedInfo))
        if rank.isFinal():
            result.append(_getLeagueCongVO(rankedInfo))

    return result


def _getRankCongVO(awardBlock, rank):
    return _getBlockVO(RANKEDBATTLES_ALIASES.AWARD_VIEW_RANK_STATE, backport.text(R.strings.ranked_battles.awards.gotRank()), rankVO=shared_vos.buildRankVO(rank=rank, imageSize=RANKEDBATTLES_ALIASES.WIDGET_HUGE, isEnabled=True), awards=awardBlock.awards)


def _getQualificationCongVO(awardBlock, ranks, rankedInfo):
    division = ranks[awardBlock.rankID].getDivision()
    newDivision = ranks[awardBlock.rankID + 1].getDivision()
    return _getBlockVO(RANKEDBATTLES_ALIASES.AWARD_VIEW_QUAL_STATE, backport.text(R.strings.ranked_battles.awards.gotQualification()), qualificationVO=_getQualificationVO(division, newDivision), awards=awardBlock.awards, **_getBonusBattleFields(rankedInfo.stepsBonusBattles, rankedInfo.efficiencyBonusBattles, False))


def _getDivisionCongVO(awardBlock, ranks, rankedInfo):
    division = ranks[awardBlock.rankID].getDivision()
    newDivision = ranks[awardBlock.rankID + 1].getDivision()
    return _getBlockVO(RANKEDBATTLES_ALIASES.AWARD_VIEW_DIVISION_STATE, backport.text(R.strings.ranked_battles.awards.gotDivision()), divisionVO=_getDivisionVO(division, newDivision), **_getBonusBattleFields(rankedInfo.stepsBonusBattles, rankedInfo.efficiencyBonusBattles, False))


def _getLeagueCongVO(rankedInfo):
    return _getBlockVO(RANKEDBATTLES_ALIASES.AWARD_VIEW_LEAGUE_STATE, backport.text(R.strings.ranked_battles.awards.gotLeague()), **_getBonusBattleFields(rankedInfo.stepsBonusBattles, rankedInfo.efficiencyBonusBattles, True))


def _getQualificationVO(division, newDivision):
    return {'division': division.getID(),
     'newDivision': newDivision.getID()}


def _getDivisionVO(division, newDivision):
    return {'division': division.getID(),
     'divisionName': text_styles.middleTitle(backport.text(R.strings.ranked_battles.division.dyn(division.getUserID())())),
     'newDivision': newDivision.getID(),
     'newDivisionName': text_styles.middleTitle(backport.text(R.strings.ranked_battles.division.dyn(newDivision.getUserID())()))}


def _getBonusBattleFields(stepsBonus, efficiencyBonus, isDaily):
    return {'bonusBattleText': _getBonusBattlesDiffLabel(stepsBonus + efficiencyBonus),
     'bonusBattleTooltip': _getBonusBattlesTooltip(stepsBonus, efficiencyBonus, isDaily)}


def _getBonusBattlesDiffLabel(bonusBattlesDiff):
    return text_styles.concatStylesWithSpace(text_styles.highlightText(backport.text(R.strings.ranked_battles.awards.bonusBattles.label(), count=bonusBattlesDiff)), icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.attentionIcon1()), vSpace=-2))


def _getBonusBattlesTooltip(stepsBonus, efficiencyBonus, isDaily):
    header = text_styles.middleTitle(backport.text(R.strings.ranked_battles.awards.bonusBattles.header()))
    rankedBonusBattlesString = getBonusBattlesIncome(R.strings.ranked_battles.awards.bonusBattles, stepsBonus, efficiencyBonus, isDaily)
    return makeTooltip(header, text_styles.main(rankedBonusBattlesString))


def _getBlockVO(state, subTitle='', rankVO=None, qualificationVO=None, divisionVO=None, awards=None, bonusBattleText='', bonusBattleTooltip=''):
    return {'state': state,
     'subTitle': subTitle,
     'rankVO': rankVO,
     'qualVO': qualificationVO,
     'divisionVO': divisionVO,
     'awards': awards,
     'bonusBattleText': bonusBattleText,
     'bonusBattleTooltip': bonusBattleTooltip}
