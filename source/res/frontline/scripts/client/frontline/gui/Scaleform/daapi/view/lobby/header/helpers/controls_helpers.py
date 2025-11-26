# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/lobby/header/helpers/controls_helpers.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import DefaultLobbyHeaderHelper
from gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getCommonFightBtnTooltipData, getRandomTooltipData
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.utils.functions import makeTooltip

class FrontlineLobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getFightBtnTooltipData(prbValidation), False)


def getFightBtnTooltipData(result):
    state = result.restriction
    if state == PRE_QUEUE_RESTRICTION.LIMIT_LEVEL:
        header = backport.text(R.strings.menu.headerButtons.fightBtn.tooltip.epicBattleVehLevel.header())
        body = backport.text(R.strings.menu.headerButtons.fightBtn.tooltip.epicBattleVehLevel.body(), requirements=backport.text(R.strings.menu.headerButtons.fightBtn.tooltip.epicBattleVehLevel.requirements(), level=toRomanRangeString(result.ctx['levels'])))
        return makeTooltip(header, body)
    if state == PRE_QUEUE_RESTRICTION.VEHICLE_WILL_BE_UNLOCKED:
        rStringShort = R.strings.menu.headerButtons.fightBtn.tooltip.epicBattleSituationalVehicle
        header = backport.text(rStringShort.header())
        body = backport.text(R.strings.menu.headerButtons.fightBtn.tooltip.epicBattleSituationalVehicle.body(), forStartBattle=backport.text(rStringShort.levels.forStartBattle(), levels=toRomanRangeString(result.ctx['vehicleLevelsForStartBattle'])), willBeUnlocked=backport.text(rStringShort.levels.willBeUnlocked(), levels=toRomanRangeString(result.ctx['unlockableInBattleVehLevels'])))
        return makeTooltip(header, body)
    return getCommonFightBtnTooltipData(result) or getRandomTooltipData(result, isInSquad=True)
