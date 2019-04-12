# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/season_comple_vos.py
import BigWorld
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES

def getFinishSeasonData(efficiencyValue, season):
    return {'typeTitle': backport.text(R.strings.ranked_battles.seasonComplete.smallTitle()),
     'typeIcon': backport.image(R.images.gui.maps.icons.battleTypes.c_40x40.ranked()),
     'seasonTitle': backport.text(R.strings.ranked_battles.seasonComplete.bigTitle(), season=str(season.getNumber())),
     'effectValue': BigWorld.wg_getIntegralFormat(efficiencyValue),
     'effectLabel': backport.text(R.strings.ranked_battles.seasonComplete.effectLabel()),
     'placeLabel': backport.text(R.strings.ranked_battles.seasonComplete.placeInRating()),
     'btnLabel': backport.text(R.strings.ranked_battles.seasonComplete.leadersButton()),
     'bgSource': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main())}


def getFinishInLeagueData(league, position):
    return {'mainImage': backport.image(R.images.gui.maps.icons.rankedBattles.league.c_300x300.num(league)()),
     'state': RANKEDBATTLES_ALIASES.SEASON_COMPLETE_VIEW_LEAGUE_STATE,
     'placeValue': position,
     'descr': ''}


def getFinishInDivisionsData(rankID):
    return {'mainImage': backport.image(R.images.gui.maps.icons.rankedBattles.ranks.c_190x260.num(rankID)()),
     'state': RANKEDBATTLES_ALIASES.SEASON_COMPLETE_VIEW_DIVISION_STATE,
     'placeValue': '',
     'descr': backport.text(R.strings.ranked_battles.seasonComplete.bestRank())}


def getRewardData(awards):
    return {'ribbonType': 'ribbon2',
     'rendererLinkage': 'RibbonAwardAnimUI',
     'gap': 20,
     'rendererWidth': 80,
     'rendererHeight': 80,
     'awards': awards}
