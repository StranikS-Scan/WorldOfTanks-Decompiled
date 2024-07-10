# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/header/helpers/controls_helpers.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import TOOLTIP_TYPES
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import DefaultLobbyHeaderHelper
from gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getRoyaleFightBtnTooltipData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS

class BattleRoyaleLobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()
    _OUT_SQUAD_TOOLTIP_KEY = 'battleRoyaleSquad'

    @classmethod
    def _getCommonFightTooltipData(cls, _, __):
        return (TOOLTIPS_CONSTANTS.BATTLE_ROYALE_PERF_ADVANCED, True)

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getRoyaleFightBtnTooltipData(prbValidation), False)


class BRTournamentLobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()

    @classmethod
    def getFightControlTooltipData(cls, prbValidation, isInSquad, isFightBtnDisabled, isNavigationEnabled):
        return ('', False)

    @classmethod
    def getSquadControlTooltipData(cls, prbValidation, isInSquad):
        return ('', TOOLTIP_TYPES.COMPLEX)
