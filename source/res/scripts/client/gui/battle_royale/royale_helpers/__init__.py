# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_royale/royale_helpers/__init__.py
from collections import namedtuple
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import CalendarStatusVO
from gui.battle_royale import constants
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers import time_utils
from shared_utils import CONST_CONTAINER
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext

class PrimeTimeStatus(CONST_CONTAINER):
    DISABLED = 0
    NOT_SET = 1
    FROZEN = 2
    NO_SEASON = 3
    NOT_AVAILABLE = 4
    AVAILABLE = 5


_AlertMessage = namedtuple('_AlertMessage', 'isPrimeAlert, alertStr, buttonVisible')

def makeStatTooltip(statKey, **kwargs):
    header = backport.text(R.strings.tooltips.battle_royale.progressPage.stats.dyn(statKey).header(), **kwargs)
    body = backport.text(R.strings.tooltips.battle_royale.progressPage.stats.dyn(statKey).body(), **kwargs)
    return makeTooltip(header, body)


def getAlertStatusVO():
    alertMessage = _getAlertMessage()
    return CalendarStatusVO(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if alertMessage.isPrimeAlert else None, buttonIcon='', buttonLabel=backport.text(R.strings.battle_royale.alertMessage.button()), buttonVisible=alertMessage.buttonVisible, buttonTooltip=None, statusText=text_styles.vehicleStatusCriticalText(alertMessage.alertStr), popoverAlias=None, bgVisible=True, shadowFilterVisible=alertMessage.isPrimeAlert, tooltip=TOOLTIPS_CONSTANTS.BATTLE_ROYALE_PRIME_TIMES)


def _getAlertMessage():
    battleRoyale = dependency.instance(IBattleRoyaleController)
    connectionMgr = dependency.instance(IConnectionManager)
    hasAvailableServers = battleRoyale.hasAvailablePrimeTimeServers()
    hasConfiguredServers = battleRoyale.hasConfiguredPrimeTimeServers()
    status, _, _ = battleRoyale.getPrimeTimeStatus()
    if hasAvailableServers:
        if status in (PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN):
            alertStr = backport.text(R.strings.battle_royale.alertMessage.unsuitablePeriphery())
            return _AlertMessage(False, alertStr, True)
        alertStr = backport.text(R.strings.battle_royale.alertMessage.somePeripheriesHalt(), serverName=connectionMgr.serverUserNameShort)
        return _AlertMessage(True, alertStr, True)
    else:
        currSeason = battleRoyale.getCurrentSeason()
        currTime = time_utils.getCurrentLocalServerTimestamp()
        if currSeason:
            if status in (PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN):
                if hasConfiguredServers:
                    alertStr = backport.text(R.strings.battle_royale.alertMessage.unsuitablePeriphery())
                    return _AlertMessage(False, alertStr, True)
                alertStr = backport.text(R.strings.battle_royale.primeTime.status.allServersDisabled())
                return _AlertMessage(True, alertStr, False)
            timeLeft = battleRoyale.getTimer()
            timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.battle_royale.tooltips.timeLeft)
            seasonsChangeTime = currSeason.getEndDate()
            if seasonsChangeTime and currTime + timeLeft >= seasonsChangeTime:
                alertStr = backport.text(R.strings.battle_royale.alertMessage.seasonAlmostFinished(), time=timeLeftStr)
                return _AlertMessage(False, alertStr, False)
            if connectionMgr.isStandalone():
                key = R.strings.battle_royale.alertMessage.singleModeHalt()
            else:
                key = R.strings.battle_royale.alertMessage.allPeripheriesHalt()
            alertStr = backport.text(key, time=timeLeftStr)
            return _AlertMessage(True, alertStr, False)
        alertStr = backport.text(R.strings.battle_royale.alertMessage.seasonFinished())
        if battleRoyale.getPreviousSeason() is None:
            timeLeft = battleRoyale.getTimer()
            timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.battle_royale.tooltips.timeLeft)
            alertStr = backport.text(R.strings.battle_royale.alertMessage.seasonIsComing(), time=timeLeftStr)
        return _AlertMessage(False, alertStr, False)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getBattleRoyaleIntroPageUrl(lobbyContext=None):
    return lobbyContext.getServerSettings().battleRoyale.introVideoUrl


def isBRVehiclesInvoiceQuestComplete(questIDs):
    for qID in questIDs:
        if qID.startswith(constants.BATTLE_ROYALE_VEHICLES_INVOICE):
            return True

    return False


def isBRQuestID(questID):
    return questID.startswith(constants.BR_QUEST_ID_PREFIX)
