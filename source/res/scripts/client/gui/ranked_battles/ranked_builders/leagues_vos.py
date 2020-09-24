# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/leagues_vos.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.ranked_battles import ranked_formatters
from gui.ranked_battles.ranked_builders import shared_vos
from gui.ranked_battles.ranked_builders.shared_vos import getStatVO

def getEfficiencyVO(currentSeasonEfficiency, currentSeasonEfficiencyDiff):
    resultVO = shared_vos.getEfficiencyVO(currentSeasonEfficiency, currentSeasonEfficiencyDiff)
    resultVO['label'] = text_styles.alignText(text_styles.mainBig(backport.text(R.strings.ranked_battles.rankedBattleMainView.stats.seasonEfficiency())), 'center')
    return resultVO


def getLeagueVO(leagueID, isSprinter, isTop, yearLBsize, isYearLBEnabled):
    resShortCut = R.strings.ranked_battles.rankedBattleMainView.leaguesView
    title = backport.text(resShortCut.unavailableTitle())
    desc = backport.text(resShortCut.unavailableDescr())
    topText = ''
    sprinterImg = ''
    if leagueID:
        title = backport.text(resShortCut.dyn('league{}'.format(leagueID))())
        descRes = resShortCut.topDescr() if isTop else resShortCut.descr()
        desc = backport.text(descRes, count=yearLBsize)
        sprinterImg = backport.image(R.images.gui.maps.icons.rankedBattles.sprinter_icon()) if isSprinter else ''
        topText = backport.text(resShortCut.top(), count=yearLBsize) if isTop else ''
    if not isYearLBEnabled:
        desc = backport.text(resShortCut.yearLeaderboardDisabled())
    return {'title': title,
     'descr': desc,
     'league': leagueID,
     'sprinterImg': sprinterImg,
     'topText': topText}


def getRatingVO(rating):
    resultVO = shared_vos.getRatingVO(rating)
    resultVO['label'] = text_styles.alignText(text_styles.mainBig(backport.text(R.strings.ranked_battles.rankedBattleMainView.stats.rating.title())), 'center')
    return resultVO


def getStatsVO(amountStepsInLeagues, amountBattlesInLeagues, amountSteps, amountBattles):
    return {'stripesInLeague': getStatVO(ranked_formatters.getIntegerStrStat(amountStepsInLeagues), 'stripesInLeague', 'stripes', 'stripesInLeague'),
     'battlesInLeague': getStatVO(ranked_formatters.getIntegerStrStat(amountBattlesInLeagues), 'battlesInLeague', 'battles', 'battlesInLeague'),
     'stripesTotal': getStatVO(ranked_formatters.getIntegerStrStat(amountSteps), 'stripesTotal', 'stripesTotal', 'stripesTotal'),
     'battlesTotal': getStatVO(ranked_formatters.getIntegerStrStat(amountBattles), 'battlesTotal', 'battlesTotal', 'battlesTotal')}
