# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/header/helpers/fight_btn_tooltips.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getRandomTooltipData
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, PREBATTLE_RESTRICTION
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.shared.utils.functions import makeTooltip
from helpers import int2roman

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
    restriction = result.restriction
    resShortCut = R.strings.menu.headerButtons.fightBtn.tooltip
    if restriction == PRE_QUEUE_RESTRICTION.BAN_IS_SET:
        header = backport.text(resShortCut.comp7BanIsSet.header())
        body = backport.text(resShortCut.comp7BanIsSet.body())
    elif restriction == PRE_QUEUE_RESTRICTION.LIMIT_NO_SUITABLE_VEHICLES:
        romanLevels = list(map(int2roman, result.ctx['levels']))
        delimiter = backport.text(resShortCut.comp7VehLevel.delimiter())
        vehicleLevelsStr = delimiter.join(romanLevels)
        header = backport.text(resShortCut.comp7VehLevel.header())
        body = backport.text(resShortCut.comp7VehLevel.body(), levels=vehicleLevelsStr)
    elif restriction == PRE_QUEUE_RESTRICTION.LIMIT_NOT_ENOUGH_SUITABLE_VEHICLES:
        minVehiclesRequired = result.ctx['amount']
        comp7NotEnoughSuitableVehicles = resShortCut.comp7NotEnoughSuitableVehicles
        header = backport.text(comp7NotEnoughSuitableVehicles.header())
        body = backport.text(comp7NotEnoughSuitableVehicles.body(), minVehiclesRequired=minVehiclesRequired)
    elif restriction == PRE_QUEUE_RESTRICTION.MODE_IS_IN_PREANNOUNCE:
        header = backport.text(resShortCut.comp7Preannounce.header())
        body = backport.text(resShortCut.comp7Preannounce.body())
    elif restriction == PRE_QUEUE_RESTRICTION.MODE_SEASON_ENDED:
        season = result.ctx['season']
        header = backport.text(resShortCut.comp7SeasonEnd.header())
        body = backport.text(R.strings.mode_selector.mode.comp7.seasonEnd.dyn(season)())
    elif restriction == PRE_QUEUE_RESTRICTION.QUALIFICATION_RESULTS_PROCESSING:
        header = backport.text(resShortCut.comp7QualificationCalculation.header())
        body = backport.text(resShortCut.comp7QualificationCalculation.body())
    elif restriction == PRE_QUEUE_RESTRICTION.MODE_NOT_SET:
        header = backport.text(resShortCut.comp7NotSet.header())
        body = backport.text(resShortCut.comp7NotSet.body())
    elif restriction == PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE:
        header = backport.text(resShortCut.comp7Disabled.header())
        body = backport.text(resShortCut.comp7Disabled.body())
    elif restriction == PRE_QUEUE_RESTRICTION.MODE_OFFLINE:
        header = backport.text(resShortCut.comp7Offline.header())
        body = backport.text(resShortCut.comp7Offline.body())
    elif restriction in (PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_TYPE, PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_CLASS, PRE_QUEUE_RESTRICTION.LIMIT_LEVEL):
        header = backport.text(resShortCut.comp7UnsuitableVehicle.header())
        body = None
    elif restriction == UNIT_RESTRICTION.VEHICLE_WRONG_MODE:
        header = backport.text(R.strings.tooltips.redButton.disabled.vehicle.not_supported.header())
        body = backport.text(R.strings.tooltips.redButton.disabled.vehicle.not_supported.body())
    else:
        return getRandomTooltipData(result, isInSquad)
    return makeTooltip(header, body)
