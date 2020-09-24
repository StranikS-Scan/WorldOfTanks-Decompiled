# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/season_gap_vos.py
from collections import namedtuple
import logging
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.ranked_battles.ranked_builders import shared_vos
from gui.ranked_battles import ranked_formatters
from gui.ranked_battles.constants import SeasonGapStates, ZERO_RANK_ID, ZERO_DIVISION_ID
from gui.ranked_battles.ranked_helpers.web_season_provider import UNDEFINED_LEAGUE_ID
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
_logger = logging.getLogger(__name__)
StateBlock = namedtuple('StateBlock', 'state, rankID, division, leagueID, isSprinter, isYearRewardEnabled')

def _buildWaitingVO(_):
    return _getDataVO(RANKEDBATTLES_ALIASES.SEASON_GAP_VIEW_LEAGUE_STATE, disabled=True, title=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.waitingLeague.title()), descr=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.waitingLeague.descr()))


def _buildLeaguesVO(stateBlock):
    sprinterImg = ''
    if stateBlock.isSprinter:
        sprinterImg = backport.image(R.images.gui.maps.icons.rankedBattles.sprinter_icon())
    return _getDataVO(RANKEDBATTLES_ALIASES.SEASON_GAP_VIEW_LEAGUE_STATE, leagueID=stateBlock.leagueID, title=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.dyn('league{}'.format(stateBlock.leagueID))()), descr=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.league.descr()), btnLabel=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.league.ratingBtn()), btnVisible=True, sprinterImg=sprinterImg)


def _buildDivisionVO(stateBlock):
    description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.division.descr())
    buttonLabel = ''
    buttonVisible = False
    if stateBlock.state != SeasonGapStates.WAITING_IN_DIVISIONS:
        buttonLabel = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.division.ratingBtn())
        buttonVisible = True
    if stateBlock.state == SeasonGapStates.BANNED_IN_LEAGUES:
        bannedLeague = R.strings.ranked_battles.rankedBattleMainView.seasonGap.bannedLeague
        description = bannedLeague.descr() if stateBlock.isYearRewardEnabled else bannedLeague.withoutPoints.descr()
        description = backport.text(description)
        description = _addAlertIcon(description)
    elif stateBlock.state == SeasonGapStates.ROLLED_IN_LEAGUES:
        description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.rolledLeague.descr())
        description = _addAlertIcon(description)
    elif stateBlock.state == SeasonGapStates.BANNED_IN_DIVISIONS:
        description = ''
        if stateBlock.isYearRewardEnabled:
            description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.bannedDivision.descr())
            description = _addAlertIcon(description)
    elif stateBlock.state == SeasonGapStates.ROLLED_IN_DIVISIONS:
        description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.rolledDivision.descr())
        description = _addAlertIcon(description)
    return _getDataVO(RANKEDBATTLES_ALIASES.SEASON_GAP_VIEW_DIVISION_STATE, divisionID=stateBlock.division.getID(), rankID=stateBlock.division.getRankUserId(stateBlock.rankID), title=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.division.title(), rank=stateBlock.division.getRankUserName(stateBlock.rankID), division=stateBlock.division.getUserName()), descr=description, btnLabel=buttonLabel, btnVisible=buttonVisible)


def _buildNotInSeasonVO(stateBlock):
    description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.notInSeason.descr())
    buttonLabel = ''
    buttonVisible = False
    if stateBlock.state != SeasonGapStates.WAITING_NOT_IN_SEASON:
        buttonLabel = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.division.ratingBtn())
        buttonVisible = True
    if stateBlock.state == SeasonGapStates.BANNED_NOT_IN_SEASON:
        description = ''
        if stateBlock.isYearRewardEnabled:
            description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.bannedNotInSeason.descr())
            description = _addAlertIcon(description)
    elif stateBlock.state == SeasonGapStates.ROLLED_NOT_IN_SEASON:
        description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.rolledNotInSeason.descr())
        description = _addAlertIcon(description)
    return _getDataVO(RANKEDBATTLES_ALIASES.SEASON_GAP_VIEW_DIVISION_STATE, disabled=True, title=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.notInSeason.title()), descr=description, btnLabel=buttonLabel, btnVisible=buttonVisible)


def _buildQualificationVO(stateBlock):
    description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.notInDivisions.descr())
    buttonLabel = ''
    buttonVisible = False
    if stateBlock.state != SeasonGapStates.WAITING_NOT_IN_DIVISIONS:
        buttonLabel = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.division.ratingBtn())
        buttonVisible = True
    if stateBlock.state == SeasonGapStates.BANNED_NOT_IN_DIVISIONS:
        description = ''
        if stateBlock.isYearRewardEnabled:
            description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.bannedNotInDivisions.descr())
            description = _addAlertIcon(description)
    elif stateBlock.state == SeasonGapStates.ROLLED_NOT_IN_DIVISIONS:
        description = backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.rolledNotInDivisions.descr())
        description = _addAlertIcon(description)
    return _getDataVO(RANKEDBATTLES_ALIASES.SEASON_GAP_VIEW_DIVISION_STATE, disabled=False, title=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonGap.notInDivisions.title()), descr=description, btnLabel=buttonLabel, btnVisible=buttonVisible)


_DATA_VOS_BUILDERS = {SeasonGapStates.WAITING_IN_LEAGUES: _buildWaitingVO,
 SeasonGapStates.WAITING_IN_DIVISIONS: _buildDivisionVO,
 SeasonGapStates.WAITING_NOT_IN_SEASON: _buildNotInSeasonVO,
 SeasonGapStates.WAITING_NOT_IN_DIVISIONS: _buildQualificationVO,
 SeasonGapStates.IN_LEAGUES: _buildLeaguesVO,
 SeasonGapStates.IN_DIVISIONS: _buildDivisionVO,
 SeasonGapStates.NOT_IN_DIVISIONS: _buildQualificationVO,
 SeasonGapStates.NOT_IN_SEASON: _buildNotInSeasonVO,
 SeasonGapStates.BANNED_IN_LEAGUES: _buildDivisionVO,
 SeasonGapStates.BANNED_IN_DIVISIONS: _buildDivisionVO,
 SeasonGapStates.BANNED_NOT_IN_SEASON: _buildNotInSeasonVO,
 SeasonGapStates.BANNED_NOT_IN_DIVISIONS: _buildQualificationVO,
 SeasonGapStates.ROLLED_IN_LEAGUES: _buildDivisionVO,
 SeasonGapStates.ROLLED_IN_DIVISIONS: _buildDivisionVO,
 SeasonGapStates.ROLLED_NOT_IN_SEASON: _buildNotInSeasonVO,
 SeasonGapStates.ROLLED_NOT_IN_DIVISIONS: _buildQualificationVO}

def getDataVO(stateBlock):
    builder = _DATA_VOS_BUILDERS.get(stateBlock.state)
    if builder is not None:
        return builder(stateBlock)
    else:
        _logger.error('Can not find builder for state = %s', stateBlock.state)
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


def _getDataVO(state, leagueID=UNDEFINED_LEAGUE_ID, divisionID=ZERO_DIVISION_ID, rankID=ZERO_RANK_ID, disabled=False, title='', descr='', btnLabel='', btnVisible=False, sprinterImg=''):
    if rankID in (ZERO_RANK_ID, ZERO_RANK_ID + 1) and divisionID == ZERO_DIVISION_ID:
        smallImage = backport.image(R.images.gui.maps.icons.rankedBattles.divisions.c_114x160.c_0())
        bigImage = backport.image(R.images.gui.maps.icons.rankedBattles.divisions.c_190x260.c_0())
    else:
        smallImage = backport.image(R.images.gui.maps.icons.rankedBattles.ranks.c_114x160.dyn('rank{}_{}'.format(divisionID, rankID))())
        bigImage = backport.image(R.images.gui.maps.icons.rankedBattles.ranks.c_190x260.dyn('rank{}_{}'.format(divisionID, rankID))())
    return {'state': state,
     'leagueID': leagueID,
     'divisionImgSmall': smallImage,
     'divisionImgBig': bigImage,
     'disabled': disabled,
     'title': title,
     'descr': descr,
     'btnLabel': btnLabel,
     'btnVisible': btnVisible,
     'sprinterImg': sprinterImg}


def _addAlertIcon(description):
    return text_styles.concatStylesToSingleLine(icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.alertIcon1()), 23, 23, -6), description)
