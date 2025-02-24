# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/header/helpers/fight_btn_tooltips.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getRandomTooltipData
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, PREBATTLE_RESTRICTION
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.shared.utils.functions import makeTooltip
from helpers import i18n, int2roman
_STR_PATH = R.strings.menu.headerButtons.fightBtn.tooltip

def getComp7BattlesOnlyVehicleTooltipData(result):
    state = result.restriction
    if state in (PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED,
     UNIT_RESTRICTION.VEHICLE_WRONG_MODE,
     PREBATTLE_RESTRICTION.VEHICLE_RENTALS_IS_OVER,
     PREBATTLE_RESTRICTION.VEHICLE_TELECOM_RENTALS_IS_OVER,
     PREBATTLE_RESTRICTION.VEHICLE_WOT_PLUS_EXCLUSIVE_UNAVAILABLE):
        header = backport.text(R.strings.menu.headerButtons.fightBtn.tooltip.comp7BattleOnly.header())
        body = backport.text(R.strings.menu.headerButtons.fightBtn.tooltip.comp7BattleOnly.body())
        return makeTooltip(header, body)


def getComp7FightBtnTooltipData(result, isInSquad):
    state = result.restriction
    resShortCut = R.strings.menu.headerButtons.fightBtn.tooltip
    if state == PRE_QUEUE_RESTRICTION.MODE_OFFLINE:
        header = backport.text(resShortCut.comp7Offline.header())
        body = backport.text(resShortCut.comp7Offline.body())
    elif state == PRE_QUEUE_RESTRICTION.MODE_NOT_SET:
        header = backport.text(resShortCut.comp7NotSet.header())
        body = backport.text(resShortCut.comp7NotSet.body())
    elif state == PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE:
        header = backport.text(resShortCut.comp7Disabled.header())
        body = backport.text(resShortCut.comp7Disabled.body())
    elif state == PRE_QUEUE_RESTRICTION.BAN_IS_SET:
        header = backport.text(resShortCut.comp7BanIsSet.header())
        body = backport.text(resShortCut.comp7BanIsSet.body())
    elif state == PRE_QUEUE_RESTRICTION.QUALIFICATION_RESULTS_PROCESSING:
        header = backport.text(resShortCut.comp7RatingCalculation.header())
        body = backport.text(resShortCut.comp7RatingCalculation.body())
    elif state == PRE_QUEUE_RESTRICTION.LIMIT_NO_SUITABLE_VEHICLES:
        romanLevels = list(map(int2roman, result.ctx['levels']))
        delimiter = backport.text(resShortCut.comp7VehLevel.delimiter())
        vehicleLevelsStr = delimiter.join(romanLevels)
        header = backport.text(resShortCut.comp7VehLevel.header())
        body = backport.text(resShortCut.comp7VehLevel.body(), levels=vehicleLevelsStr)
    elif state == PRE_QUEUE_RESTRICTION.SHOP_PAGE_OPENED:
        header = None
        body = i18n.makeString(TOOLTIPS.HANGAR_STARTBTN_PREVIEW_BODY)
    elif state == PRE_QUEUE_RESTRICTION.MODE_IS_IN_PREANNOUNCE:
        header = backport.text(resShortCut.comp7Preannounce.header())
        body = backport.text(resShortCut.comp7Preannounce.body())
    else:
        return getRandomTooltipData(result, isInSquad)
    return makeTooltip(header, body)
