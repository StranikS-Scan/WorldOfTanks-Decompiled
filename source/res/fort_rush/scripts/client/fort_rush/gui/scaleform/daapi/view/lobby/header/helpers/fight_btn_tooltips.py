# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/lobby/header/helpers/fight_btn_tooltips.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getRandomTooltipData
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.shared.utils.functions import makeTooltip

def getFortRushFightBtnTooltipData(result, isInSquad):
    state = result.restriction
    if state == UNIT_RESTRICTION.VEHICLE_NOT_SELECTED:
        header = backport.text(R.strings.tooltips.hangar.startBtn.squadNotReady.header())
        body = backport.text(R.strings.tooltips.hangar.startBtn.squadNotReady.body())
    else:
        return getRandomTooltipData(result, isInSquad)
    return makeTooltip(header, body)
