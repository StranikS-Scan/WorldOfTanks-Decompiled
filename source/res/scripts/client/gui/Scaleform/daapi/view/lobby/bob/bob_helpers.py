# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/bob/bob_helpers.py
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.periodic_battles.models import CalendarStatusVO
from gui.shared.formatters import text_styles
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBobController
from skeletons.connection_mgr import IConnectionManager
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.utils.functions import makeTooltip

def getPrimeTimeStatusVO(status, hasAvailableServers):
    showPrimeTimeAlert = status != PrimeTimeStatus.AVAILABLE
    return CalendarStatusVO(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if showPrimeTimeAlert else None, buttonIcon='', buttonLabel=backport.text(R.strings.bob.alertMessage.button()), buttonVisible=showPrimeTimeAlert and hasAvailableServers, buttonTooltip=None, statusText=text_styles.vehicleStatusCriticalText(_getPrimeTimeStatusText()), popoverAlias=None, bgVisible=True, shadowFilterVisible=showPrimeTimeAlert, tooltip=TOOLTIPS_CONSTANTS.BOB_SELECTOR_INFO)


@dependency.replace_none_kwargs(bobCtrl=IBobController, connectionMgr=IConnectionManager)
def _getPrimeTimeStatusText(bobCtrl=None, connectionMgr=None):
    hasAvailableServers = bobCtrl.hasAvailablePrimeTimeServers()
    _, timeLeft, _ = bobCtrl.getPrimeTimeStatus()
    alertStr = ''
    if hasAvailableServers:
        alertStr = backport.text(R.strings.bob.alertMessage.somePeripheriesHalt(), serverName=connectionMgr.serverUserNameShort)
    else:
        currSeason = bobCtrl.getCurrentSeason()
        currTime = time_utils.getCurrentLocalServerTimestamp()
        isCycleNow = currSeason and currSeason.hasActiveCycle(currTime) and timeLeft
        if isCycleNow:
            if connectionMgr.isStandalone():
                key = R.strings.bob.alertMessage.singleModeHalt()
            else:
                key = R.strings.bob.alertMessage.allPeripheriesHalt()
            timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.bob.status.timeLeft)
            alertStr = backport.text(key, time=timeLeftStr)
        else:
            alertStr = backport.text(R.strings.bob.systemMessage.notAvailable())
    return alertStr


@dependency.replace_none_kwargs(bobCtrl=IBobController)
def getBobFightBtnTooltipData(result, bobCtrl=None):
    state = result.restriction
    hasAvailableServers = bobCtrl.hasAvailablePrimeTimeServers()
    if state == PRE_QUEUE_RESTRICTION.MODE_DISABLED:
        header = backport.text(R.strings.bob.headerButtons.fightBtn.tooltip.disabled.header())
        if hasAvailableServers:
            body = backport.text(R.strings.bob.headerButtons.fightBtn.tooltip.currentServerUnavailable.body())
        else:
            body = backport.text(R.strings.bob.headerButtons.fightBtn.tooltip.disabled.body())
    elif state == PRE_QUEUE_RESTRICTION.LIMIT_LEVEL:
        header = backport.text(R.strings.bob.headerButtons.fightBtn.tooltip.vehLevelRequired.header())
        body = backport.text(R.strings.bob.headerButtons.fightBtn.tooltip.vehLevelRequired.body(), level=toRomanRangeString(result.ctx['levels'], 1))
    else:
        return ''
    return makeTooltip(header, body)
