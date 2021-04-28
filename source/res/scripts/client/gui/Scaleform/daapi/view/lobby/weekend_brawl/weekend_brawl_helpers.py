# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/weekend_brawl/weekend_brawl_helpers.py
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.periodic_battles.models import CalendarStatusVO
from gui.shared.formatters import text_styles
from helpers import dependency, time_utils
from skeletons.gui.game_control import IWeekendBrawlController
from skeletons.connection_mgr import IConnectionManager
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.utils.functions import makeTooltip

def getPrimeTimeStatusVO(status, hasAvailableServers):
    showPrimeTimeAlert = status != PrimeTimeStatus.AVAILABLE
    return CalendarStatusVO(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if showPrimeTimeAlert else None, buttonIcon='', buttonLabel=backport.text(R.strings.weekend_brawl.alertMessage.button()), buttonVisible=showPrimeTimeAlert and hasAvailableServers, buttonTooltip=None, statusText=text_styles.vehicleStatusCriticalText(_getPrimeTimeStatusText()), popoverAlias=None, bgVisible=True, shadowFilterVisible=showPrimeTimeAlert, tooltip=TOOLTIPS_CONSTANTS.WEEKEND_BRAWL_SELECTOR_INFO, isSimpleTooltip=False)


@dependency.replace_none_kwargs(wBrawlCtrl=IWeekendBrawlController, connectionMgr=IConnectionManager)
def _getPrimeTimeStatusText(wBrawlCtrl=None, connectionMgr=None):
    hasAvailableServers = wBrawlCtrl.hasAvailablePrimeTimeServers()
    _, timeLeft, _ = wBrawlCtrl.getPrimeTimeStatus()
    strPath = R.strings.weekend_brawl.alertMessage
    if hasAvailableServers:
        alertStr = backport.text(strPath.somePeripheriesHalt(), serverName=connectionMgr.serverUserNameShort)
    else:
        currSeason = wBrawlCtrl.getCurrentSeason()
        currTime = time_utils.getCurrentLocalServerTimestamp()
        isCycleNow = currSeason and currSeason.hasActiveCycle(currTime) and timeLeft
        if isCycleNow:
            key = strPath.singleModeHalt() if connectionMgr.isStandalone() else strPath.allPeripheriesHalt()
            timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.weekend_brawl.status.timeLeft)
            alertStr = backport.text(key, time=timeLeftStr)
        else:
            alertStr = backport.text(R.strings.weekend_brawl.systemMessage.notAvailable())
    return alertStr


@dependency.replace_none_kwargs(wBrawlCtrl=IWeekendBrawlController)
def getWeekendBrawlFightBtnTooltipData(result, wBrawlCtrl=None):
    state = result.restriction
    hasAvailableServers = wBrawlCtrl.hasAvailablePrimeTimeServers()
    strPath = R.strings.weekend_brawl.headerButtons.fightBtn.tooltip
    if state == PRE_QUEUE_RESTRICTION.MODE_DISABLED:
        header = backport.text(strPath.disabled.header())
        if hasAvailableServers:
            body = backport.text(strPath.currentServerUnavailable.body())
        else:
            body = backport.text(strPath.disabled.body())
    elif state == PRE_QUEUE_RESTRICTION.LIMIT_LEVEL:
        header = backport.text(strPath.vehLevelRequired.header())
        body = backport.text(strPath.vehLevelRequired.body(), level=toRomanRangeString(result.ctx['levels'], 1))
    else:
        return ''
    return makeTooltip(header, body)
