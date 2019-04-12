# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_helpers/__init__.py
import logging
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import CalendarStatusVO
from gui.ranked_battles.constants import RANKED_QUEST_ID_PREFIX, PRIME_TIME_STATUS
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.utils.functions import makeTooltip
from gui.shared.formatters import text_styles
from helpers import dependency, time_utils
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

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


def getPrimeTimeStatusText():
    ranked = dependency.instance(IRankedBattlesController)
    connectionMgr = dependency.instance(IConnectionManager)
    hasAvailableServers = ranked.hasAvailablePrimeTimeServers()
    _, timeLeft, _ = ranked.getPrimeTimeStatus()
    if hasAvailableServers:
        alertStr = backport.text(R.strings.ranked_battles.alertMessage.somePeripheriesHalt(), serverName=connectionMgr.serverUserNameShort)
    else:
        currSeason = ranked.getCurrentSeason()
        currTime = time_utils.getCurrentLocalServerTimestamp()
        isCycleNow = currSeason and currSeason.hasActiveCycle(currTime)
        if isCycleNow:
            if connectionMgr.isStandalone():
                key = R.strings.ranked_battles.alertMessage.singleModeHalt()
            else:
                key = R.strings.ranked_battles.alertMessage.allPeripheriesHalt()
            timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.ranked_battles.status.timeLeft)
            alertStr = backport.text(key, time=timeLeftStr)
        else:
            alertStr = backport.text(R.strings.ranked_battles.alertMessage.seasonFinished())
    return alertStr


def getPrimeTimeStatusVO(status, hasAvailableServers):
    showPrimeTimeAlert = status != PRIME_TIME_STATUS.AVAILABLE
    return CalendarStatusVO(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if showPrimeTimeAlert else None, buttonIcon='', buttonLabel=backport.text(R.strings.ranked_battles.alertMessage.button()), buttonVisible=showPrimeTimeAlert and hasAvailableServers, buttonTooltip=None, statusText=text_styles.vehicleStatusCriticalText(getPrimeTimeStatusText()), popoverAlias=None, bgVisible=True, shadowFilterVisible=showPrimeTimeAlert, tooltip=TOOLTIPS_CONSTANTS.RANKED_CALENDAR_DAY_INFO)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesUrl(lobbyContext=None):
    return lobbyContext.getServerSettings().bwRankedBattles.rblbHostUrl


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesInfoPageUrl(lobbyContext=None):
    return lobbyContext.getServerSettings().bwRankedBattles.infoPageUrl


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesIntroPageUrl(lobbyContext=None):
    return lobbyContext.getServerSettings().bwRankedBattles.introPageUrl


def getRankedDataFromTokenQuestID(questID):
    seasonID, league = questID.split('_')[-2:]
    return (int(seasonID), int(league))


def getShieldSizeByRankSize(rankSize):
    return RANKEDBATTLES_ALIASES.WIDGET_HUGE if rankSize in RANKEDBATTLES_ALIASES.SHIELD_HUGE_SIZES else RANKEDBATTLES_ALIASES.WIDGET_MEDIUM


def isRankedQuestID(questID):
    return questID.startswith(RANKED_QUEST_ID_PREFIX)


def makeStatTooltip(statKey):
    header = backport.text(R.strings.tooltips.rankedBattleView.stats.dyn(statKey).header())
    body = backport.text(R.strings.tooltips.rankedBattleView.stats.dyn(statKey).body())
    return makeTooltip(header, body)
