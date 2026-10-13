# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/lobby/header/helpers/fight_btn_tooltips.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getRandomTooltipData, getSquadFightBtnTooltipData
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, UNIT_RESTRICTION
from gui.shared.utils.functions import makeTooltip

def getHalloweenFightButtonTooltipData(result, isInSquad):
    state = result.restriction
    if state == PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE:
        header = backport.text(R.strings.halloween_tooltips.hangar.startBtn.offline.header())
        body = backport.text(R.strings.halloween_tooltips.hangar.startBtn.offline.body())
        return makeTooltip(header, body)
    if state == PRE_QUEUE_RESTRICTION.VEHICLE_WILL_BE_UNLOCKED:
        header = backport.text(R.strings.halloween_tooltips.hangar.startBtn.lock.header())
        body = backport.text(R.strings.halloween_tooltips.hangar.startBtn.lock.body())
        return makeTooltip(header, body)
    return getHalloweenSquadFightBtnTooltipData(result) if isInSquad else getRandomTooltipData(result, isInSquad)


def getHalloweenSquadFightBtnTooltipData(result):
    state = result.restriction
    if state == UNIT_RESTRICTION.MODE_NOT_AVAILABLE:
        header = backport.text(R.strings.halloween_tooltips.hangar.startBtn.offline.header())
        body = backport.text(R.strings.halloween_tooltips.hangar.startBtn.offline.body())
    elif state == UNIT_RESTRICTION.IS_IN_ARENA:
        header = backport.text(R.strings.halloween_tooltips.hangar.startBtn.squadInBattle.header())
        body = backport.text(R.strings.halloween_tooltips.hangar.startBtn.squadInBattle.body())
    elif state == UNIT_RESTRICTION.VEHICLE_NOT_VALID:
        header = backport.text(R.strings.halloween_tooltips.hangar.startBtn.lock.header())
        body = backport.text(R.strings.halloween_tooltips.hangar.startBtn.lock.body())
    elif state == UNIT_RESTRICTION.UNIT_WRONG_DATA:
        header = backport.text(R.strings.halloween_tooltips.hangar.startBtn.squadNotAvailableLevel.header())
        body = backport.text(R.strings.halloween_tooltips.hangar.startBtn.squadNotAvailableLevel.body())
    else:
        return getSquadFightBtnTooltipData(result)
    return makeTooltip(header, body)
