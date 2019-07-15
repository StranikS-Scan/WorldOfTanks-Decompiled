# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/season_comple_vos.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_helpers.league_provider import TOP_LEAGUE_ID
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.shared.formatters import text_styles, icons

def getFinishSeasonData(efficiencyValue, seasonNumber):
    return {'typeTitle': backport.text(R.strings.ranked_battles.seasonComplete.smallTitle()),
     'typeIcon': backport.image(R.images.gui.maps.icons.battleTypes.c_40x40.ranked()),
     'seasonTitle': backport.text(R.strings.ranked_battles.seasonComplete.bigTitle(), season=str(seasonNumber)),
     'effectValue': backport.getIntegralFormat(efficiencyValue),
     'effectLabel': backport.text(R.strings.ranked_battles.seasonComplete.effectLabel()),
     'btnLabel': backport.text(R.strings.ranked_battles.seasonComplete.leadersButton()),
     'bgSource': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main())}


def getFinishInLeagueData(league, position, seasonNumber, isSprinter):
    header = backport.text(R.strings.ranked_battles.rankedBattleMainView.leaguesView.dyn('league{}'.format(league))())
    body = backport.text(R.strings.ranked_battles.seasonComplete.tooltip.body(), season=str(seasonNumber))
    sprinterLabel = ''
    if isSprinter:
        if league == TOP_LEAGUE_ID:
            sprinterLabel = backport.text(R.strings.ranked_battles.seasonComplete.sprinterTop())
        else:
            sprinterLabel = backport.text(R.strings.ranked_battles.seasonComplete.sprinterImproved())
        sprinterLabel = text_styles.concatStylesToSingleLine(icons.makeImageTag(backport.image(R.images.gui.maps.icons.rankedBattles.sprinter_icon()), 32, 17, -3), text_styles.highlightText(sprinterLabel))
    return {'mainImage': backport.image(R.images.gui.maps.icons.rankedBattles.league.c_300x300.num(league)()),
     'state': RANKEDBATTLES_ALIASES.SEASON_COMPLETE_VIEW_LEAGUE_STATE,
     'placeLabel': backport.text(R.strings.ranked_battles.seasonComplete.placeInRating()),
     'placeValue': position,
     'descr': '',
     'sprinterLabel': sprinterLabel,
     'tooltip': makeTooltip(header=header, body=body)}


def getFinishInDivisionsData(division, rankID, seasonNumber):
    divisionID = division.getID()
    divisionName = backport.text(R.strings.ranked_battles.division.dyn(division.getUserID())())
    rankUserID = division.getRankUserName(rankID)
    header = backport.text(R.strings.ranked_battles.seasonComplete.division.tooltip.header(), rank=rankUserID, division=divisionName)
    body = backport.text(R.strings.ranked_battles.seasonComplete.tooltip.body(), season=str(seasonNumber))
    return {'mainImage': backport.image(R.images.gui.maps.icons.rankedBattles.ranks.c_190x260.dyn('rank%s_%s' % (divisionID, rankUserID))()),
     'state': RANKEDBATTLES_ALIASES.SEASON_COMPLETE_VIEW_DIVISION_STATE,
     'placeLabel': backport.text(R.strings.ranked_battles.seasonComplete.outOfRating()),
     'placeValue': '',
     'descr': backport.text(R.strings.ranked_battles.seasonComplete.bestRank()),
     'tooltip': makeTooltip(header=header, body=body)}


def getAwardsData(awards):
    return {'ribbonType': 'ribbon2',
     'rendererLinkage': 'RibbonAwardAnimUI',
     'gap': 20,
     'rendererWidth': 80,
     'rendererHeight': 80,
     'awards': awards}
