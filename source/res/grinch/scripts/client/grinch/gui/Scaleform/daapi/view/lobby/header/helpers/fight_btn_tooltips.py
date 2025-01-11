# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/lobby/header/helpers/fight_btn_tooltips.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getRandomTooltipData
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import UNIT_RESTRICTION, PRE_QUEUE_RESTRICTION
from gui.shared.utils.functions import makeTooltip

def getGrinchFightBtnTooltipData(result, isInSquad):
    state = result.restriction
    if state == PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE:
        header = backport.text(R.strings.grinch.headerButtons.fightBtn.tooltip.notAvailable.header())
        body = backport.text(R.strings.grinch.headerButtons.fightBtn.tooltip.notAvailable.body())
    elif state == UNIT_RESTRICTION.VEHICLE_NOT_SELECTED:
        header = backport.text(R.strings.tooltips.hangar.startBtn.squadNotReady.header())
        body = backport.text(R.strings.tooltips.hangar.startBtn.squadNotReady.body())
    else:
        return getRandomTooltipData(result, isInSquad)
    return makeTooltip(header, body)
