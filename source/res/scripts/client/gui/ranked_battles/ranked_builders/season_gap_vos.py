# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/season_gap_vos.py
import logging
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.ranked_battles.ranked_builders import shared_vos
from gui.ranked_battles import ranked_formatters
from gui.ranked_battles.constants import SeasonGapStates, ZERO_RANK_ID, ZERO_DIVISION_ID
from gui.ranked_battles.ranked_helpers.league_provider import UNDEFINED_LEAGUE_ID
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
if typing.TYPE_CHECKING:
    from gui.ranked_battles.ranked_models import Division
_logger = logging.getLogger(__name__)

def _buildWaitingVO(state, rankID, division, leagueID):
    return _getDataVO(RANKEDBATTLES_ALIASES.SEASON_GAP_VIEW_LEAGUE_STATE, disabled=True, title=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.waitingLeague.title()), descr=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.waitingLeague.descr()))


def _buildLeaguesVO(state, rankID, division, leagueID):
    return _getDataVO(RANKEDBATTLES_ALIASES.SEASON_GAP_VIEW_LEAGUE_STATE, leagueID=leagueID, title=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.dyn('league{}'.format(leagueID))()), descr=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.league.descr()), btnLabel=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.league.ratingBtn()), btnVisible=True)


def _buildDivisionVO(state, rankID, division, leagueID):
    description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.division.descr())
    buttonLabel = ''
    buttonVisible = False
    if state != SeasonGapStates.WAITING_IN_DIVISIONS:
        buttonLabel = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.division.ratingBtn())
        buttonVisible = True
    if state == SeasonGapStates.BANNED_IN_LEAGUES:
        description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.bannedLeague.descr())
        description = _addAlertIcon(description)
    elif state == SeasonGapStates.BANNED_IN_DIVISIONS:
        description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.bannedDivision.descr())
        description = _addAlertIcon(description)
    return _getDataVO(RANKEDBATTLES_ALIASES.SEASON_GAP_VIEW_DIVISION_STATE, divisionID=division.getID(), rankID=division.getRankIdInDivision(rankID), title=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.division.title(), rank=division.getRankUserName(rankID), division=division.getUserName()), descr=description, btnLabel=buttonLabel, btnVisible=buttonVisible)


def _buildNotInSeasonVO(state, rankID, division, leagueID):
    description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.notInSeason.descr())
    buttonLabel = ''
    buttonVisible = False
    if state != SeasonGapStates.WAITING_NOT_IN_SEASON:
        buttonLabel = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.division.ratingBtn())
        buttonVisible = True
    if state == SeasonGapStates.BANNED_NOT_IN_SEASON:
        description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.bannedNotInSeason.descr())
        description = _addAlertIcon(description)
    return _getDataVO(RANKEDBATTLES_ALIASES.SEASON_GAP_VIEW_DIVISION_STATE, divisionID=division.getID(), disabled=True, title=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.notInSeason.title()), descr=description, btnLabel=buttonLabel, btnVisible=buttonVisible)


_DATA_VOS_BUILDERS = {SeasonGapStates.WAITING_IN_LEAGUES: _buildWaitingVO,
 SeasonGapStates.WAITING_IN_DIVISIONS: _buildDivisionVO,
 SeasonGapStates.WAITING_NOT_IN_SEASON: _buildNotInSeasonVO,
 SeasonGapStates.IN_LEAGUES: _buildLeaguesVO,
 SeasonGapStates.IN_DIVISIONS: _buildDivisionVO,
 SeasonGapStates.NOT_IN_SEASON: _buildNotInSeasonVO,
 SeasonGapStates.BANNED_IN_LEAGUES: _buildDivisionVO,
 SeasonGapStates.BANNED_IN_DIVISIONS: _buildDivisionVO,
 SeasonGapStates.BANNED_NOT_IN_SEASON: _buildNotInSeasonVO}

def getDataVO(state, rankID, division, leagueID):
    builder = _DATA_VOS_BUILDERS.get(state)
    if builder is not None:
        return builder(state, rankID, division, leagueID)
    else:
        _logger.error('Can not find builder for state = %s', state)
        return _getDataVO(RANKEDBATTLES_ALIASES.SEASON_GAP_VIEW_DIVISION_STATE)


def getEfficiencyVO(currentSeasonEfficiency):
    return {'icon': 'efficiency',
     'label': text_styles.alignText(text_styles.mainBig(backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.stats.efficiency())), 'center'),
     'value': ranked_formatters.getFloatPercentStrStat(currentSeasonEfficiency)}


def getRatingVO(rating, isMastered):
    resultVO = shared_vos.getRatingVO(rating)
    label = backport.text(R.strings.ranked_battles.rankedBattleMainView.stats.rating.title())
    value = resultVO['value']
    if not isMastered:
        label = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.stats.outOfRating())
        value = ' '
    resultVO['label'] = text_styles.alignText(text_styles.mainBig(label), 'center')
    resultVO['value'] = value
    return resultVO


def _getDataVO(state, leagueID=UNDEFINED_LEAGUE_ID, divisionID=ZERO_DIVISION_ID, rankID=ZERO_RANK_ID, disabled=False, title='', descr='', btnLabel='', btnVisible=False):
    if rankID == ZERO_RANK_ID:
        rankID += 1
    return {'state': state,
     'leagueID': leagueID,
     'divisionImgSmall': backport.image(R.images.gui.maps.icons.rankedBattles.ranks.c_114x160.dyn('rank%s_%s' % (divisionID, rankID))()),
     'divisionImgBig': backport.image(R.images.gui.maps.icons.rankedBattles.ranks.c_190x260.dyn('rank%s_%s' % (divisionID, rankID))()),
     'disabled': disabled,
     'title': title,
     'descr': descr,
     'btnLabel': btnLabel,
     'btnVisible': btnVisible}


def _addAlertIcon(description):
    return text_styles.concatStylesToSingleLine(icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.alertIcon1()), 23, 23, -6), description)
