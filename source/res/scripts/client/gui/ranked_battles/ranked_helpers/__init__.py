# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_helpers/__init__.py
import logging
import typing
from collections import namedtuple
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import CalendarStatusVO
from gui.ranked_battles.constants import RANKED_QUEST_ID_PREFIX, PrimeTimeStatus, RankedTokenQuestPostfix, LandingUrlParams, AlertTypes
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.utils.functions import makeTooltip
from gui.shared.formatters import text_styles
from gui.shared.formatters.ranges import toRomanRangeString
from helpers import dependency, time_utils
from skeletons.connection_mgr import IConnectionManager
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


def getAlertStatusVO():
    alertMessage = _getAlertMessage()
    buttonLabelResID = R.strings.ranked_battles.alertMessage.button.moreInfo()
    if alertMessage.alertType == AlertTypes.PRIME:
        buttonLabelResID = R.strings.ranked_battles.alertMessage.button.changeServer()
    return CalendarStatusVO(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if alertMessage.alertType != AlertTypes.SEASON else None, buttonIcon='', buttonLabel=backport.text(buttonLabelResID), buttonVisible=alertMessage.buttonVisible, buttonTooltip=None, statusText=text_styles.vehicleStatusCriticalText(alertMessage.alertStr), popoverAlias=None, bgVisible=True, shadowFilterVisible=alertMessage.alertType != AlertTypes.SEASON, tooltip=TOOLTIPS_CONSTANTS.RANKED_CALENDAR_DAY_INFO if alertMessage.alertType != AlertTypes.VEHICLE else None)


def _getAlertMessage():
    rankedController = dependency.instance(IRankedBattlesController)
    if not rankedController.hasSuitableVehicles():
        minLvl, maxLvl = rankedController.getSuitableVehicleLevels()
        alertStr = backport.text(R.strings.ranked_battles.alertMessage.unsuitableVehicles(), levels=toRomanRangeString(range(minLvl, maxLvl + 1)))
        return _AlertMessage(AlertTypes.VEHICLE, alertStr, True)
    connectionMgr = dependency.instance(IConnectionManager)
    hasAvailableServers = rankedController.hasAvailablePrimeTimeServers()
    hasConfiguredServers = rankedController.hasConfiguredPrimeTimeServers()
    status, _, _ = rankedController.getPrimeTimeStatus()
    if hasAvailableServers:
        if status in (PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN):
            alertStr = backport.text(R.strings.ranked_battles.alertMessage.unsuitablePeriphery(), serverName=connectionMgr.serverUserNameShort)
            return _AlertMessage(AlertTypes.PRIME, alertStr, True)
        alertStr = backport.text(R.strings.ranked_battles.alertMessage.somePeripheriesHalt(), serverName=connectionMgr.serverUserNameShort)
        return _AlertMessage(AlertTypes.PRIME, alertStr, True)
    currSeason = rankedController.getCurrentSeason()
    currTime = time_utils.getCurrentLocalServerTimestamp()
    if currSeason:
        if status in (PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN):
            alertStr = backport.text(R.strings.ranked_battles.alertMessage.unsuitablePeriphery(), serverName=connectionMgr.serverUserNameShort)
            return _AlertMessage(AlertTypes.PRIME, alertStr, hasConfiguredServers)
        timeLeft = rankedController.getTimer()
        timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.ranked_battles.status.timeLeft)
        seasonsChangeTime = currSeason.getEndDate()
        if seasonsChangeTime and currTime + timeLeft >= seasonsChangeTime:
            alertStr = backport.text(R.strings.ranked_battles.alertMessage.seasonFinished(), seasonName=currSeason.getUserName())
            return _AlertMessage(AlertTypes.SEASON, alertStr, False)
        if connectionMgr.isStandalone():
            key = R.strings.ranked_battles.alertMessage.singleModeHalt()
        else:
            key = R.strings.ranked_battles.alertMessage.allPeripheriesHalt()
        alertStr = backport.text(key, time=timeLeftStr)
        return _AlertMessage(AlertTypes.PRIME, alertStr, False)
    _logger.warning('This codepoint should not be reached')
    return _AlertMessage(AlertTypes.SEASON, '', False)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesRatingUrl(lobbyContext=None):
    return lobbyContext.getServerSettings().bwRankedBattles.rblbHostUrl


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesInfoPageUrl(lobbyContext=None):
    return lobbyContext.getServerSettings().bwRankedBattles.infoPageUrl


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesIntroPageUrl(lobbyContext=None):
    return lobbyContext.getServerSettings().bwRankedBattles.introPageUrl


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesSeasonGapUrl(lobbyContext=None):
    return lobbyContext.getServerSettings().bwRankedBattles.seasonGapPageUrl


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesYearRatingUrl(lobbyContext=None, isLobbySub=False):
    url = lobbyContext.getServerSettings().bwRankedBattles.yearRatingPageUrl
    params = LandingUrlParams.LOBBY_SUB if isLobbySub else LandingUrlParams.PAGE_TAB
    return url + params if url is not None else None


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesShopUrl(lobbyContext=None, isLobbySub=False):
    url = lobbyContext.getServerSettings().bwRankedBattles.shopPageUrl
    params = LandingUrlParams.LOBBY_SUB if isLobbySub else LandingUrlParams.PAGE_TAB
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
