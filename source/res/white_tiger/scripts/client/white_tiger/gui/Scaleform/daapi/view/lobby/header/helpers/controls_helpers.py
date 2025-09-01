# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/lobby/header/helpers/controls_helpers.py
from __future__ import absolute_import
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import UNIT_RESTRICTION, PREBATTLE_RESTRICTION
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import DefaultLobbyHeaderHelper
from gui.shared.utils.functions import makeTooltip
if typing.TYPE_CHECKING:
    from gui.prb_control.items import ValidationResult
_RESTRICTION_TO_STRING_SUBCLASS = {UNIT_RESTRICTION.VEHICLE_NOT_VALID: R.strings.tooltips.white_tiger.squad.disable,
 UNIT_RESTRICTION.UNDEFINED: R.strings.tooltips.white_tiger.squad.disable,
 UNIT_RESTRICTION.VEHICLE_IS_IN_BATTLE: R.strings.tooltips.redButton.disabled.vehicle.inBattle,
 UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED: R.strings.tooltips.hangar.startBtn.squadNotReady,
 UNIT_RESTRICTION.IS_IN_ARENA: None,
 PREBATTLE_RESTRICTION.VEHICLE_IN_BATTLE: R.strings.tooltips.redButton.disabled.vehicle.inBattle}

class WhiteTigerLobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()

    @classmethod
    def _getOutSquadTooltipData(cls, _):
        squad = R.strings.white_tiger_lobby.platoon.headerButton.tooltips.squad
        return (squad.header(), squad.body(), {})

    @classmethod
    def _getInSquadTooltipData(cls, _):
        defaultSquadTooltip = R.strings.platoon.headerButton.tooltips.dyn(cls._IN_SQUAD_TOOLTIP_KEY)
        wtSquadTooltip = R.strings.white_tiger_lobby.platoon.headerButton.tooltips.squad
        return (wtSquadTooltip.header(), defaultSquadTooltip.body(), {})

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        state = prbValidation.restriction
        ctx = prbValidation.ctx
        rSubClass = R.strings.tooltips.hangar.startBtn.primeNotAvailable
        if state == PREBATTLE_RESTRICTION.VEHICLE_NOT_READY and 'noTickets' in ctx and ctx['noTickets']:
            rSubClass = R.strings.tooltips.hangar.startBtn.noTicket
        elif state in _RESTRICTION_TO_STRING_SUBCLASS:
            rSubClass = _RESTRICTION_TO_STRING_SUBCLASS[state]
        return (makeTooltip(None, None), False) if not rSubClass else (makeTooltip(backport.text(rSubClass.header()), backport.text(rSubClass.body())), False)
