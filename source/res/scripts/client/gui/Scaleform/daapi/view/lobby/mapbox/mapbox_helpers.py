# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/mapbox/mapbox_helpers.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.periodic_battles.models import AlertData
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, UNIT_RESTRICTION
from gui.shared.formatters import text_styles
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, time_utils
from skeletons.gui.game_control import IMapboxController
from skeletons.connection_mgr import IConnectionManager
if typing.TYPE_CHECKING:
    from gui.prb_control.items import ValidationResult

def getPrimeTimeStatusVO():
    mapboxCtrl = dependency.instance(IMapboxController)
    connectionMgr = dependency.instance(IConnectionManager)
    status, _, _ = mapboxCtrl.getPrimeTimeStatus()
    errorStr = backport.text(R.strings.mapbox.serverAlertMessage(), serverName=connectionMgr.serverUserNameShort)
    showPrimeTimeAlert = status != PrimeTimeStatus.AVAILABLE
    return AlertData(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if showPrimeTimeAlert else None, buttonIcon='', buttonLabel=backport.text(R.strings.mapbox.serverAlertMessage.button()), buttonVisible=showPrimeTimeAlert and mapboxCtrl.hasAvailablePrimeTimeServers(), buttonTooltip=None, statusText=text_styles.vehicleStatusCriticalText(errorStr), popoverAlias=None, bgVisible=True, shadowFilterVisible=showPrimeTimeAlert, tooltip=TOOLTIPS_CONSTANTS.MAPBOX_SELECTOR_INFO, isSimpleTooltip=False)


def getMapboxFightBtnTooltipData(result):
    strPath = R.strings.mapbox.headerButtons.fightBtn.tooltip
    strAddPath = R.strings.tooltips.hangar
    restriction = result.restriction
    if restriction == PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE or restriction == UNIT_RESTRICTION.CURFEW:
        header = backport.text(strPath.disabled.header())
        body = backport.text(strPath.disabled.text())
    elif restriction == PRE_QUEUE_RESTRICTION.LIMIT_LEVEL:
        levels = backport.text(strPath.mapboxVehLevel.levelSubStr(), levels=toRomanRangeString(result.ctx['levels']))
        header = backport.text(strPath.mapboxVehLevel.header())
        body = backport.text(strPath.mapboxVehLevel.body(), levelSubStr=levels)
    elif restriction == UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED:
        header = backport.text(strAddPath.startBtn.squadNotReady.header())
        body = backport.text(strAddPath.startBtn.squadNotReady.body())
    elif restriction == UNIT_RESTRICTION.VEHICLE_INVALID_LEVEL:
        header = backport.text(strAddPath.tankCarusel.wrongSquadVehicle.header())
        body = backport.text(strAddPath.tankCarusel.wrongSquadVehicle.body())
    elif restriction == UNIT_RESTRICTION.SPG_IS_FULL or restriction == UNIT_RESTRICTION.SPG_IS_FORBIDDEN:
        header = backport.text(strAddPath.tankCarusel.wrongSquadSPGVehicle.header())
        body = backport.text(strAddPath.tankCarusel.wrongSquadSPGVehicle.body())
    else:
        return ''
    return makeTooltip(header, body)


def getTillTimeString(timeStamp):
    timeLeft = time_utils.getTimeDeltaFromNow(timeStamp)
    modeStrBase = R.strings.menu.headerButtons.battle.types.mapbox.availability
    if timeLeft < time_utils.ONE_HOUR:
        res = backport.text(modeStrBase.lessThanHour())
    else:
        res = backport.backport_time_utils.getTillTimeStringByRClass(timeLeft, modeStrBase)
    return res
