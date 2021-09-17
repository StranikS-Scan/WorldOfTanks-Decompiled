# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_helpers/__init__.py
import logging
import typing
from collections import namedtuple
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.constants import RANKED_QUEST_ID_PREFIX, RankedTokenQuestPostfix, LOBBY_SUB_LANDING_PARAM, SEASON_RATING_PARAM
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.shared.utils.functions import makeTooltip
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)
_AlertMessage = namedtuple('_AlertMessage', 'alertType, alertStr, buttonVisible')

def getBonusBattlesLabel(bonusBattlesCount):
    label = ''
    if bonusBattlesCount:
        label = backport.text(R.strings.ranked_battles.rankedBattleMainView.bonusBattles(), battlesCount=bonusBattlesCount)
    return label


def getBonusMultiplierLabel():
    bonusMultiplier = dependency.instance(IRankedBattlesController).getBonusBattlesMultiplier()
    label = ''
    if bonusMultiplier > 0:
        label = backport.text(R.strings.ranked_battles.rankedBattlesWidget.bonusMultiplier(), count=bonusMultiplier)
    return label


def getBonusBattlesIncome(resRoot, stepsCount, efficiencyCount, isStepsDaily):
    forEfficiencyStr = ''
    if efficiencyCount > 0:
        forEfficiencyStr = backport.text(resRoot.efficiency(), amount=text_styles.neutral(efficiencyCount))
    forStepsStr = ''
    stepsKey = 'daily' if isStepsDaily else 'persistent'
    if stepsCount > 0:
        forStepsStr = backport.text(resRoot.steps.dyn(stepsKey)(), amount=text_styles.neutral(stepsCount))
    return text_styles.concatStylesToSingleLine(forEfficiencyStr, forStepsStr) if forEfficiencyStr or forStepsStr else ''


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesSeasonRatingUrl(lobbyContext=None, spaID=None):
    url = lobbyContext.getServerSettings().rankedBattles.seasonRatingPageUrl
    params = SEASON_RATING_PARAM.format(spaID)
    return url + params if spaID is not None else url


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesInfoPageUrl(lobbyContext=None):
    return lobbyContext.getServerSettings().rankedBattles.infoPageUrl


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesIntroPageUrl(lobbyContext=None):
    return lobbyContext.getServerSettings().rankedBattles.introPageUrl


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesSeasonGapUrl(lobbyContext=None):
    return lobbyContext.getServerSettings().rankedBattles.seasonGapPageUrl


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesYearRatingUrl(lobbyContext=None, isLobbySub=False):
    url = lobbyContext.getServerSettings().rankedBattles.yearRatingPageUrl
    params = LOBBY_SUB_LANDING_PARAM + str(isLobbySub).lower()
    return url + params if url is not None else None


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesShopUrl(lobbyContext=None, isLobbySub=False):
    url = lobbyContext.getServerSettings().rankedBattles.shopPageUrl
    params = LOBBY_SUB_LANDING_PARAM + str(isLobbySub).lower()
    return url + params if url is not None else None


def isSeasonTokenQuest(questID):
    return questID.split('_')[-1] in (RankedTokenQuestPostfix.SPRINTER, RankedTokenQuestPostfix.COMMON)


def isFinalTokenQuest(questID):
    return questID.split('_')[-1] == RankedTokenQuestPostfix.FINAL


def isLeaderTokenQuest(questID):
    return questID.split('_')[-1] == RankedTokenQuestPostfix.LEADER


def getDataFromSeasonTokenQuestID(questID):
    seasonID, leagueID, postfix = questID.split('_')[-3:]
    if postfix not in (RankedTokenQuestPostfix.SPRINTER, RankedTokenQuestPostfix.COMMON):
        _logger.error('getDataFromSeasonTokenQuestID usage not for season token quest')
    return (int(seasonID), int(leagueID), postfix == RankedTokenQuestPostfix.SPRINTER)


def getDataFromFinalTokenQuestID(questID):
    points, postfix = questID.split('_')[-2:]
    if postfix != RankedTokenQuestPostfix.FINAL:
        _logger.error('getDataFromFinalTokenQuestID usage only for final token quest')
    return int(points)


def getShieldSizeByRankSize(rankSize):
    return RANKEDBATTLES_ALIASES.WIDGET_HUGE if rankSize in RANKEDBATTLES_ALIASES.SHIELD_HUGE_SIZES else RANKEDBATTLES_ALIASES.WIDGET_MEDIUM


def isRankedQuestID(questID):
    return questID.startswith(RANKED_QUEST_ID_PREFIX)


def makeStatTooltip(statKey):
    header = backport.text(R.strings.tooltips.rankedBattleView.stats.dyn(statKey).header())
    body = backport.text(R.strings.tooltips.rankedBattleView.stats.dyn(statKey).body())
    return makeTooltip(header, body)
